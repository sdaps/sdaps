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

class QObject(object):

    def __init__(self, parent):
        self.review_comment = ''

    @property
    def empty(self):
        return not self.review_comment

class Box(object):

    def __init__(self, parent):
        self.state = 0
        self.metrics = dict()
        self.quality = 1
        self.x = parent.x
        self.y = parent.y
        self.width = parent.width
        self.height = parent.height

        # Set _parent last, so that we don't trigger notifications
        # during __init__
        self._parent = parent

    def __setattr__(self, name, value):
        if hasattr(self, name):
            old_value = getattr(self, name)
        else:
            old_value = None

        object.__setattr__(self, name, value)
        # private
        if name.startswith('_'):
            return

        if value != old_value and hasattr(self, '_parent') and self._parent is not None:
            self._dirty = True
            self._parent.question.questionnaire.notify_data_changed(self._parent, self, name, old_value)

    @property
    def empty(self):
        return not self.state

class Checkbox(Box):

    pass


class Textbox(Box):

    def __init__(self, parent):
        self.text = str()

        Box.__init__(self, parent)


class Additional_Mark(object):

    def __init__(self, parent):
        self.value = 0

    @property
    def empty(self):
        return self.value == 0

