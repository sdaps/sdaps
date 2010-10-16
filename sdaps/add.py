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
	import Image
	import subprocess
	import sys

	survey = model.survey.Survey.load(survey_dir)

	for file in files :

		print _('Processing %s') % file

		try :
			image = Image.open(file)
		except IOError :
			print _('Unknown file format. Only TIFF is supported')
			print _('Processing stopped')
			continue

		if image.format != 'TIFF' :
			print _('Unknown image file format (%s). Only TIFF is supported') % image.format
			print _('Processing stopped')
			continue

		if not image.mode == '1' :
			print _('Wrong data type inside TIFF (%s). It should be black and white data.') % image.mode
			print _('Processing stopped')
			continue

		directory = survey.new_path('%i')
		os.mkdir(directory)
		try:
			tiffsplit = subprocess.Popen(
				['tiffsplit', file, directory + '/'],
				stdout = subprocess.PIPE, stderr = subprocess.PIPE
			)
		except OSError, e:
			if e.errno == 2:
				raise AssertionError(_('Could not execute tiffsplit!'))
			else:
				raise e
		stdout, stderr = tiffsplit.communicate()

		for line in stdout.split('\n') :
			line = line.strip()
			if line: print line

		for line in stderr.split('\n') :
			if line.startswith('%s: Warning, incorrect count for field "DateTime"' % file) :
				continue
			line = line.strip()
			if line: print line

		img_list = os.listdir(directory)
		img_list.sort()
		c = survey.questionnaire.page_count
		assert len(img_list) % c == 0

		dir = os.path.basename(directory)
		for i in range(len(img_list) / c) :
			sheet = model.sheet.Sheet()
			survey.add_sheet(sheet)
			for j in range(c) :
				image = model.sheet.Image()
				sheet.add_image(image)
				image.filename = os.path.join(dir, img_list[c*i+j])

		print _('Done')

	survey.save()

