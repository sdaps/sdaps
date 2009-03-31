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
pdftext.py

Classes for representing textual information in PDF documents.

Text state command support.
"""

# Import required items from the pdftools module.
from pdfdefs import point

try:
    from PyQt4.QtGui import QFontDatabase, QFontMetricsF
    with_metrics = True

except ImportError:
    with_metrics = False


class Font:

    def __init__(self, font, size):

        self.font = font
        self.size = size
    
    def _width_without_metrics(self, text):
    
        # Return the width of this piece of text when rendered using this
        # font.
        
        # * To be replaced: return a value for a monospaced font. *
        return len(text) * self.size
    
    def _width_with_metrics(self, text):
    
        # Return the width of this piece of text when rendered using this
        # font.
        
        fontName = self.font["BaseFont"].name
        at = fontName.find("+")
        if at != -1:
            fontName = fontName[at+1:]

        if "-" in fontName:
            family, style = fontName.split("-")[:2]
        elif " " in fontName:
            family, style = fontName.split(" ")[:2]
        elif "," in fontName:
            family, style = fontName.split(",")[:2]
        else:
            family = fontName
            style = ""
        
        font = QFontDatabase().font(family, style, self.size)
        font.setPointSizeF(self.size)
        fm = QFontMetricsF(font)
        return fm.width(text)
    
    def width(self, text, use_metrics = False):
    
        if use_metrics and with_metrics:
            return self._width_with_metrics(text)
        else:
            return self._width_without_metrics(text)


class Text:

    def __init__(self, text, font, size, character_spacing, word_spacing,
                 rendering_matrix, position):
    
        self.text = text
        
        # Keep a reference to the font dictionary used.
        self.font = font
        
        self.size = size
        
        self.character_spacing = character_spacing
        self.word_spacing = word_spacing
        
        self.rendering_matrix = rendering_matrix.copy()
        self.position = position
        
        # This is temporary
        #sys.stdout.write(text)
    
    def after(self):
    
        # Calculate the location of the current point after the text has
        # been placed using the position given as the initial location of the
        # current point.
        
        # We must first determine the direction of the text.
        
        # * Assume horizontal text. *
        
        # We examine each character in turn, calculating its width or
        # height, depending on the writing direction, then apply the
        # character spacing correction to this length value.
        
        # If a space character is found then the word spacing correction is
        # additionally applied to the length found for the space.
        
        # Finally, the total displacement of the current point is added to
        # its initial value to determine its new value.
        return point(self.font.width(self.text) + self.character_spacing, 0)
