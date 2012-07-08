# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2010, Benjamin Berg <benjamin@sipsolutions.net>
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
Contains the functionality to create a new SDAPS project using a LaTeX input
file.
"""

from sdaps import model
from sdaps import script

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


@script.register
@script.doc(_(u'''questionnaire_tex [additional_questions]

    Setup creates a new survey. It compiles the TeX file, and parses the
    output to create the data model.
    The survey must not exist yet.

    questionnaire_tex: the questionnaire in TeX-format
    additional_questions: the questions in the internet(optional)
    '''))
def setup_tex(survey_dir, questionnaire_odt, additional_questions=None):
    survey = model.survey.Survey.new(survey_dir)
    import setup
    setup.setup(survey, questionnaire_odt, additional_questions)

