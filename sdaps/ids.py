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

import model
import script

from ugettext import ugettext, ungettext
_ = ugettext

parser = script.subparsers.add_parser("ids",
    help=_("Export and import questionnaire IDs."))
parser.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: ids_%%i)"))
parser.add_argument('-a', '--add',
    metavar="FILE",
    help=_("Add IDs to the internal list from the specified file."))

@script.logfile
def ids(cmdline):
    survey = model.survey.Survey.load(survey_dir)

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

            line = line.decode('utf-8')
            line = line.strip('\r\n')
            to_add.append(survey.validate_questionnaire_id(line))

        survey.questionnaire_ids += to_add
        survey.save()

    else:
        if cmdline['output']:
            if cmdline['output'] == '-':
                ids = sys.stdout
            else:
                filename = cmdline['output']
                ids = file(filename, 'w')
        else:
            filename = survey.new_path('ids_%i')
            ids = file(filename, 'w')

        for id in survey.questionnaire_ids:
            ids.write(unicode(id).encode('utf-8'))
        ids.close()

parser.set_defaults(func=ids)

