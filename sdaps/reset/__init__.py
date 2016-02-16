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

u"""
This module reset already stored data so next reports and exports will contain only new questionnaires.
"""

from collections import defaultdict
from sdaps import model
import bz2,os,cPickle
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def reset(survey):
    print "Removing stored data..."
    data = None
    with bz2.BZ2File(os.path.join(survey.survey_dir, 'survey'), 'rb') as f:
        data = cPickle.load(f)
        data.sheets = []
    with bz2.BZ2File(os.path.join(survey.survey_dir, 'survey'), 'w') as f:
        cPickle.dump(data, f, 2)
    print "Done"
