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

# Created: 2004

"""
pdfdefs.py

Definitions of PDF-related classes and values that are needed by the other
pdftools modules.
"""

import copy, string, sys, types


class boolean:
    """Generic boolean class. Used to define "true" and "false".
    """
    def __init__(self, value):

        self.value = value
    
    def __repr__(self):
    
        return "<boolean: %s>" % self.value
    
    def __cmp__(self, other):
    
        if not isinstance(other, boolean):
        
            # Invalid comparison
            return -1
        
        if self.value == other.value:
        
            return 0
        
        elif self.value == "true":
        
            return 1
        
        elif self.value == "false":
        
            return -1
        
        # Invalid value(s)
        return -1

true = boolean('true')
false = boolean('false')

class empty:
    """The empty class of which null is an instance."""
    pass

null = empty()

class reference:
    """Class for defining references to objects. Instantiate with object and
    generation attributes, "obj" and "gen".

    Example: ref = pdftools.reference(15, 0)
    """
    def __init__(self, obj, gen):

        self.obj = obj
        self.gen = gen

class name:
    """Class for defining names. Typically the / symbol which defines names in
    a PDF document is removed when the name is stored in the "name" attribute.

    Example: n = pdftools.name("Font")
    """
    def __init__(self, name):

        self.name = name
    
    def __repr__(self):
    
        return '<name: %s>' % self.name
    
    def __cmp__(self, other):
    
        if not isinstance(other, name):
        
            # Invalid comparison
            return -1
        
        return cmp(self.name, other.name)

class comment:
    """Comment class with "comment" attribute.

    Example: comment = pdftools.comment("Some text")
    """
    def __init__(self, comment):

        self.comment = comment
    
    def __repr__(self):
    
        return "<comment: %s>" % self.comment

class object:
    """Object class with "object" attribute which usually contains a list of
    other elements of a PDF file, such as dictionaries, objects, references,
    arrays, etc.

    Example: obj = pdftools.object(["Some text", [1,2,3]])
    """
    def __init__(self, object):

        self.object = object

class Stream:
    """Stream class. The "start" attribute of an instance of this class points
    to the start of a stream in a file. The "end" points to the character after
    the end of the stream, so that slice notation can be used to extract the
    stream from the document.

    Example: s = pdftools.Stream(32, 64)
    """
    def __init__(self, start, end):

        self.start = start
        self.end = end


class matrix:

    def __init__(self, rows):
    
        self.rows = rows
    
    def __repr__(self):
    
        values = reduce(lambda x, y: x + y, self.rows)
        format = ("((%03f, %03f, %03f),\n"
                  " (%03f, %03f, %03f),\n"
                  " (%03f, %03f, %03f))")
        return format % tuple(values)
    
    def ___mul___(self, r1, r2):
    
        rows = [[r1[0][0]*r2[0][0] + r1[0][1]*r2[1][0] + r1[0][2]*r2[2][0],
                 r1[0][0]*r2[0][1] + r1[0][1]*r2[1][1] + r1[0][2]*r2[2][1],
                 r1[0][0]*r2[0][2] + r1[0][1]*r2[1][2] + r1[0][2]*r2[2][2]],
                [r1[1][0]*r2[0][0] + r1[1][1]*r2[1][0] + r1[1][2]*r2[2][0],
                 r1[1][0]*r2[0][1] + r1[1][1]*r2[1][1] + r1[1][2]*r2[2][1],
                 r1[1][0]*r2[0][2] + r1[1][1]*r2[1][2] + r1[1][2]*r2[2][2]],
                [r1[2][0]*r2[0][0] + r1[2][1]*r2[1][0] + r1[2][2]*r2[2][0],
                 r1[2][0]*r2[0][1] + r1[2][1]*r2[1][1] + r1[2][2]*r2[2][1],
                 r1[2][0]*r2[0][2] + r1[2][1]*r2[1][2] + r1[2][2]*r2[2][2]]]
        
        return rows
    
    def __mul__(self, other):
    
        r1 = self.rows
        r2 = other.rows
        
        return matrix(self.___mul___(r1, r2))
    
    def __rmul__(self, other):
    
        r1 = other.rows
        r2 = self.rows
        
        return matrix(self.___mul___(r1, r2))
    
    def copy(self):
    
        return matrix(copy.deepcopy(self.rows))


