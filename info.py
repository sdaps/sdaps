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

@script.register
def info (survey, field, content = None) :
	u'''field [content]
	
	Alter metadata.
	
	field: name of the field you whish to alter
	content: the new content for that field
		(empty if you want to delete the field)
	
	'''	
	import model
	
	assert isinstance(survey, model.survey.Survey)	
	field = field.decode('utf-8').strip()
	content = content.decode('utf-8').strip()
	
	if content :
		survey.info[field] = content
	else :
		del survey.info[field]
	
	survey.save()
	
