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

import model
import script

from ugettext import ugettext, ungettext
_ = ugettext


@script.register
@script.logfile
@script.doc(_(u'''files

	Add scanned questionnaires to the survey.

	files: TIFF-Images containing scanned questionnaires.
	'''))
def add (survey_dir, *files):
	import image
	import subprocess
	import sys
	import shutil

	survey = model.survey.Survey.load(survey_dir)

	for file in files :

		print _('Processing %s') % file

		if not image.check_tiff_monochrome(file):
			print _('Invalid input file %s. You need to specify a (multipage) monochrome TIFF as input.' % file);

		tiff = survey.new_path('%i.tif')
		shutil.copyfile(file, tiff)

		num_pages = image.get_tiff_page_count(tiff)

		c = survey.questionnaire.page_count
		assert num_pages % c == 0

		tiff = os.path.basename(tiff)

		for i in range(num_pages / c) :
			sheet = model.sheet.Sheet()
			survey.add_sheet(sheet)
			for j in range(c) :
				image = model.sheet.Image()
				sheet.add_image(image)
				image.filename = tiff
				image.page = c*i+j

		print _('Done')

	survey.save()

