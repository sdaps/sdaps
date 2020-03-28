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
This module implements a simple export to feather files.
"""

import os
import sys

from sdaps import model
from sdaps import script

from sdaps.cmdline import export_subparser

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


export = export_subparser.add_parser('feather',
    help=_("Export data to feather file."))
export.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: data_%%i.feather)"))
export.add_argument('-f', '--filter',
    help=_("Filter to only export a partial dataset."))
export.set_defaults(direction='export')
script.add_project_argument(export)

@script.connect(export)
@script.logfile
def feather(cmdline):
    import pandas
    import sdaps.pandas

    survey = model.survey.Survey.load(cmdline['project'])

    if cmdline['direction'] == 'export':
        if cmdline['output']:
            filename = cmdline['output']
        else:
            filename = survey.new_path('data_%i.feather')

        df = sdaps.pandas.to_dataframe(survey, filter=cmdline['filter'])

        df.to_feather(filename)
    else:
        raise AssertionError


