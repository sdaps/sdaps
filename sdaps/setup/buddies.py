# -*- coding: utf8 -*-
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

from sdaps import model

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


class QObject(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.QObject
    name = 'setup'

    def init(self):
        pass

    def question(self, chars):
        pass

    def answer(self, chars):
        pass

    def box(self, box):
        pass

    def validate(self):
        pass

    def setup(self, args):
        pass


class Head(QObject):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Head

    def question(self, chars):
        self.obj.title += chars.strip()

    def validate(self):
        if not self.obj.title:
            print _(u'Warning: Head %(l0)i got no title.') % {'l0': self.obj.id[0]}


class Question(QObject):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Question

    def question(self, chars):
        self.obj.question += chars.strip()

    def validate(self):
        if not self.obj.question:
            print _(u'Warning: %(class)s %(l0)i.%(l1)i got no question.') % {
                'class': self.obj.__class__.__name__,
                'l0': self.obj.id[0], 'l1': self.obj.id[1]
            }


class Choice(Question):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Choice

    def init(self):
        self.cache = list()

    def _box(self, box):
        self.obj.add_box(box)
        if self.obj.page_number == 0:
            self.obj.page_number = box.page_number
        else:
            assert self.obj.page_number == box.page_number

    def answer(self, chars):
        if self.cache:
            if isinstance(self.cache[0], unicode):
                self.cache.append(chars)
            else:
                box = self.cache.pop(0)
                box.setup.answer(chars)
                self._box(box)
        else:
            self.cache.append(chars)

    def box(self, box):
        if self.cache:
            if isinstance(self.cache[0], unicode):
                answer = self.cache.pop(0)
                box.setup.answer(answer)
                self._box(box)
            else:
                self.cache.append(box)
        else:
            self.cache.append(box)

    def validate(self):
        Question.validate(self)
        if self.cache:
            raise AssertionError(_("Error in question \"%s\"") % self.obj.question)
        del self.cache
        if not self.obj.boxes:
            print _(u'Warning: %(class)s %(l0)i.%(l1)i got no boxes.') % {
                'class': self.obj.__class__.__name__,
                'l0': self.obj.id[0], 'l1': self.obj.id[1]
            }


class Mark(Question):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Mark

    def answer(self, chars):
        self.obj.answers.append(chars)

    def box(self, box):
        assert isinstance(box, model.questionnaire.Checkbox)
        self.obj.add_box(box)
        if self.obj.page_number == 0:
            self.obj.page_number = box.page_number
        else:
            assert self.obj.page_number == box.page_number

    def validate(self):
        Question.validate(self)
        if not len(self.obj.boxes) == 5:
            print _(u'Warning: %(class)s %(l0)i.%(l1)i got not exactly five boxes.') % {
                'class': self.obj.__class__.__name__,
                'l0': self.obj.id[0], 'l1': self.obj.id[1]
            }
        if not len(self.obj.answers) == 2:
            print _(u'Warning: %(class)s %(l0)i.%(l1)i got not exactly two answers.') % {
                'class': self.obj.__class__.__name__,
                'l0': self.obj.id[0], 'l1': self.obj.id[1]
            }


class Text(Question):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Text

    def box(self, box):
        assert isinstance(box, model.questionnaire.Textbox)
        self.obj.add_box(box)
        if self.obj.page_number == 0:
            self.obj.page_number = box.page_number
        else:
            assert self.obj.page_number == box.page_number

    def validate(self):
        Question.validate(self)
        if not len(self.obj.boxes) == 1:
            print _(u'Warning: %(class)s %(l0)i.%(l1)i got not exactly one box.') % {
                'class': self.obj.__class__.__name__,
                'l0': self.obj.id[0], 'l1': self.obj.id[1]
            }


class Additional_Head(Head):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Additional_Head

    def setup(self, args):
        assert len(args) == 1
        self.question(args[0])
        self.validate()


class Additional_Mark(Question):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Additional_Mark

    def setup(self, args):
        assert len(args) == 3
        self.question(args[0])
        self.obj.answers.append(args[1])
        self.obj.answers.append(args[2])
        self.validate()


class Additional_FilterHistogram(Question):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Additional_FilterHistogram

    def setup(self, args):
        assert len(args) % 2 == 1
        self.question(args.pop(0))
        while len(args):
            self.obj.answers.append(args.pop(0))
            self.obj.filters.append(args.pop(0))
        self.validate()


class Box(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    obj_class = model.questionnaire.Box
    name = 'setup'

    def setup(self, page_number, x, y, width, height):
        self.obj.page_number = page_number
        self.obj.x = x
        self.obj.y = y
        self.obj.width = width
        self.obj.height = height

    def answer(self, text):
        self.obj.text = text