def identity(size):

    return matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


class vector:

    def __init__(self, x, y):
    
        self.x, self.y = x, y
    
    def __repr__(self):
    
        return "<vector: (%.3f, %.3f)>" % (self.x, self.y)
    
    def __add__(self, other):
    
        x = self.x + other.x
        y = self.y + other.y
        
        # Return a new object.
        return vector(x, y)
    
    __radd__ = __add__
    
    def __sub__(self, other):
    
        x = self.x - other.x
        y = self.y - other.y
        
        # Return a new object.
        return vector(x, y)
    
    def __rsub__(self, other):
    
        x = other.x - self.x
        y = other.y - self.y
        
        # Return a new object.
        return vector(x, y)
    
    def __cmp__(self, other):
    
        # This next expression will only return zero (equals) if both
        # expressions are false.
        return self.x == other.x or self.y == other.y
    
    def __abs__(self):
    
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def copy(self):
    
        """vector = copy(self)
        
        Copy the vector so that new vectors containing the same values
        are passed around rather than references to the same object.
        """
        
        return vector(self.x, self.y)

# The point class is a synonym for the vector class.
# We subclass vector in order to make it clear that point is a class.
# (It's easier to search for classes if they are declared in some way.)

class point(vector):

    pass


delimiter = '<>()[]{}/%'
not_regular = string.whitespace + delimiter
escaped = (('\\n', '\012'), ('\\r', '\015'), ('\\t', '\011'), ('\\b', '\177'),
       ('\\f', '\014'), ('\\(', '('), ('\\)', ')'), ('\\\\', '\\'))
hexadecimal = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
           '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12,
           'd': 13, 'e': 14, 'f': 15}

whitespace = '\000\011\012\014\015 '

# hexa = '0123456789abcdef'
integer = '0123456789+-'
real = '0123456789+-.'

base85m4 = long(pow(85,4))
base85m3 = long(pow(85,3))
base85m2 = long(pow(85,2))


class FileWrapper:

    def __init__(self, file):
    
        self.file = file
    
    def __getitem__(self, item):
    
        if type(item) == types.SliceType:
        
            self.file.seek(item.start)
            length = max(0, item.stop - item.start)
            data = self.file.read(length)
            if len(data) != length:
                raise IndexError, "string index out of range"
        else:
        
            self.file.seek(item)
            data = self.file.read(1)
            if not data:
                raise IndexError, "string index out of range"
        
        return data
    
    if sys.version_info < 2.0:
    
        def __getslice__(self, i, j):
        
            return self[max(0, i):max(0, j):]
    
    def __len__(self):
    
        offset = self.file.tell()
        self.file.seek(0, 2)
        length = self.file.tell()
        self.file.seek(offset, 0)
        return int(length)
    
    def find(self, sub, start = 0, end = None):
    
        if end is None:
            end = len(self)
        elif end < 0:
            end = len(self) + end
        
        length = len(sub)
        if start < 0:
            window_start = end + start
        else:
            window_start = start
        
        self.file.seek(window_start, 0)
        
        # Try to read twice the length of the substring.
        window_end = window_start + length * 2
        # Only read as much as is available.
        read_to = min(window_end, end)
        read_length = read_to - window_start
        data = self.file.read(read_length)
        
        while end - window_start >= length:
        
            at = data.find(sub)
            if at != -1:
            
                return window_start + at
            
            # Start searching after the substring length.
            window_start = window_start + length
            # Try to read another substring worth of data.
            window_end = window_end + length
            # Only read as much as is available.
            next_read_to = min(window_end, end)
            read_length = next_read_to - read_to
            read_to = next_read_to
            data = data[length:] + self.file.read(read_length)
        
        return -1
    
    def rfind(self, sub, start = 0, end = None):
    
        if end is None:
            window_end = end = len(self)
        elif end < 0:
            window_end = len(self) + end
        else:
            window_end = end
        
        length = len(sub)
        if start < 0:
            window_start = end + start
        else:
            window_start = start
        
        # Try to read twice the length of the substring.
        window_start = window_end - length * 2
        # Only read as much as is available.
        read_from = max(start, window_start)
        read_length = window_end - read_from
        
        self.file.seek(read_from, 0)
        data = self.file.read(read_length)
        
        while window_end - start >= length:
        
            at = data.rfind(sub)
            if at != -1:
            
                return read_from + at
            
            # Start searching before the substring length.
            window_end = window_end - length
            # Try to read another substring worth of data.
            window_start = window_start - length
            # Only read as much as is available.
            next_read_from = max(start, window_start)
            read_length = read_from - next_read_from
            self.file.seek(next_read_from, 0)
            read_from = next_read_from
            data = self.file.read(read_length) + data[:-length]
        
        return -1

