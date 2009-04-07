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

from sdaps import script


class stamp (script.script) :
	doc = _(u'''stamp [count [used_ids]]
	
	Stamp corner marks and questionnaire ids on the questionnaire.
	
	count: number of unique questionnaire ids you want to create
	used_ids: don't use any id named in this file (pattern = '%i\\n')
	
	creates stamped_[index].pdf
	''')

	@classmethod
	def run (klass, survey, count = 0, used_ids = None) :
		if count != 0 :
			count = count.decode('utf-8')
		count = int(count)
		if used_ids is not None:
			used_ids = used_ids.decode('utf-8')

		import stamp

		stamp.stamp(survey, count, used_ids)

