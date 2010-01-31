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
SDAPS has a modular design. It ships a core python module called "model" which
is responsible for storing and basic modification of the data. When other
modules like "recognize" are loaded they '''extend''' the original model.

As an example the "recognize" module contains everything required to analyize
the scanned data and find checkmarks. However, it will in addition load the
"image", "matrix" and "surface" modules. These three modules are responsible
for loading and caching the image data and doing some pre-processing of the
image data (transformation matrix calculation).

Please have a look at the documentation of the "model" package.
"""
