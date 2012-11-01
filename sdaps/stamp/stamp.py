# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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
import codecs

from sdaps import model
from sdaps import log

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


def stamp(survey, cmdline):
    # copy questionnaire_ids
    # get number of sheets to create
    if cmdline['file'] or cmdline['random']:
        if not survey.defs.print_questionnaire_id:
            log.error(_("You may not specify the number of sheets for surveys that do not print a quesitonnaire id."))
            return 1

        if cmdline['file']:
            if cmdline['file'] == '-':
                fd = sys.stdin
            else:
                fd = codecs.open(cmdline['file'], 'r', encoding="utf-8")

            questionnaire_ids = list()
            for line in fd.readlines():
                # Only strip newline/linefeed not spaces
                line = line.strip('\n\r')

                # Skip empty lines
                if line == "":
                    continue

                questionnaire_ids.append(survey.validate_questionnaire_id(line))
        else:
            # Create random IDs
            max = pow(2, 16)
            min = max - 50000
            questionnaire_ids = range(min, max)

            # Remove any id that has already been used.
            for id in survey.questionnaire_ids:
                if type(id) != int:
                    continue
                questionnaire_ids[id - min] = 0

            questionnaire_ids = [id for id in questionnaire_ids if id > min]
            random.shuffle(questionnaire_ids)
            questionnaire_ids = questionnaire_ids[:cmdline['random']]
    else:
        if survey.defs.print_questionnaire_id:
            log.error(_("Questionnaire IDs are required, use --random to create random ones or specify some using --file."))
            return 1

        questionnaire_ids = None

    if os.path.exists(survey.path('questionnaire.tex')):
        # use the LaTeX stamper
        from sdaps.stamp.latex import create_stamp_pdf
    else:
        from sdaps.stamp.generic import create_stamp_pdf
    create_stamp_pdf(survey, questionnaire_ids)

    survey.save()

