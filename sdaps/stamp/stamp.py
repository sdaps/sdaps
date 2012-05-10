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

import random

import os
import sys
import math

from sdaps import model

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

def stamp (survey, count = 0, used_ids = None) :
	# copy questionnaire_ids
	# get number of sheets to create
	if count :
		if not survey.defs.print_questionnaire_id :
			print _("You may not specify the number of sheets for surveys that do not print a quesitonnaire id.")
			return 1

		if used_ids :
			used_ids = file(used_ids, 'r')
			survey.questionnaire_ids.extend([int(id) for id in used_ids.readlines()])
			used_ids.close()
		sheets = count
		max = pow(2, 16)
		min = max - 50000
		questionnaire_ids = range(min, max)

		# Remove any idea that has already been used.
		for id in survey.questionnaire_ids :
			questionnaire_ids[id] = 0
		questionnaire_ids = [id for id in questionnaire_ids if id > min]
		random.shuffle(questionnaire_ids)
		questionnaire_ids = questionnaire_ids[:sheets]
	else :
		if survey.defs.print_questionnaire_id :
			print _("You need to specify the number of questionnaires to create when questionnaire ids are printed.")
			return 1

		sheets = 1
		questionnaire_ids = None

	if os.path.exists(survey.path('questionnaire.tex')):
		# use the LaTeX stamper
		from sdaps.stamp.latex import create_stamp_pdf
	else:
		from sdaps.stamp.generic import create_stamp_pdf
	create_stamp_pdf(survey, questionnaire_ids)

	survey.save()

