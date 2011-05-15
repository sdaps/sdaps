# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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

usage=_("""[options] questionnaire_odt questionnaire_pdf [additional_questions]

	Setup creates a new survey. It parses the questionnaire to create the data
	model. The survey must not exist yet.

	questionnaire_odt: the questionnaire in odt-format
	questionnaire_pdf: the questionnaire in pdf-format
	internetquestions: the questions in the internet (optional)""")

# Stupid bugger always adds a "Usage:" string that we do not want.
parser = optparse.OptionParser(usage=optparse.SUPPRESS_USAGE)

parser.set_defaults(print_survey_id=True)
parser.set_defaults(print_questionnaire_id=True)

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

@script.register
@script.doc(usage + '\n\n\t' + '\n\t'.join(parser.format_help().split('\n')))
def setup (survey_dir, *args) :
	survey = model.survey.Survey.new(survey_dir)

	(options, arguments) = parser.parse_args(list(args))

	if not len(arguments) in [2, 3]:
		# Print our documentation string
		print setup.func_doc
		return 1

	import setup
	setup.setup(survey, options, *arguments)

