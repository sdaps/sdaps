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
import shutil

from sdaps import utils
from sdaps import model
from sdaps import log

import buddies
import boxesparser
import qobjectsparser
import additionalparser
import metaparser


def setup (survey, questionnaire_odt, questionnaire_pdf, additionalqobjects = None) :
	if os.access(survey.path(), os.F_OK) :
		print _('The survey directory already exists')
		print _('Cancelling setup')
		return 1

	mimetype = utils.mimetype(questionnaire_odt)
	if mimetype != 'application/vnd.oasis.opendocument.text' and mimetype != '':
		print _('Unknown file type (%s). questionnaire_odt should be application/vnd.oasis.opendocument.text') % mimetype
		print _('Cancelling setup')
		return 1

	mimetype = utils.mimetype(questionnaire_pdf)
	if mimetype != 'application/pdf' and mimetype != '':
		print _('Unknown file type (%s). questionnaire_pdf should be application/pdf') % mimetype
		print _('Cancelling setup')
		return 1

	if additionalqobjects is not None :
		mimetype = utils.mimetype(additionalqobjects)
		if mimetype != 'text/plain' and mimetype != '':
			print _('Unknown file type (%s). additionalqobjects should be text/plain') % mimetype
			print _('Cancelling setup')
			return 1

	# Add the new questionnaire
	survey.add_questionnaire(model.questionnaire.Questionnaire())

	# Parse the box objects into a cache
	boxes, page_count = boxesparser.parse(questionnaire_pdf)
	survey.questionnaire.page_count = page_count

	# Parse qobjects
	qobjectsparser.parse(survey, questionnaire_odt, boxes)

	# Parse additionalqobjects
	if additionalqobjects :
		additionalparser.parse(survey, additionalqobjects)

	# Parse Metadata
	metaparser.parse(survey, questionnaire_odt)

	# Last not least calculate the survey id
	survey.calculate_survey_id()

	# Print the result
	print survey.title

	for item in survey.info.items() :
		print u'%s: %s' % item

	print unicode(survey.questionnaire)

	# Create the survey
	os.mkdir(survey.path())

	log.logfile.open(survey.path('log'))

	shutil.copy(questionnaire_odt, survey.path('questionnaire.odt'))
	shutil.copy(questionnaire_pdf, survey.path('questionnaire.pdf'))

	survey.save()
	log.logfile.close()

