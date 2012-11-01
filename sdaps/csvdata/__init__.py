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

u"""
This module implements a simple export/import to/from CSV files.
"""

from sdaps import model
from sdaps import script

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("csv",
    help=_("Import or export data to/from CSV files."))

subparser = parser.add_subparsers()

export = subparser.add_parser('export',
    help=_("Export data to CSV file."))
export.add_argument('-f', '--filter',
    help=_("Filter to only export a partial dataset."))
export.set_defaults(direction='export')

import_ = subparser.add_parser('import',
    help=_("Import data to from a CSV file."))
import_.add_argument('file',
    help=_("The file to import."))
import_.set_defaults(direction='import')

@script.logfile
def csvdata(cmdline):
    survey = model.survey.Survey.load(cmdline['project'])
    import csvdata
    if cmdline['direction'] == 'export':
        csvdata.csvdata_export(survey, cmdline)
    elif cmdline['direction'] == 'import':
        csvdata.csvdata_import(survey, cmdline)
    else:
        raise AssertionError

parser.set_defaults(func=csvdata)

