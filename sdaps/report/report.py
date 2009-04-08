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

import os

from reportlab import platypus

from sdaps import model

from sdaps import clifilter
from sdaps import template
from sdaps import matrix

import buddies


def report (survey, filter, filename = None, stats = 0, small = 0) :
	assert isinstance(survey, model.survey.Survey)
	
	# compile clifilter
	filter = clifilter.clifilter(survey, *filter)
	
	# initialise buddies
	survey.questionnaire.report.init(small)
	
	# iterate over sheets
	survey.iterate(
		survey.questionnaire.report.report,
		lambda : survey.sheet.valid and filter()
	)
	
	# do calculations
	survey.questionnaire.report.calculate()	
	
	# create story
	story = template.story_title(
		survey,
		{
			_(u'Turned in Questionnaires'): survey.questionnaire.report.count,
		}
	)
	story.extend(survey.questionnaire.report.story())
	
	# create report
	if filename is None : filename = survey.new_path('report_%i.pdf')
	subject = []
	for key, value in survey.info.iteritems():
		subject.append(u'%(key)s: %(value)s' % {'key': key, 'value': value})
	subject = u'\n'.join(subject)

	doc = template.DocTemplate(
		filename,
		_(u'sdaps report'),
		{
			'title' : survey.title,
			'subject' : subject,
		}
	)
	doc.build(story)

	if stats :
		# save reference
		survey.questionnaire.report.reference()
		
		# do a report for every filter
		for i, filter in enumerate(survey.questionnaire.report.filters()) :
			report (survey, [filter], filename = '%s_%i %s.pdf' % (filename.split('.')[0], i, filter))
	
