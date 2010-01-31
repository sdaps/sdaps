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
This modules contains the functionality to create PDF based reports.
"""

from sdaps import script


class report (script.script) :
	doc = _(u'''report [filter...]
	
	Report generates a basic report which shows for every question (if appropriate)
		- the histogramm
		- the mean
		- the standard derivation
		- all handwritten comments
	
	filter: filter expression to select the sheets to appear in the report

	creates report_[index].pdf
	''')

	@classmethod
	def run (klass, survey, *filter) :
		import report
		report.report(survey, filter)


class stats (script.script) :
	doc = _(u'''stats [filter...]
	
	Stats generates a report for every filter condition (not compounded)
	
	filter: filter expression to select the sheets to appear in the reference report

	creates report_[index].pdf (the reference report)
	creates report_[index]_[index] description.pdf
	''')

	@classmethod
	def run (klass, survey, *filter) :
		import report
		report.report(survey, filter, stats = 1)


class smallreport (script.script) :
	doc = _(u'''smallreport [filter...]
	
	Smallreport generates a basic report which shows for every question (if appropriate)
		- the histogramm
		- the mean
		- the standard derivation
	It does not contain any handwritten comment
	
	filter: filter expression to select the sheets to appear in the report

	creates report_[index].pdf
	''')

	@classmethod
	def run (klass, survey, *filter) :
		import report
		report.report(survey, filter, small = 1)
