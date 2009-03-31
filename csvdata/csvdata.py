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

import csv

import clifilter

import model
import buddies


def csvdata_export (survey, *filter) :
	# compile clifilter
	filter = clifilter.clifilter(survey, *filter)

	# export
	survey.questionnaire.csvdata.export_header()
	
	survey.iterate(
		survey.questionnaire.csvdata.export_data, 
		filter,
	)
	
	survey.questionnaire.csvdata.export_finish()
	

def csvdata_import (survey, filename) :
	csvfile = file(filename, 'r')
	csvreader = csv.DictReader(csvfile)
	
	for data in csvreader :
		survey.questionnaire.csvdata.import_data(data)

	csvfile.close()
	
	survey.save()


