# -*- coding: utf-8 -*-
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

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


def stamp(survey, output_filename, cmdline):
    # copy questionnaire_ids
    # get number of sheets to create
    if cmdline['file'] or cmdline['random'] or cmdline['existing']:
        if not survey.defs.print_questionnaire_id:
            log.error(_("You may not specify the number of sheets for this survey. All questionnaires will be identical as the survey has been configured to not use questionnaire IDs for each sheet."))
            return 1

        if cmdline['existing']:
            questionnaire_ids = survey.questionnaire_ids
        elif cmdline['file']:
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
            questionnaire_ids = list(range(min, max))

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
            log.error(_("This survey has been configured to use questionnaire IDs. Each questionnaire will be unique. You need to use on of the options to add new IDs or use the existing ones."))
            return 1

        questionnaire_ids = None

    if questionnaire_ids is not None and not cmdline['existing']:
        survey.questionnaire_ids.extend(questionnaire_ids)

    if os.path.exists(survey.path('questionnaire.tex')):
        # use the LaTeX stamper
        from sdaps.stamp.latex import create_stamp_pdf
    else:
        raise AssertionError('Only LaTeX stamping is currently supported!')

    create_stamp_pdf(survey, output_filename, questionnaire_ids)

    survey.save()

