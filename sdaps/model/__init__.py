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

'''data model for sdaps

Survey
======

survey ::

    +-- questionnaire
    |        +-- qobjects ---------------+
    |                +-- boxes ----------+
    +-- sheets                           |
            +-- data dictionary          |
            |        +-- data objects <--+
            +-- images


The questionnaire tree resembles the structer of the questionnaire and the
internal structure of the programm. It is set up by the setup script and not
altered(much) later.

The sheets tree holds the data of the answered questionnaires. The sheet
objects are created while the scanned images are added to the project.

Iterating through sheets and jumping
====================================

Survey provides a function iterate. It iterates through the sheets and calls a
function for each. Inside this function, the sheet is accessible through
survey.sheet(a property, pointing to the actual sheet)
The functions goto_something jump the survey.sheet pointer to the specified
sheet.

Buddies
=======

A script may define a buddy class for a class in the model. Then each object of
that model class is accompanied by an object of the buddy class.
The buddy object is instanciated automatically upon first access and then
cached. It is not saved on disc.

The buddy system allows you to define additional methods and attributes for
the objects in the model.

'''

from . import buddy
from . import data
from . import questionnaire
from . import sheet
from . import survey


