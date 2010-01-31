# -*- coding: utf-8 -*-
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

u"""This modules contains a helper function to allow writing filter expressions
on the command line of sdaps. Using this it is for example possible to create
a report that only contains a subset of all filled out sheets."""

class Locals (object) :
	
	def __init__ (self, survey) :
		self.survey = survey
		self.qobjects = dict([
			(u'_%i_%i' % qobject.id, qobject)
			for qobject in self.survey.questionnaire.qobjects
		])
	
	def __getitem__ (self, key) :
		if key in self.qobjects :
			return self.qobjects[key].get_answer()
		elif key == 'valid' :
			return self.survey.sheet.valid
		else :
			raise KeyError


def clifilter (survey, *expression) :
	expression = u' '.join([x.decode('utf-8') for x in expression]).strip()
	
	if not expression :
		return lambda : True

	exp = compile(expression, '<string>', 'eval')
	globals = __builtins__
	locals = Locals(survey)
	return lambda : eval(exp, globals, locals)

