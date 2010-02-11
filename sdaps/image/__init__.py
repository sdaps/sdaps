# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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
This modules contains low level image processing functions. These functions
are implemented in C for speed reasons. Usually one will not need to use these
directly, instead modules like "recognize" or "surface" use them to load and
analyze the image data.
"""

import os
import sys

from sdaps import paths

if paths.local_run :
    # image.so liegt in build_dir/image/
    __path__.append(os.path.join(paths.build_dir, 'image'))

# Wenn ein installiertes sdaps ausgeführt wird (local_run == False), liegt
# image.so im selben Verzeichnis wie diese Datei

from image import *
