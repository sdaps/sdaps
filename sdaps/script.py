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

	sdaps - scripts for data acquisition with paper based surveys

	script - Registration center for sdaps scripts


Defining a script
=================

	from sdaps import script

	@script.register
	def my_script (survey, *arguments) :
		u\'''arguments
		description
		\'''
		from sdaps import buddies
		do the work

	if sdaps imports your module, the script will be registerd
	
	if sdaps calls your script, it should import any buddies, so that they will
	be registerd.

'''

scripts = dict()

def register (function) :
	scripts[function.__name__] = function
	function.new_survey = 0
	return function

def new_survey (function) :
	function.new_survey = 1
	return function
	
