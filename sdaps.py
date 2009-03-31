#! /usr/bin/env python
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
u'''

	sdaps - Scripts for data acquisition with paper based surveys


sdaps.py survey script [arguments...]


scripts
*******
'''

import sys

import script
import model
import log

import add
import boxgallery
import cover
import csvdata
import gui
import ids
import info
import recognize
import report
import setup
import stamp


def sdaps (survey_dir, script_name, *arguments) :
	print '-' * 80
	print
	print 'sdaps', script_name
	print
	print '-' * 80
	if script.scripts[script_name].new_survey :
		survey = model.survey.Survey.new(survey_dir)
	else :
		survey = model.survey.Survey.load(survey_dir)
		log.logfile.open(survey.path('log'))
	script.scripts[script_name](survey, *arguments)
	log.logfile.close()


def doc () :
	print __doc__
	for name, function in script.scripts.items() :
		print name, function.__doc__


def main () :
	if len(sys.argv) < 3 :
		doc()
	else :
		sdaps(*sys.argv[1:])


if __name__ == '__main__' :
	main()
	
