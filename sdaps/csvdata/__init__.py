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
This module implements a simple export/import to/from CSV files.
"""

from sdaps import model
from sdaps import script

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


@script.register
@script.logfile
@script.doc(_(u'''export [filter...]

	Export to csv

	filter: filter expression to select the sheets to export

	creates data_[index].csv


csvdata import filename

	Import from csv

	filename: file to read from
	'''))
def csvdata (survey_dir, command, *args) :
	survey = model.survey.Survey.load(survey_dir)
	import csvdata
	if command == 'export' :
		csvdata.csvdata_export(survey, *args)
	elif command == 'import' :
		csvdata.csvdata_import(survey, *args)
	else :
		print _('Unknown command')

