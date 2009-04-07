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


class csvdata (script.script) :
	doc = _(u'''csvdata export [filter...]
	
	Export to csv
	
	filter: filter expression to select the sheets to export
	
	creates data_[index].csv


csvdata import filename

	Import from csv

	filename: file to read from
	''')

	@classmethod
	def run (klass, survey, command, *args) :
		import csvdata
		if command == 'export' :
			csvdata.csvdata_export(survey, *args)
		elif command == 'import' :
			csvdata.csvdata_import(survey, *args)
		else :
			print _('Unknown command')
