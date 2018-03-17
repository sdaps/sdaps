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

import gettext


def ugettext(string):
    '''gettext for unicode objects
    '''
    translation = gettext.gettext(string.encode('UTF-8')).decode('UTF-8')

    return translation.split('|', 1)[-1]


def ungettext(singular, plural, n):
    '''ngettext for unicode objects
    '''
    return gettext.ngettext(
        singular.encode('UTF-8'),
        plural.encode('UTF-8'),
        n).decode('UTF-8')
