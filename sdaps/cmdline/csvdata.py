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

import os
import sys

from sdaps import model
from sdaps import script

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("csv",
    help=_("Import or export data to/from CSV files."),
    description=_("""Import or export data to/from a CSV file. The first line
    is a header which defines questionnaire_id and global_id, and a column
    for each checkbox and textfield. Note that the import is currently very
    limited, as you need to specifiy the questionnaire ID to select the sheet
    which should be updated."""))

subparser = parser.add_subparsers()

export = subparser.add_parser('export',
    help=_("Export data to CSV file."))
export.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: data_%%i.csv)"))
export.add_argument('-d', '--delimiter',
    help=_("The delimiter used in the CSV file (default ',')"),
    default=',',
    action='store')
export.add_argument('-f', '--filter',
    help=_("Filter to only export a partial dataset."))
export.add_argument('--images',
    help=_("Export images of freeform fields."),
    dest='export_images',
    action='store_const',
    const=True,
    default=False)
export.set_defaults(direction='export')

import_ = subparser.add_parser('import',
    help=_("Import data to from a CSV file."))
import_.add_argument('file',
    help=_("The file to import."))
import_.set_defaults(direction='import')

@script.connect(parser)
@script.logfile
def csvdata(cmdline):
    from sdaps import csvdata

    survey = model.survey.Survey.load(cmdline['project'])

    if cmdline['direction'] == 'export':
        if cmdline['output']:
            if cmdline['output'] == '-':
                outfd = os.dup(sys.stdout.fileno())
                outfile = os.fdopen(outfd, 'w')
            else:
                filename = cmdline['output']
                outfile = file(filename, 'w')
        else:
            filename = survey.new_path('data_%i.csv')
            outfile = file(filename, 'w')

        csvoptions = { 'delimiter' : cmdline['delimiter'] }

        return csvdata.csvdata_export(survey, outfile, cmdline['filter'], cmdline['export_images'], csvoptions)
    elif cmdline['direction'] == 'import':
        return csvdata.csvdata_import(survey, file(cmdline['file'], 'r'))
    else:
        raise AssertionError


