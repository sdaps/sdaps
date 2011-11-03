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
import optparse

from ugettext import ugettext, ungettext
_ = ugettext

usage=_("""[options] files

	Add scanned questionnaires to the survey.

	file: TIFF-Images containing scanned questionnaires.""")

# Stupid bugger always adds a "Usage:" string that we do not want.
parser = optparse.OptionParser(usage=optparse.SUPPRESS_USAGE)

parser.set_defaults(print_survey_id=True)
parser.set_defaults(print_questionnaire_id=True)

parser.add_option('--copy', action="store_const",
                  help=_('Copy the TIFF into the project directory (default).'),
                  dest='copy', const=True, default=True)
parser.add_option('--no-copy', action="store_const",
                  help=_('Do not copy the TIFF. Instead reference it with a relative path.'),
                  dest='copy', const=False, default=True)

@script.register
@script.logfile
@script.doc(usage + '\n\n\t' + '\n\t'.join(parser.format_help().split('\n')))
def add (survey_dir, *args):
	import image
	import subprocess
	import sys
	import shutil

	survey = model.survey.Survey.load(survey_dir)

	(options, files) = parser.parse_args(list(args))

	for file in files :

		print _('Processing %s') % file

		if not image.check_tiff_monochrome(file):
			print _('Invalid input file %s. You need to specify a (multipage) monochrome TIFF as input.' % file);
			raise AssertionError()

		if options.copy:
			tiff = survey.new_path('%i.tif')
			shutil.copyfile(file, tiff)
		else:
			tiff = file

		num_pages = image.get_tiff_page_count(tiff)

		c = survey.questionnaire.page_count
		assert num_pages % c == 0

		if options.copy:
			tiff = os.path.basename(tiff)
		else:
			tiff = os.path.relpath(os.path.abspath(tiff), survey.survey_dir)

		for i in range(num_pages / c) :
			sheet = model.sheet.Sheet()
			survey.add_sheet(sheet)
			for j in range(c) :
				img = model.sheet.Image()
				sheet.add_image(img)
				img.filename = tiff
				img.tiff_page = c*i+j

		print _('Done')

	survey.save()

