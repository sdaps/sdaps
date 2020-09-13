# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# The code uses multiple inheritance; however, most of the additional base
# classes are solely used as mixins. This means they must not contain any
# __init__ functions, as that could cause trouble.


from . import db
from . import buddy
from . import data
import sys
import struct


class DataObject(object):
    '''Mixin
    '''

    def get_data(self):
        if not self.id in self.sheet.data:
            if hasattr(self, '_data_object'):
                clsname = self._data_object
            else:
                clsname = self.__class__.__name__
            self.sheet.data[self.id] = getattr(data, clsname)(self)
        return self.sheet.data[self.id]

    data = property(get_data)


class Questionnaire(buddy.Object):
    '''
    Identification: There is only one.
    Reference: survey.questionnaire
    Parent: self.survey
    '''

    _save_skip = {'survey'}

    def __init__(self):
        self.survey = None
        self.qobjects = list()
        self.last_id = (-1,)
        self.init_attributes()
        self._notify_changed_list = list()

    def init_attributes(self):
        self.page_count = 0

    def add_qobject(self, qobject, new_id=None):
        qobject.questionnaire = self

        if new_id is not None:
            # We allow IDs to move backward, but will continue auto-counting
            # at the last increasing position.
            if new_id > self.last_id:
                self.last_id = new_id
            else:
                # If it moved backward, assert that there is no collision
                for q in self.qobjects:
                    assert q.id != new_id
            qobject.id = new_id
        else:
            self.last_id = qobject.init_id(self.last_id)
        self.qobjects.append(qobject)

    def get_sheet(self):
        return self.survey.sheet

    sheet = property(get_sheet)

    def notify_data_changed(self, qobj, dobj, name, old_value):
        for func in self._notify_changed_list:
            func(self, qobj, dobj, name, old_value)

    def connect_data_changed(self, func):
        self._notify_changed_list.append(func)

    def disconnect_data_changed(self, func):
        self._notify_changed_list.remove(func)

    def __str__(self):
        return str().join(
            ['%s\n' % self.__class__.__name__] +
            [str(qobject) for qobject in self.qobjects]
        )

    def find_object(self, oid):
        for qobject in self.qobjects:
            obj = qobject.find_object(oid)

            if obj is not None:
                return obj

    def reinit_state(self):
        self._notify_changed_list = list()

    def __setstate__(self, data):
        self.__dict__.update(data)

        self._notify_changed_list = list()

        for i in range(len(self.qobjects)):
            self.qobjects[i] = db.fromJson(self.qobjects[i], sys.modules[__name__])
            self.qobjects[i].questionnaire = self

class QObject(buddy.Object, DataObject):
    '''
    Identification: id ==(major, minor)
    Reference: survey.questionnaire.qobjects[i](i != id)
    Parent: self.questionnaire
    '''

    _data_object = 'QObject'
    _save_skip = {'survey', 'questionnaire'}

    def __init__(self):
        self.questionnaire = None
        self.boxes = list()
        self.last_id = -1
        self.max_value = -1
        self.var = None
        self.init_attributes()

    def init_attributes(self):
        pass

    def init_id(self, id):
        self.id = id[:-1] + (id[-1] + 1,)
        return self.id

    def add_box(self, box):
        box.question = self
        self.last_id = box.init_id(self.last_id)
        self.max_value = max(self.max_value, box.init_value(self.max_value))
        self.boxes.append(box)

    def get_sheet(self):
        return self.questionnaire.sheet

    sheet = property(get_sheet)

    def calculate_survey_id(self, md5):
        pass

    def id_str(self):
        ids = [str(x) for x in self.id]
        return '.'.join(ids)

    def id_csv(self):
        if self.var:
            return self.var

        ids = [str(x) for x in self.id]
        return '_'.join(ids)

    def id_filter(self):
        ids = [str(x) for x in self.id]
        return '_' + '_'.join(ids)

    def __str__(self):
        return '(%s)\n' % (
            self.__class__.__name__,
        )

    def find_object(self, oid):
        if self.id == oid:
            return self

        for box in self.boxes:
            obj = box.find_object(oid)

            if obj is not None:
                return obj

        return None

    def __setstate__(self, data):
        # Attributes that may not (yet) be present in the database
        self.var = None

        self.__dict__.update(data)
        self.id = tuple(self.id)

        for i in range(len(self.boxes)):
            self.boxes[i] = db.fromJson(self.boxes[i], sys.modules[__name__])
            self.boxes[i].question = self

class Head(QObject):

    def init_attributes(self):
        QObject.init_attributes(self)
        self.title = str()

    def init_id(self, id):
        self.id = (id[0] + 1, ) + (0,)*(len(id)-1)
        return self.id

    def __str__(self):
        return '%s(%s) %s\n' % (
            self.id_str(),
            self.__class__.__name__,
            self.title,
        )


class Question(QObject):

    def init_attributes(self):
        QObject.init_attributes(self)
        self.page_number = 0
        self.question = str()

    def calculate_survey_id(self, md5):
        for box in self.boxes:
            box.calculate_survey_id(md5)

    def __str__(self):
        return '%s(%s) %s {%i}\n' % (
            self.id_str(),
            self.__class__.__name__,
            self.question,
            self.page_number
        )


