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

import model
import script

from ugettext import ugettext, ungettext
_ = ugettext


@script.register
@script.logfile
@script.doc(_(u'''[pattern = '%i\\n']

	Write a list containing all questionnaire ids.

	creates ids_[index]
	'''))
def ids (survey_dir, pattern = '%i\n') :
	survey = model.survey.Survey.load(survey_dir)

	pattern = pattern.decode('utf-8')

	ids = file(survey.new_path('ids_%i'), 'w')
	for id in survey.questionnaire_ids :
		ids.write((pattern % id).encode('utf-8'))
	ids.close()