class PDFError(Exception):

    pass

# Abstract class from which the PDFDocument and PDFContents classes inherit
# common methods.

class Abstract:

    def _skip_whitespace(self, offset):
    
        while offset < self.length:

            if self.file[offset] in whitespace:
                offset = offset + 1
            else:
                break
    
        return offset
    
    def _read_comment(self, offset):
    
        at = offset
        while self.file[at] not in '\012\015':
    
            at = at + 1
    
        text = self.file[offset:at]
    
        while self.file[at] in '\012\015':
    
            at = at + 1
    
        return at, comment(text)
    
    def _read_string(self, offset):
    
        # Strings start with ( and end with a matched )
        # The level of parentheses is the number of ) required to end
        # the string
    
        level = 1
    
        at = offset

        while (level > 0) and (at < self.length):
    
            # Look for \
            backslash = string.find(self.file, '\\', at)
            if backslash == -1:
                backslash = self.length
    
            # Look for (
            start = string.find(self.file, '(', at)
            if start == -1:
                start = self.length
    
            # Look for )
            end = string.find(self.file, ')', at)
            if end == -1:
                end = self.length
    
            # \ ( ) or \ ) (
            if (backslash < start) and (backslash < end):
    
                # Skip escaped character
                at = backslash + 2
    
            # ( \ ) or ( ) \
            elif start < end:
    
                level = level + 1
                at = start + 1
    
            # ) \ ( or ) ( \
            elif end < start:
    
                level = level - 1
                at = end + 1
    
            else:
                raise PDFError, 'Problem with string at %s' % hex(offset)
    
        # All text from the character at "offset" until the character before
        # "at" is comment.
        return at, self._clean_string(self.file[offset:at-1])
    
    
    def _clean_string(self, a):

        for old, new in escaped:
    
            a = string.replace(a, old, new)
    
        # Octal numbers are the same in Python as they are in PDF strings
    
        return a

    
    def _read_hexadecimal(self, offset):
    
        # Hexadecimal strings start with a < and end with a >
        # Nesting is not allowed
        # The characters contained are 0-9 A-F a-f
        at = string.find(self.file, '>', offset)
    
        return at + 1, self._clean_hexadecimal(string.lower(self.file[offset:at]))
    
    
    def _clean_hexadecimal(self, a):
    
        # Read the string, converting the pairs of digits to
        # characters
        b = ''
        shift = 4
        value = 0
    
        try:
    
            for i in a:
    
                value = value | (hexadecimal[i] << shift)
                shift = 4 - shift
                if shift == 4:
                    b = b + chr(value)
                    value = 0
    
        except ValueError:
        
            raise PDFError, 'Problem with hexadecimal string %s' % a
    
        return b
    
    def _asciihexdecode(self, text):

        at = string.find(text, '>')

        return self._clean_hexadecimal(string.lower(text[:at]))

    def _ascii85decode(self, text):
    
        end = string.find(text, '~>')
    
        new = []
        i = 0
        ch = 0
        value = 0
    
        while i < end:
    
            if text[i] == 'z':
    
                if ch != 0:
                    raise PDFError, 'Badly encoded ASCII85 format.'
    
                new.append('\000\000\000\000')
    
                ch = 0
                value = 0
    
            else:
    
                v = ord(text[i])
                if v >= 33 and v <= 117:
    
                    if ch == 0:
                        value = ((v-33) * base85m4)
                    elif ch == 1:
                        value = value + ((v-33) * base85m3)
                    elif ch == 2:
                        value = value + ((v-33) * base85m2)
                    elif ch == 3:
                        value = value + ((v-33) * 85)
                    elif ch == 4:
                        value = value + (v-33)
    
                        c1 = int(value >> 24)
                        c2 = int((value >> 16) & 255)
                        c3 = int((value >> 8) & 255)
                        c4 = int(value & 255)
    
                        new.append(chr(c1) + chr(c2) + chr(c3) + chr(c4))
    
                    ch = (ch + 1) % 5
    
            i = i + 1
    
        if ch != 0:
    
            c = chr(value >> 24) + chr((value >> 16) & 255) + \
                chr((value >> 8) & 255) + chr(value & 255)
    
            new.append(c[:ch-1])
    
        return string.join(new, "")

    def _read_name(self, offset):
    
        # Read characters in the range 33-126 but not delimiters
        b = ''
        at = offset
        
        while at < self.length:
        
            n = ord(self.file[at])
            
            if n >= 33 and n <= 126 and (self.file[at] not in delimiter):
                at = at + 1
            
            else:
                break
        
        return at, name(self._clean_name(self.file[offset:at]))
    
    def _clean_name(self, a):
    
        # Find # symbols followed by hexadecimal
    
        b = ''
        at = 0

        try:
    
            while at < self.length:
                h = string.find(a, '#', at)
                if h == -1:
                    b = b + a[at:]
                    break
                else:
                    b = b + a[at:h] + self._clean_hexadecimal(a[h+1:h+3])
                    at = h + 3
    
        except IndexError:
        
            raise PDFError, 'Problem with name %s' % a
    
        return b
    
    def _read_next(self, offset, this_array):
    
        #print "_read_next", hex(offset)
        c = self.file[offset]
        
        # Comment
        if c == '%':
    
            #print 'comment', hex(offset)
            at, element = self._read_comment(offset+1)
    
        # Boolean
        elif c == 't':
    
            if self.file[offset:offset+4] == 'true':
    
                #print 'true', hex(offset)
                element = true
                at = offset + 4
    
            else:
                raise PDFError, 'Expected true at %s' % hex(offset)
    
        elif c == 'f':
    
            if self.file[offset:offset+5] == 'false':
    
                #print 'false', hex(offset)
                element = false
                at = offset + 5
    
            else:
                raise PDFError, 'Expected false at %s' % hex(offset)
    
        # Integer or Real
        elif c in integer:
    
            value = c
            offset = offset + 1
            is_real = 0
            while offset < self.length:
    
                n = self.file[offset]
                if n in integer:
                    value = value + n
                elif n in real:
                    value = value + n
                    is_real = 1
                else:
                    break
    
                offset = offset + 1
    
            at = offset
    
            if is_real == 0:
                #print 'integer', hex(offset), int(value)
                element = int(value)
            else:
                #print 'real', hex(offset), float(value)
                element = float(value)
    
        elif c in real:
    
            value = c
            offset = offset + 1
            while offset < self.length:
    
                n = self.file[offset]
                if n in real:
                    value = value + n
                else:
                    break
    
                offset = offset + 1
    
            at = offset
            element = float(value)
    
        # Name
        elif c == '/':
    
            #print 'name', hex(offset)
            at, element = self._read_name(offset+1)
    
        # String
        elif c == '(':
    
            #print 'string', hex(offset)
            at, element = self._read_string(offset+1)
    
        # Hexadecimal string or dictionary
        elif c == '<':
    
            if self.file[offset+1] != '<':
    
                #print 'hexadecimal string', hex(offset)
                at, element = self._read_hexadecimal(offset+1)
    
            else:
                #print 'dictionary', hex(offset)
                at, element = self._read_dictionary(offset+2)
    
        # Array
        elif c == '[':
    
            #print "array", hex(offset)
            at, element = self._read_array(offset+1)
    
        # null
        elif c == 'n':
        
            if self.file[offset:offset+4] == 'null':
    
                #print 'null', hex(offset)
                at = offset + 4
                element = null
    
            else:
                raise PDFError, 'Expected null at %s' % hex(offset)
    
        # Object reference
        elif c == 'R':
    
            #print 'reference', hex(offset)
            # Take the last two items in the array and check that they
            # are integers
            obj, gen = this_array[-2], this_array[-1]
            this_array.pop()
            this_array.pop()
    
            element = reference(obj, gen)
            at = offset + 1
    
        # Stream or other token beginning with s
        elif c == 's':
        
            if self.file[offset:offset+6] == 'stream':
                #print 'stream', hex(offset)
                at, element = self._read_stream(offset+6)
            
            elif self.file[offset:offset+9] == 'startxref':
                return offset, None
        
        # Object
        elif c == 'o':
    
            if self.file[offset:offset+3] == 'obj':
            
                #print 'object', hex(offset)
                # Take the last two items in the array and check that they
                # are integers
                obj, gen = this_array[-2], this_array[-1]
                this_array.pop()
                this_array.pop()
    
                # Read the object
                at, element = self._read_object(offset+3)
                element.obj = obj
                element.gen = gen
    
            else:
                raise PDFError, 'Expected obj at %s' % hex(offset)
    
        else:
    
            raise PDFError, 'Unknown object found at %s' % hex(offset)
    
        return at, element
    
    def _read_array(self, offset):
    
        #print '_read_array', hex(offset)
        # Arrays begin with [ and end with ]
        # They can be nested like strings, but contain objects rather
        # than just a series of bytes
    
        this_array = []
    
        at = offset

        while at < self.length:
    
            at = self._skip_whitespace(at)
    
    #        print hex(at)
    
            # Look at the next character
    
            # End of array
            if self.file[at] == ']':
    
                break
    
            else:
    
                at, element = self._read_next(at, this_array)
                
                # Add the element to the array
                if element is not None:
                    this_array.append(element)
                else:
                    break
        
        #print '_read_array return', hex(at)
        return at + 1, this_array
    
    def _read_dictionary(self, offset):
    
        #print '_read_dictionary', hex(offset)
        # Dictionaries start with << and end with >>
        # They can be nested
    
        at = offset

        this_array = []
    
        while at < self.length:
        
            at = self._skip_whitespace(at)
    
            # Look at the next character
    
            # End of dictionary
            if self.file[at:at+2] == '>>':
            
                break
    
            else:
            
                #print "dictionary next", hex(at)
                at, element = self._read_next(at, this_array)
                
                if element is not None:
                    this_array.append(element)
                else:
                    break
    
        # Collate the list into key value pairs
        dict = {}
        keyvalue = 0
    
        for element in this_array:
    
            # Key or value
            if keyvalue == 0:
                if isinstance(element, name) == 0:
                    raise PDFError, \
                          'Key found which was not a name "'+repr(element) + \
                          '" in dictionary at %s' % hex(offset - 1)
                else:
                    key = element
                    keyvalue = 1
            else:
                # Use the textual form of the name to make the key
                dict[key.name] = element
                keyvalue = 0
    
        if keyvalue == 1:
            print 'Incomplete dictionary at %s ?' % hex(offset - 1)
    
        #print '_read_dictionary return', hex(at)
    
        return at + 2, dict
    
    def _read_object(self, offset):
    
        # Objects start with obj and end with endobj
        #print '_read_object', hex(offset)
    
        at = offset

        this_array = []
    
        while at < self.length:
    
            at = self._skip_whitespace(at)
    
            if self.file[at:at+6] == 'endobj':
    
                break
    
            else:
            
                #print "object next", hex(at)
                at, element = self._read_next(at, this_array)
                
                if element is not None:
                    this_array.append(element)
                else:
                    break
    
        #print '_read_object return'
    
        return at+6, object(this_array)
    
    def _read_ref(self, offset):
    
        at, obj = self.read_integer(offset, self.length)
        at = self._skip_whitespace(at)
        at, gen = self.read_integer(at, self.length)
        at = self._skip_whitespace(at)
        at, element = self._read_next(at, [obj, gen])
    
        return element
    
    def _read_stream(self, offset):
    
        #print '_read_stream', hex(offset)
        
        # Expect either a carriage return then a linefeed or just a linefeed.
        
        if self.file[offset:offset + 2] == '\r\n':
        
            offset = offset + 2
        
        elif self.file[offset] == '\n':
        
            offset = offset + 1
        
        else:
        
            raise PDFError, "Unexpected start to the stream at %x" % offset
        
        # Temporary solution
        at = string.find(self.file, 'endstream', offset)
    
        #print 'endstream', hex(at)
        return at+9, Stream(offset, at)
