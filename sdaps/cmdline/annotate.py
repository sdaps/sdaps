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

import os

from sdaps import model
from sdaps import script

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


parser = script.add_project_subparser("annotate",
    help=_("Annotate the questionnaire and show the recognized positions."),
    description=_("""This command is mainly a debug utility. It creates an
    annotated version of the questionnaire, with the information that SDAPS
    knows about it overlayed on top."""))

@script.connect(parser)
@script.logfile
def annotate(cmdline):
    from sdaps.annotate import annotate

    survey = model.survey.Survey.load(cmdline['project'])

    return annotate(survey)

