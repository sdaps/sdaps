# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2012, Benjamin Berg <benjamin@sipsolutions.net>
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


parser = script.add_project_subparser("reorder",
    help=_("Reorder pages according to questionnaire ID."),
    description=_("""This command reorders all pages according to the already
    recognized questionnaire ID. To use it add all the files to the project,
    then run a partial recognition using "recognize --identify". After this
    you have to run this command to reorder the data for the real recognition.
    """))


@script.connect(parser)
@script.logfile
def reorder(cmdline):
    survey = model.survey.Survey.load(cmdline['project'])

    from sdaps import reorder

    return reorder.reorder(survey)

