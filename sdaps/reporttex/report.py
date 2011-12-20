# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008, 2011, Benjamin Berg <benjamin@sipsolutions.net>
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
import tempfile
import shutil
import subprocess

from sdaps import model

from sdaps import clifilter
from sdaps import template
from sdaps import matrix
from sdaps import paths

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

import buddies
import codecs


def report (survey, filter, filename = None, small = 0) :
	assert isinstance(survey, model.survey.Survey)

	# compile clifilter
	filter = clifilter.clifilter(survey, *filter)

	# First: calculate buddies

	# init buddies
	survey.questionnaire.calculate.init()

	# iterate over sheets
	survey.iterate(
		survey.questionnaire.calculate.read,
		lambda : survey.sheet.valid and filter()
	)

	# do calculations
	survey.questionnaire.calculate.calculate()


	# Second: report buddies

	# init buddies
	survey.questionnaire.report.init(small)

	# Filename of output
	if filename is None :
		filename = survey.new_path('report_%i.pdf')

	# Temporary directory for TeX files.
	tmpdir = tempfile.mkdtemp()

	try:
		# iterate over sheets
		survey.iterate(
			survey.questionnaire.report.report,
			lambda : survey.sheet.valid and filter(),
			tmpdir
		)


		# Copy class
		if paths.local_run :
			cls_file = os.path.join(paths.source_dir, 'tex', 'sdapsreport.cls')
		else :
			cls_file = os.path.join(paths.prefix, 'share', 'sdaps', 'sdapsreport.cls')
		shutil.copy(cls_file, os.path.join(tmpdir, 'sdapsreport.cls'))

		texfile = codecs.open(os.path.join(tmpdir, 'report.tex'), 'w', 'utf-8')

		author = _('Unknown')

		extra_info = []
		for key, value in survey.info.iteritems():
			if key == 'Author':
				author = value
				continue

			extra_info.append(u'\\addextrainfo{%(key)s}{%(value)s}' % {'key': key, 'value': value})

		extra_info = u'\n'.join(extra_info)
		texfile.write(r"""\documentclass{sdapsreport}

	\usepackage[utf8]{inputenc}

	\title{sdaps Report}
	\subject{%(title)s}
	\author{%(author)s}

	\addextrainfo{%(turned_in)s}{%(count)i}
	%(extra_info)s

	\begin{document}

	\maketitle

	""" % {'turned_in' : _('Turned in Questionnaires'), 'title': survey.title, 'author' : author, 'extra_info' : extra_info, 'count' : survey.questionnaire.calculate.count})

		survey.questionnaire.report.write(texfile, tmpdir)

		texfile.write(r"""
	\end{document}
	""")

		subprocess.call(['rubber', '--into', tmpdir, '-d', os.path.join(tmpdir, 'report.tex')])
		if not os.path.exists(os.path.join(tmpdir, 'report.pdf')):
			print _("Error running \"rubber -d\" to compile the LaTeX file.")
			raise

		shutil.move(os.path.join(tmpdir, 'report.pdf'), filename)

	except:
		print _("An occured during creation of the report.")
		shutil.rmtree(tmpdir)

		raise

	shutil.rmtree(tmpdir)

