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

import script

@script.new_survey
@script.register
def setup (survey, questionnaire_odt, questionnaire_pdf, internetquestions = None) :
	u'''questionnaire_odt questionnaire_pdf [additional_questions]
	
	Setup creates a new survey. It parses the questionnaire to create the data
	model. The survey must not exist yet.
	
	questionnaire_odt: the questionnaire in odt-format
	questionnaire_pdf: the questionnaire in pdf-format
	internetquestions: the questions in the internet (optional)
	
	'''	
	import setup
	setup.setup(survey, questionnaire_odt, questionnaire_pdf, internetquestions)

