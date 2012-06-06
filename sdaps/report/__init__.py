# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
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

from sdaps import model
from sdaps import script

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


@script.register
@script.logfile
@script.doc(_(u'''[filter...]

	Report generates a basic report which shows for every question (if appropriate)
		- the histogramm
		- the mean
		- the standard derivation
		- all handwritten comments

	filter: filter expression to select the sheets to appear in the report

	creates report_[index].pdf
	'''))
def report (survey_dir, *filter) :
	survey = model.survey.Survey.load(survey_dir)
	import report
	report.report(survey, filter)

@script.register
@script.logfile
@script.doc(_(u'''[filter...]

	Stats generates a report for every filter condition (not compounded)

	filter: filter expression to select the sheets to appear in the reference report

	creates report_[index].pdf (the reference report)
	creates report_[index]_[index] description.pdf
	'''))
def stats (survey_dir, *filter) :
	survey = model.survey.Survey.load(survey_dir)
	import report
	report.stats(survey, filter)

@script.register
@script.logfile
@script.doc(_(u'''[filter...]

	Smallreport generates a basic report which shows for every question (if appropriate)
		- the histogramm
		- the mean
		- the standard derivation
	It does not contain any handwritten comment

	filter: filter expression to select the sheets to appear in the report

	creates report_[index].pdf
	'''))
def smallreport (survey_dir, *filter) :
	survey = model.survey.Survey.load(survey_dir)
	import report
	report.report(survey, filter, small = 1)

