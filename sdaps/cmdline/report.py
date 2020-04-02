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

from sdaps import model
from sdaps import script
from sdaps.cmdline import report_subparser

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

parser = report_subparser.add_parser("reportlab",
    help=_("Create a PDF report using reportlab."),
    description=_("""This command creates a PDF report using reportlab that
    contains statistics and if selected the freeform fields."""))
script.add_project_argument(parser)

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
parser.add_argument('--suppress-images',
    help=_('Do not include original images in the report. This is useful if there are privacy concerns.'),
    dest='suppress',
    action='store_const',
    const='images')
parser.add_argument('--suppress-substitutions',
    help=_('Do not use substitutions instead of images.'),
    dest='suppress',
    action='store_const',
    const='substitutions',
    default=None)
parser.add_argument('-p', '--paper',
    help=_('The paper size used for the output (default: locale dependent)'),
    dest='papersize')
parser.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: report_%%i.pdf)"))

@script.connect(parser)
@script.logfile
def report(cmdline):
    from sdaps import report

    survey = model.survey.Survey.load(cmdline['project'])

    if cmdline['format'] == 'short':
        small = 1
    else:
        small = 0

    if cmdline['all_filters']:
        return report.stats(survey, cmdline['filter'], cmdline['output'], cmdline['papersize'], small, cmdline['suppress'])
    else:
        return report.report(survey, cmdline['filter'], cmdline['output'], cmdline['papersize'], small, cmdline['suppress'])


