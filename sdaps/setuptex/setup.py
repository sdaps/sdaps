# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2010, Benjamin Berg <benjamin@sipsolutions.net>
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
import glob
import subprocess

from sdaps import utils
from sdaps import model
from sdaps import log
from sdaps import paths

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

from sdaps.setup import buddies
import sdapsfileparser
from sdaps.setup import additionalparser
#import metaparser
from sdaps.setup.pdftools import pdffile


def setup (survey, questionnaire_tex, additionalqobjects = None) :
	if os.access(survey.path(), os.F_OK) :
		print _('The survey directory already exists')
		print _('Cancelling setup')
		return 1

	mimetype = utils.mimetype(questionnaire_tex)
	if mimetype != 'text/x-tex' and mimetype != '':
		print _('Unknown file type (%s). questionnaire_tex should be of type text/x-tex') % mimetype
		print _('Will keep going, but expect failure!')
		print

	if additionalqobjects is not None :
		mimetype = utils.mimetype(additionalqobjects)
		if mimetype != 'text/plain' and mimetype != '':
			print _('Unknown file type (%s). additionalqobjects should be text/plain') % mimetype
			print _('Cancelling setup')
			return 1

	# Add the new questionnaire
	survey.add_questionnaire(model.questionnaire.Questionnaire())

	# Create the survey directory, and copy the tex file.
	os.mkdir(survey.path())
	try:
		shutil.copy(questionnaire_tex, survey.path('questionnaire.tex'))

		# Copy class and dictionary files
		if paths.local_run :
			cls_file = os.path.join(paths.source_dir, 'tex', 'sdaps.cls')
			dict_files = os.path.join(paths.source_dir, 'tex', '*.dict')
			dict_files = glob.glob(dict_files)
		else :
			cls_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'sdaps.cls')
			dict_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.dict')
			dict_files = glob.glob(dict_files)

		shutil.copyfile(cls_file, survey.path('sdaps.cls'))
		for dict_file in dict_files:
			shutil.copyfile(dict_file, survey.path(os.path.basename(dict_file)))


		# Compile the .tex file
		subprocess.call(['rubber', '--into', survey.path(), '-d', survey.path('questionnaire.tex')])
		if not os.path.exists(survey.path('questionnaire.pdf')):
			print _("Error running \"rubber -d\" to compile the LaTeX file.")
			raise

		# Get the papersize
		doc = pdffile.PDFDocument(survey.path('questionnaire.pdf'))
		page = doc.read_page(1)
		survey.defs.paper_width = abs(page.MediaBox[0] - page.MediaBox[2]) / 72.0 * 25.4
		survey.defs.paper_height = abs(page.MediaBox[1] - page.MediaBox[3]) / 72.0 * 25.4
		survey.questionnaire.page_count = doc.count_pages()
		survey.defs.print_questionnaire_id = False
		survey.defs.print_survey_id = True

		# Parse qobjects
		try:
			sdapsfileparser.parse(survey)
		except:
			print _("Error: Caught an Exception while parsing the SDAPS file. The current state is:")
			print unicode(survey.questionnaire)
			print "------------------------------------"

			raise

		# Parse additionalqobjects
		if additionalqobjects :
			additionalparser.parse(survey, additionalqobjects)

		# Last but not least calculate the survey id
		survey.calculate_survey_id()

		# Print the result
		print survey.title

		for item in survey.info.items() :
			print u'%s: %s' % item

		print unicode(survey.questionnaire)

		log.logfile.open(survey.path('log'))

		survey.save()
		log.logfile.close()
	except:
		print _("An error occured in the setup routine, deleting the survey directory again.")
		shutil.rmtree(survey.path())
		raise

