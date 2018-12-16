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

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

parser = script.add_project_subparser("stamp",
    help=_("Add marks for automatic processing."),
    description=_("""This command creates the printable document. Depending on
    the projects setting you are required to specifiy a source for questionnaire
    IDs."""))

parser.add_argument('-r', '--random',
    metavar="N",
    help=_("If using questionnaire IDs, create N questionnaires with randomized IDs."),
    type=int)
parser.add_argument('-f', '--file',
    help=_("If using questionnaire IDs, create questionnaires from the IDs read from the specified file."))
parser.add_argument('--existing',
    action="store_true",
    help=_("If using questionnaire IDs, create questionnaires for all stored IDs."))

parser.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: stamp_%%i.pdf)"))

@script.connect(parser)
@script.logfile
def stamp(cmdline):
    from sdaps import stamp

    survey = model.survey.Survey.load(cmdline['project'])

    if cmdline['output'] is None:
        output = survey.new_path('stamped_%i.pdf')
    else:
        output = cmdline['output']

    return stamp.stamp(survey, output, cmdline)


