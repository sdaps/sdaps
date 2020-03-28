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

import csv

from sdaps import clifilter
from sdaps import model

from . import buddies


def to_dataframe(survey, filter=None):
    # compile clifilter
    filter = clifilter.clifilter(survey, filter)

    survey.questionnaire.pandas.init()

    survey.iterate(
        survey.questionnaire.pandas.append_row,
        filter,
    )

    return survey.questionnaire.pandas.get_dataframe()


