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
This modules contains the functionality to create PDF based reports.
"""

from sdaps import model
from sdaps import script

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

parser = script.subparsers.add_parser("report",
    help=_("Create a PDF report."))

parser.add_argument('-f', '--filter',
    help=_("Filter to only export a partial dataset."))
parser.add_argument('--all-filters',
    help=_("Create a filtered report for every checkbox."),
    action="store_true")
parser.add_argument('-s', '--short',
    help=_("Short format (without freeform text fields)."),
    action="store_const",
    const="short",
    dest="format")
parser.add_argument('-l', '--long',
    help=_("Detailed output. (default)"),
    dest="format",
    action="store_const",
    const="long",
    default="long")
parser.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: report_%%i.pdf)"))

@script.logfile
def report(cmdline):
    survey = model.survey.Survey.load(cmdline['project'])
    import report

    if cmdline['format'] == 'short':
        small = 1
    else:
        small = 0

    if cmdline['all_filters']:
        report.stats(survey, cmdline['filter'], cmdline['output'], small)
    else:
        report.report(survey, cmdline['filter'], cmdline['output'], small)

parser.set_defaults(func=report)

