# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, 2011, Benjamin Berg <benjamin@sipsolutions.net>
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

parser = report_subparser.add_parser("tex",
    help=_("Create a PDF report using LaTeX."),
    description=_("""This command creates a PDF report using LaTeX that
    contains statistics and freeform fields."""))
script.add_project_argument(parser)

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
parser.add_argument('--create-tex',
    help=_('Save the generated TeX files instead of the final PDF.'),
    dest='create-tex',
    action='store_true',
    default=False)
parser.add_argument('-p', '--paper',
    help=_('The paper size used for the output (default: locale dependent)'),
    dest='papersize')
parser.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: report_%%i.pdf)"))

parser.add_argument('-f', '--filter',
    help=_("Filter to only export a partial dataset."))

@script.connect(parser)
@script.logfile
def report_tex(cmdline):
    from sdaps import reporttex

    survey = model.survey.Survey.load(cmdline['project'])

    return reporttex.report(survey, cmdline['filter'], cmdline['output'], cmdline['papersize'], suppress=cmdline['suppress'], tex_only=cmdline['create-tex'])


