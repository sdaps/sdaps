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

from sdaps import model
from sdaps import script

import os
import sys

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

parser = script.add_project_subparser("ids",
    help=_("Export and import questionnaire IDs."),
    description=_("""This command can be used to import and export questionnaire
    IDs. It only makes sense in projects where such an ID is printed on the
    questionnaire. Note that you can also add IDs by using the stamp command,
    which will give you the PDF at the same time."""))
parser.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: ids_%%i)"))
parser.add_argument('-a', '--add',
    metavar="FILE",
    help=_("Add IDs to the internal list from the specified file."))

@script.connect(parser)
@script.logfile
def ids(cmdline):
    survey = model.survey.Survey.load(cmdline['project'])

    if cmdline['add']:
        if cmdline['add'] == '-':
            ids = sys.stdin
        else:
            ids = open(cmdline['add'], 'r')

        to_add = []
        for line in ids.readlines():
            # Skip empty lines
            if line == "":
                continue

            line = line
            line = line.strip('\r\n')
            to_add.append(survey.validate_questionnaire_id(line))

        survey.questionnaire_ids += to_add
        survey.save()

    else:
        if cmdline['output']:
            if cmdline['output'] == '-':
                outfd = os.dup(sys.stdout.fileno())
                ids = os.fdopen(outfd, 'w')
            else:
                filename = cmdline['output']
                ids = open(filename, 'w')
        else:
            filename = survey.new_path('ids_%i')
            ids = open(filename, 'w')

        for id in survey.questionnaire_ids:
            ids.write(str(id))
            ids.write('\n')

        if ids != sys.stdout:
            ids.close()


