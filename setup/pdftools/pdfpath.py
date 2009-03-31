# pdftools - A library of classes for parsing and rendering PDF documents.
# Copyright (C) 2001-2008 by David Boddie
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Created: 2003

"""
pdfpath.py

Classes for representing path information in PDF documents.

Path state command support.
"""

class Path:

    def __init__(self, subpaths, clipping, painting):
    
        self.subpaths = subpaths
        self.clipping = clipping
        self.painting = painting

class Subpath:

    def __init__(self, contents):
    
        self.contents = contents

class Move:

    def __init__(self, point):
    
        self.point = point
    
    def __repr__(self):
    
        return "<Move: %s>" % repr(self.point)

class Line:

    def __init__(self, point1, point2):
    
        self.point1 = point1
        self.point2 = point2
    
    def __repr__(self):
    
        return "<Line: from %s to %s>" % ( repr(self.point1), repr(self.point2) )

class Bezier:

    def __init__(self, point1, control1, control2, point2):
    
        self.point1 = point1
        self.control1 = control1
        self.control2 = control2
        self.point2 = point2
    
    def __repr__(self):
    
        return "<Bezier: from %s to %s; control points: %s %s>" % (
            repr(self.point1), repr(self.point2),
            repr(self.control1), repr(self.control2)
            )

class Rectangle:

    def __init__(self, point, width, height):
    
        self.point = point
        self.width = width
        self.height = height
    
    def __repr__(self):
    
        return "<Rectangle: origin: %s; dimensions: %.3f x %.3f>" % (
            repr(self.point), self.width, self.height
            )

class Close:

    pass

class Clip:

    def __init__(self, winding):
    
        self.winding = winding
    
    def __repr__(self):
    
        return "<Clip: %s rule>" % self.winding

# Painting operations

class Stroke:

    pass

class Fill:

    def __init__(self, winding):
    
        self.winding = winding
    
    def __repr__(self):
    
        return "<Fill: %s rule>" % self.winding

class Gradient:

    def __init__(self, name):
    
        self.name = name

