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
from sdaps import script
import optparse

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("setup",
    help=_("Create a new survey using an ODT document."),
    description=_("""Create a new surevey from an ODT document. The PDF export
    of the file needs to be specified at the same time. SDAPS will import
    metadata (properties) and the title from the ODT document."""))

parser.add_argument('questionnaire.odt',
    help=_("The ODT Document"))
parser.add_argument('questionnaire.pdf',
    help=_("PDF export of the ODT document"))
parser.add_argument('additional_questions',
    nargs='?',
    help=_("Additional questions that are not part of the questionnaire."))

parser.set_defaults(print_survey_id=True)
parser.set_defaults(print_questionnaire_id=False)
parser.set_defaults(global_id="")
parser.set_defaults(duplex=True)

parser.add_argument('--print-survey-id',
    action="store_const",
    help=_('Enable printing of the survey ID (default).'),
    dest='print_survey_id', const=True)
parser.add_argument('--no-print-survey-id',
    action="store_const",
    help=_('Disable printing of the survey ID.'),
    dest='print_survey_id', const=False)

parser.add_argument('--print-questionnaire-id',
    action="store_true",
    help=_('Enable printing of the questionnaire ID.'),
    dest='print_questionnaire_id')
parser.add_argument('--no-print-questionnaire-id',
    action="store_false",
    help=_('Disable printing of the questionnaire ID (default).'),
    dest='print_questionnaire_id')

parser.add_argument('--global-id',
    help=_('Set an additional global ID for tracking. This can can only be used in the "code128" style.'),
    dest='global_id')

parser.add_argument('--style',
    choices=["code128", "classic", "custom"],
    help=_('The stamping style to use. Should be either "classic" or "code128". Use "code128" for more features.'),
    dest='style',
    default="code128")

parser.add_argument('--duplex',
    action="store_true",
    help=_('Use duplex mode (ie. only print the IDs on the back side). Requires a mulitple of two pages.'),
    dest='duplex')

parser.add_argument('--simplex',
    action="store_false",
    help=_('Use simplex mode. IDs are printed on each page. You need a simplex scan currently!'),
    dest='duplex')

@script.connect(parser)
def setup(cmdline):
    from sdaps import setupodt

    survey = model.survey.Survey.new(cmdline['project'])

    # Cleanup of options.
    if cmdline['global_id'] == '':
        cmdline['global_id'] = None

    return setupodt.setup(survey, cmdline['questionnaire.odt'], cmdline['questionnaire.pdf'], cmdline['additional_questions'], cmdline)


