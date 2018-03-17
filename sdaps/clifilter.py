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

"""
This modules contains a helper function to allow writing filter expressions
on the command line of sdaps. Using this it is for example possible to create
a report that only contains a subset of all filled out sheets.
"""


class Locals(object):

    def __init__(self, survey):
        self.survey = survey
        self.qobjects = dict([
            (qobject.id_filter(), qobject)
            for qobject in self.survey.questionnaire.qobjects
        ])

    def __getitem__(self, key):
        if key in self.qobjects:
            return self.qobjects[key].get_answer()
        elif key in ['survey_id', 'questionnaire_id', 'global_id', 'valid', 'quality', 'recognized', 'verified', 'complete']:
            return getattr(self.survey.sheet, key)
        else:
            raise KeyError


def clifilter(survey, expression):
    if expression is None or expression.strip() == '':
        return lambda: True

    exp = compile(expression, '<string>', 'eval')
    globals = __builtins__
    locals = Locals(survey)
    return lambda: eval(exp, globals, locals)

