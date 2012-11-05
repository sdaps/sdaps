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
Contains the functionality to create a new SDAPS project using an OpenOffice.org
document and its PDF Export.
"""

from sdaps import model
from sdaps import script
import optparse

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

usage = _("""[options] questionnaire_odt questionnaire_pdf [additional_questions]

    Setup creates a new survey. It parses the questionnaire to create the data
    model. The survey must not exist yet.

    questionnaire_odt: the questionnaire in odt-format
    questionnaire_pdf: the questionnaire in pdf-format
    internetquestions: the questions in the internet(optional)""")

# Stupid bugger always adds a "Usage:" string that we do not want.
parser = optparse.OptionParser(usage=optparse.SUPPRESS_USAGE)

parser.set_defaults(print_survey_id=True)
parser.set_defaults(print_questionnaire_id=False)
parser.set_defaults(style="classic")
parser.set_defaults(global_id="")
parser.set_defaults(duplex=True)

parser.add_option('--print-survey-id', action="store_const",
                  help=_('Enable printing of the survey ID (default).'),
                  dest='print_survey_id', const=True)
parser.add_option('--no-print-survey-id', action="store_const",
                  help=_('Disable printing of the survey ID.'),
                  dest='print_survey_id', const=False)

parser.add_option('--print-questionnaire-id', action="store_const",
                  help=_('Enable printing of the questionnaire ID.'),
                  dest='print_questionnaire_id', const=True)
parser.add_option('--no-print-questionnaire-id', action="store_const",
                  help=_('Disable printing of the questionnaire ID (default).'),
                  dest='print_questionnaire_id', const=False)

parser.add_option('--global-id',
                  help=_('Set an additional global ID for tracking. This can can not be used in the "code128" style.'),
                  dest='global_id')

parser.add_option('--style',
                  help=_('The stamping style to use. Should be either "classic" or "code128". Use "code128" for more features.'),
                  dest='style')

parser.add_option('--duplex', action="store_true",
                  help=_('Use duplex mode (ie. only print the IDs on the back side). Requires a mulitple of two pages.'),
                  dest='duplex')

parser.add_option('--simplex', action="store_false",
                  help=_('Use simplex mode. IDs are printed on each page. You need a simplex scan currently!'),
                  dest='duplex')


@script.register
@script.doc(usage + '\n\n\t' + '\n\t'.join(parser.format_help().split('\n')))
def setup(survey_dir, *args):
    survey = model.survey.Survey.new(survey_dir)

    (options, arguments) = parser.parse_args(list(args))

    if not len(arguments) in [2, 3]:
        # Print our documentation string
        print setup.func_doc
        return 1

    # Cleanup of options.
    if options.global_id == '':
        options.global_id = None

    options.style = options.style.lower()

    if not options.style in model.survey.valid_styles:
        print >>sys.stderr, _("You selected an unsupported style '%s'.\nValid choices are:") % options.style
        for style in model.valid_styles:
            print >>sys.stderr, " * %s" % style
        sys.exit(1)

    import setup
    setup.setup(survey, options, *arguments)