class Choice(Question):

    def __str__(self):
        return str().join(
            [Question.__str__(self)] +
            [str(box) for box in self.boxes]
        )

    def get_answer(self):
        '''it's a list containing all selected values
        '''
        answer = list()
        for box in self.boxes:
            if box.data.state:
                answer.append(box.value)
        return answer

class Option(Question):

    def init_attributes(self):
        Question.init_attributes(self)
        self.value_none = "NA"
        self.value_invalid = "error-multi-select"

    def __str__(self):
        return str().join(
            [Question.__str__(self)] +
            [str(box) for box in self.boxes]
        )

    def get_answer(self):
        answer = list()
        for box in self.boxes:
            if box.data.state:
                answer.append(box.value)

        if len(answer) == 1:
            return answer[0]
        else:
            if len(answer) == 0:
                return self.value_none
            else:
                return self.value_invalid

    def set_answer(self, answer):
        # Used for CSV import. Set the first box with the right value, unset
        # all others.
        # Raises an exception if not found

        # Unset all if value is the none value or None
        if answer == self.value_none or answer is None:
            for box in self.boxes:
                box.data.state = 0
            return

        # Set all if value is not an integer or the invalid value
        # NOTE: Assumes more than one box!
        if answer == self.value_invalid or not isinstance(answer, int):
            assert len(self.boxes) > 1
            for box in self.boxes:
                box.data.state = 1
            return

        found = False
        for box in self.boxes:
            if not found and box.value == answer:
                found = True
                box.data.state = 1
            else:
                box.data.state = 0

        assert(found)

class Range(Option):

    def init_attributes(self):
        Option.init_attributes(self)
        self.answers = ("", "")
        self.range = (0, 0)

    def __str__(self):
        if len(self.answers) == 2:
            return str().join(
                [Question.__str__(self)] +
                ['\t%s (%i) - %s (%i)\n' % (self.answers[0], self.range[0], self.answers[1], self.range[1])] +
                [str(box) for box in self.boxes]
            )
        else:
            return str().join(
                [Question.__str__(self)] +
                ['\t? - ?\n'] +
                [str(box) for box in self.boxes]
            )

class Mark(Range):
    # Just an alias for unpickling old data
    pass

class Text(Question):

    def __str__(self):
        return str().join(
            [Question.__str__(self)] +
            [str(box) for box in self.boxes]
        )

    def get_answer(self):
        '''it's a bool, wether there is content in the textbox
        '''
        assert len(self.boxes) == 1
        text = ""
        for box in self.boxes:
            text = text + box.data.text
        if text:
            return text
        else:
            return self.boxes[0].data.state


class Additional_Head(Head):

    pass


class Additional_Mark(Question):

    def init_attributes(self):
        Question.init_attributes(self)
        self.answers = list()

    def __str__(self):
        return str().join(
            [Question.__str__(self)] +
            ['\t%s - %s\n' % tuple(self.answers)]
        )

    def get_answer(self):
        return self.data.value

    def set_answer(self, answer):
        self.data.value = answer


class Additional_FilterHistogram(Question):

    def init_attributes(self):
        Question.init_attributes(self)
        self.answers = list()
        self.filters = list()

    def __str__(self):
        result = []
        result.append(Question.__str__(self))
        for i in range(len(self.answers)):
            result.append('\t%s - %s\n' % (self.answers[i], self.filters[i]))
        return str().join(result)

    def get_answer(self):
        return self.data.value

    def set_answer(self, answer):
        raise NotImplemented()


class Box(buddy.Object, DataObject):
    '''
    Identification: id of the parent and value of the box ::

        id == (major, minor, value)

    Reference: survey.questionnaire.qobjects[i].boxes[j]
    Parent: self.question
    '''

    _save_skip = { 'question' }

    def __init__(self):
        self.question = None
        self.init_attributes()

    def init_attributes(self):
        self.page_number = 0
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.lw = 25.4 / 72.0
        self.text = str()

        self.var = None
        self.value = None

    def init_id(self, id):
        id = id + 1

        self.id = self.question.id + (id,)
        return id

    def init_value(self, value):
        value = value + 1

        if self.value is None:
            self.value = value

        return self.value

    def id_str(self):
        ids = [str(x) for x in self.id]
        return '.'.join(ids)

    def id_csv(self):
        if self.var:
            return self.var

        ids = [str(x) for x in self.id]
        return '_'.join(ids)

    def get_sheet(self):
        return self.question.sheet

    sheet = property(get_sheet)

    def calculate_survey_id(self, md5):
        tmp = struct.pack('!ffff', self.x, self.y, self.width, self.height)
        md5.update(tmp)

    def __str__(self):
        return '\t%i(%s) %s %s %s %s %s\n' % (
            self.value,
            (self.__class__.__name__).ljust(8),
            ('%.1f' % self.x).rjust(5),
            ('%.1f' % self.y).rjust(5),
            ('%.1f' % self.width).rjust(5),
            ('%.1f' % self.height).rjust(5),
            self.text
        )

    def find_object(self, oid):
        if self.id == oid:
            return self

    def __setstate__(self, data):
        self.__dict__.update(data)
        self.id = tuple(self.id)

class Checkbox(Box):

    def init_attributes(self):
        Box.init_attributes(self)
        self.form = "box"

    def calculate_survey_id(self, md5):
        Box.calculate_survey_id(self, md5)
        md5.update(self.form.encode('utf-8'))

class Textbox(Box):

    pass

class Codebox(Textbox):

    _data_object = 'Textbox'

