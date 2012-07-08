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


class Box(object):

    def __init__(self, parent):
        self.state = 0
        self.metrics = dict()
        self.quality = 1
        self.x = parent.x
        self.y = parent.y
        self.width = parent.width
        self.height = parent.height


class Checkbox(Box):

    pass


class Textbox(Box):

    pass


class Additional_Mark(object):

    def __init__(self, parent):
        self.value = 0
