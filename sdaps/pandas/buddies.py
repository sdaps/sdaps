# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, 2017, Benjamin Berg <benjamin@sipsolutions.net>
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

import os
import os.path
import numpy as np
import pandas
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'pandas'
    obj_class = model.questionnaire.Questionnaire

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)
        self.init()

    def init(self):
        self._questionnaire_id = []
        self._global_id = []
        self._empty = []
        self._valid = []
        self._recognized = []
        self._verified = []

        columns = [('questionnaire_id', np.str_, self._questionnaire_id),
                   ('global_id', np.str_, self._global_id),
                   ('empty', np.bool_, self._empty),
                   ('valid', np.bool_, self._valid),
                   ('recognized', np.bool_, self._recognized),
                   ('verified', np.bool_, self._verified)]

        # TODO: Allow image exporting into pandas (like the CSV export does)?

        for qobject in self.obj.qobjects:
            columns.extend(qobject.pandas.init())

        self._columns = columns
        self._data = [[]] * len(columns)

    def append_row(self):
        self._questionnaire_id.append(self.obj.sheet.questionnaire_id)
        self._global_id.append(str(self.obj.sheet.global_id))
        self._empty.append(self.obj.sheet.empty)
        self._valid.append(self.obj.sheet.valid)
        self._recognized.append(self.obj.sheet.recognized)
        self._verified.append(self.obj.sheet.verified)

        for qobject in self.obj.qobjects:
            qobject.pandas.append_row()

    def get_dataframe(self):
        columns = []
        labels = []
        length = len(self._columns[0][2])

        for label, dtype, rows in self._columns:
            assert len(rows) == length

            columns.append(pandas.DataFrame(rows, columns=[label], dtype=dtype))

        return pandas.concat(columns, axis=1)

class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'pandas'
    obj_class = model.questionnaire.QObject

    def init(self):
        columns = []
        for box in self.obj.boxes:
            columns.extend(box.pandas.init())

        return columns

    def append_row(self):
        for box in self.obj.boxes:
            box.pandas.append_row()


class Option(QObject, metaclass=model.buddy.Register):

    name = 'pandas'
    obj_class = model.questionnaire.Option

    def init(self):
        self._data = []
        columns = [(self.obj.id_csv(), np.int_, self._data)]
        columns.extend(QObject.init(self))

        return columns

    def append_row(self):
        self._data.append(self.obj.get_answer())

        QObject.append_row(self)

class Additional_Mark(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'pandas'
    obj_class = model.questionnaire.Additional_Mark

    def init(self):
        self._data = []
        return [(self.obj.id_csv(), np.int_, self._data)]

    def append_row(self):
        self._data.append(self.obj.get_answer())


class Box(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'pandas'
    obj_class = model.questionnaire.Box

    def init(self):
        self._values = []
        self._qualities = []

        return [(self.obj.id_csv(), np.int_, self._values),
                (self.obj.id_csv() + '_quality', np.float_, self._qualities)]

    def append_row(self):
        self._values.append(self.obj.data.state)
        self._qualities.append(self.obj.data.quality)


class Textbox(Box, metaclass=model.buddy.Register):

    name = 'pandas'
    obj_class = model.questionnaire.Textbox

    def init(self):
        self._states = []
        self._texts = []

        return [(self.obj.id_csv(), np.bool_, self._states),
                (self.obj.id_csv() + '_text', np.unicode_, self._texts),]

    def append_row(self):
        self._states.append(self.obj.data.state)
        self._texts.append(self.obj.data.text if self.obj.data.state else None)


