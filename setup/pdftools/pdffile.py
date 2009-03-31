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

# Historical information

# Created:        Fri 9th March 2001

"""
Example of use:

    from pdftools.pdffile import PDFDocument
    
    file = "MyFile.pdf"
    doc = PDFDocument(file)
    
    print "Document uses PDF format version", doc.document_version()
    
    pages = doc.count_pages()
    print "Document contains %i pages." % pages
    
    if pages > 123:
    
        page123 = doc.read_page(123)
        contents123 = page123.read_contents()
        
        print "The objects found in this page:"
        print
        print contents123.contents
    
"""
import sys, types, zlib

# Import useful definitions.
from pdfdefs import *

# Import related modules.
import pdftext, pdfpath


class PDFDocument(Abstract):
    """PDF document reading class.

    Open a document by reading a PDF file using a file name passed as a string
    on instantiation.

    Example:

        file = "MyFile.pdf"
        doc = PDFDocument(file)
    
    Useful methods:
    
        total_number = count_pages(self)
        page_object  = read_page(self, number) # 1 <= number <= total_number
    
    """
    def __init__(self, path, in_memory = 0):

        try:
            if in_memory:
                self.file = open(path, 'rb').read()
            else:
                self.file = FileWrapper(open(path, 'rb'))
        except IOError:
            raise PDFError, "Couldn't open the specified file: %s" % path
        
        self.path = path
        self.length = len(self.file)
        
        # Prepare the document for reading.
        self._read_document()
    
    # Return version information

    def document_version(self):
        """Read the version of PDF used to encode the document.
            Returns a string containing the version number.

        Example: version = doc.document_version()
        """
        offset, element = self._read_comment(1)
    
        if isinstance(element, comment) == 0:
            print 'Not a PDF file'
    
        elif element.comment[:4] != 'PDF-':
            raise PDFError, 'Not a PDF file'
    
        else:
            self.version = element.comment[4:]

        return self.version
    
    def find_page(self, number, count = 0, tree = None):
    
        """number, dict = find_page(self, number, count = 0, tree = None)
        
        Takes a page number and a starting tree object and returns the
        page number and either a dictionary containing the page attributes
        (if successful) or None (if unsuccessful).
        """
        
        # Using the catalogue entry if necessary, descend until a
        # particular page is found.
        
        if tree == None:
        
            pages = self.catalog['Pages']
            
            tree = self._dereference(pages)
        
        # Page tree
        if tree['Type'].name == 'Pages':
        
            if count < number <= count + tree['Count']:
            
                # The page is contained within a child of this node.
                kids = tree['Kids']
                
                # We do not know how many pages are contained within each
                # child node, so we must search through them rather than
                # trying to directly index the "Kids" array.
                
                for ref in kids:
                
                    kid = self._dereference(ref)
                    count, kid = self.find_page(number, count, kid)
                    
                    if kid is not None:
                    
                        # The required page was found.
                        return count, kid
            
            else:
            
                # The page is outside the range of pages contained beneath
                # this node.
                count = count + tree["Count"]
        
        elif tree['Type'].name == 'Page':
        
            # Page
            
            # Increment the page counter to provide this page with the correct
            # number and compare it with the page number we are looking for.
            count = count + 1
            
            if count == number:
            
                return count, tree
        
        return count, None
    
    def count_pages(self):
    
        # Read the "Pages" catalogue entry.
        pages = Pages(self, self._dereference(self.catalog["Pages"]))
        
        # Read the "Count" property (dictionary entry).
        return pages["Count"]
    
    # _read_catalog() must be called before this function is called.
    
    def read_page(self, number):
        """page_object = read_page(self, number)
        
        Return a Page object corresponding to the specified page.
        
        If the page is not found then a PDFError exception is raised.
        
        Example: page = doc.read_page(123)
        """
        # Look up the page details.
        number, page = self.find_page(number)
        
        if page is None:
        
            raise PDFError, "No such page"
        
        return Page(self, page)
    
    def write_document(self, path = None, linearized = 0):
    
        """write_document(self, path = None, linearized = 0)
        
        Write the document to a file, either using an optional path or to
        the original file. If linearized, the file will be optimised for
        access by readers that read the file sequentially.
        """
        
        if path is None:
        
            path = self.path
        
        try:
        
            fh = open(path, "wb")
            self._write_document(fh, linearized)
        
        except IOError:
        
            raise PDFError, "Failed to write the document to %s" % path
    
    def _read_trailer(self, offset):
    
        at = self._skip_whitespace(offset)
        at, trailer_dict = self._read_dictionary(at+2)
        
        at = string.find(self.file, 'startxref', at)
        at = self._skip_whitespace(at+9)
    
        value = ''
    
        while at < self.length:
    
            n = self.file[at]
            if n in integer:
                value = value + n
            else:
                break
    
            at = at + 1
    
        # Return the dictionary and the location of the xref table
        return trailer_dict, int(value)
    
    def _read_integer(self, offset, end):
    
        value = self.file[offset]
        at = offset + 1
        while at < end:
        
            n = self.file[at]
            if n in integer:
                value = value + n
            else:
                break
            
            at = at + 1
        
        return at, int(value)
    
    def _read_xref(self, offset, end = None):
        """used, free = _read_xref(self, offset, end = None)
        
        Read the cross reference table found at the offset given in the file
        and ending at the end specified.
        
        The used and free dictionaries returned take the form:
        
            { object_number : (generation, offset), ... }
        
        """
        if end is None: end = self.length
        
        used = {}
        free = {}
    
        next = []
    
        at = offset
        at = self._skip_whitespace(at)
        at, start = self._read_integer(at, end)
        at = self._skip_whitespace(at)
        at, number = self._read_integer(at, end)
        at = self._skip_whitespace(at)
        
        item = start
        
        # Read items until we either reach the end of the xref table or
        # we have read the given number of items.
        #while at < end and number > 0:
        while number > 0:
    
            c = self.file[at]
    
            if c == 'f':
    
                if len(next) != 2:
                    raise PDFError, 'Problem in xref table at %s' % hex(at)
    
                at = at + 1
    
                free[item] = next
                next = []
                item = item + 1
                number = number - 1
    
            elif c == 'n':
    
                if len(next) != 2:
                    raise PDFError, 'Problem in xref table at %s' % hex(at)
    
                at = at + 1
    
                used[item] = next
                next = []
                item = item + 1
                number = number - 1
    
            # Integer
            elif c in integer:
            
                if len(next) < 2:
                
                    at, value = self._read_integer(at, end)
    
                    # Append value to the list
                    next.append(value)
                
                else:
                
                    # An integer after a pair of integers: the last pair must be a subsection.
                    item = next[0]
                    number = next[1]
                    
                    at, value = self._read_integer(at, end)
                    
                    # Append value to the list
                    next.append(value)
                
            else:

                # End of table - can't guarantee that the xref table
                # will immediately precede the trailer. There might be
                # an old trailer after it, but searching for "trailer"
                # from the start of the xref table isn't reliable.
                raise PDFError, 'Unexpected element in xref table at %s' % hex(at)
            
            at = self._skip_whitespace(at)
    
        return start, number, used, free

    def _read_linearized(self):
    
        # Starting at the beginning of the file, skip the initial
        # version declaration and binary data.
        version = self.document_version()
        
        try:
            if float(version) > 1.4:
                raise ValueError
        except ValueError:
            raise PDFError, "Unsupported PDF version: %s" % version
        
        i = 1 + len("PDF-") + len(version)
        
        i = self._skip_whitespace(i)
        
        # We are now at the parameters following the document version.
        
        while self.file[i] == '%':
        
            i, comment = self._read_comment(i + 1)
        
        if self.file[i] in whitespace:
        
            i = self._skip_whitespace(i)
        
        # We should now be at document data which may contain linearization
        # parameters. Therefore, look for object and generation numbers
        # followed by the "obj" operator.
        
        # Use a list for the parameter stack required for operators.
        this_array = []
        
        # Search up to the end of the file. Note that the file may not
        # have been completely loaded.
        
        found = None
        
        while i < self.length:
        
            i, element = self._read_next(i, this_array)
            
            i = self._skip_whitespace(i)
            
            if isinstance(element, object):
            
                # We have found an object. Assume that it is a dictionary
                # containing linearization parameters.
                found = element
                break
            
            else:
            
                # Keep the value on the stack.
                this_array.append(element)
        
        if found is None:
        
            return None
        
        # Check the object to discover whether it contains a dictionary
        # defining the linearization parameters.
        if found.object == [] or type(found.object[0]) != types.DictType:
        
            return None
        
        d = found.object[0]
        
        if not d.has_key('Linearized'):
        
            return None
        
        # Copy useful information stored in the dictionary.
        
        if d.has_key('L'): self.length = d['L'] # File length
        if d.has_key('N'): self.number_of_pages = d['N']
        
        # Since this is a linearized document then this dictionary should
        # be followed by the cross reference table.
        i = self._skip_whitespace(i)
        
        # Record the cross reference table position.
        xref_pos = i
        
        # Look for the trailer.
        trailer_pos = string.find(self.file, "trailer", xref_pos)
        
        trailer_dict, false_xref_pos = self._read_trailer(trailer_pos + 7)

        return trailer_pos, trailer_dict, xref_pos
    
    def _trailer_info(self, backwards = 1):
        """dict = _trailer_info(self, backwards = 1)
        
        Return the trailer dictionary of the document which contains the
        location of the cross-reference table. This sets up an internal copy
        of the dictionary for later use, although it isn't necessary to do
        this.
        
        By default, the trailer is searched for from the end of the file.
        If backwards equals zero then it is searched for from the beginning
        of the file.
        
        Example: dict = doc._trailer_info()
        """
        if backwards == 1:
            trailer_pos = string.rfind(self.file, 'trailer')
        else:
            trailer_pos = string.find(self.file, 'trailer')
    
    #    print hex(trailer_pos)
    
        trailer_dict, xref_pos = self._read_trailer(trailer_pos + 7)

        return trailer_pos, trailer_dict, xref_pos

    # _trailer_info must be called before _xref_info()
    
    def _xref_info(self, xref_pos):
        """Return the contents of the cross reference table.

        Example: objects_in_use, free_space = doc._xref_info()
        """

        start, number, used, free = \
            self._read_xref(xref_pos + 4) #, self.trailer_pos)

        return used, free
    
    def _find_in_used(self, obj, gen):

        for key, value in self.used.items():
        
            if obj == key and gen == value[1]:
            
                # Read the object number and generation number from the object's
                # location in the file.
                
                at, this_obj = self._read_integer(value[0], self.length)
                gen_at = self._skip_whitespace(at)
                
                if this_obj != obj:
                
                    raise PDFError, \
                        "Object number %i at %s disagrees with that the " + \
                        "number %i from the cross reference table." % \
                            (this_obj, hex(value[0]), obj)
                
                at, this_gen = self._read_integer(gen_at, self.length)
                at = self._skip_whitespace(at)
                
                if this_gen != gen:
                
                    raise PDFError, \
                        "Generation number %i at %s disagrees with the " + \
                        "number %i given in the cross reference table." % \
                            (this_gen, hex(gen_at), gen)
                
                at, element = self._read_next(at, [obj, gen])
                
                return element
        
        return None
    
    # *Required* before any page lookup is done

    def _read_catalog(self):
    
        """cat = _read_catalog(self)
        
        Read the document's catalog(ue). This is necessary before any
        page lookup is attempted. This method will read the document
        trailer's dictionary and cross-reference table if required.

        Example: cat = doc._read_catalog()
        """
        # Read the trailer to find the /Root object

        root = self.trailer_dict['Root']

        catalog = self._dereference(root)

        return catalog
    
    # Find an inherited attribute: move up the document structure until
    # the attribute is found or we reach the top.

    def _inherit(self, tree, key):

        while tree.has_key(key)==0 and tree.has_key('Parent')==1:

            ref = tree['Parent']
            tree = self._dereference(ref)

        if tree.has_key(key) == 0:

            return

        else:

            return tree[key]

    # Dereference an entry in an array or dictionary

    def _dereference(self, element):

        # Reduce to the simplest description

        if isinstance(element, reference):

            element = self._find_in_used(element.obj, element.gen).object

        if isinstance(element, object):

            element = element.object

        if type(element) == types.ListType:

            if len(element) == 1:
                return element[0]
            else:
                return element
        else:

            return element

        return element

    def _collect_dict(self, dict):

        new_dict = {}

        for key in dict.keys():

            # Dereference if required
            element = self._dereference(dict[key])
            # Dictionary
            if type(element) == types.DictionaryType:

                new_dict[key] = self._collect_dict(element)

            else:
                new_dict[key] = element

        return new_dict

    def _read_document(self):
    
        """_read_document(self)
        
        Prepare the document for access by finding the document trailer
        and cross reference table.
        """
        
        self.trailer_dict = {}
        
        # Check whether the document is "linearized".
        linear_info = self._read_linearized()
        
        if linear_info is not None:
        
            trailer_pos, trailer_dict, xref_pos = linear_info
            self.is_linearized = 1
        
        else:
        
            # Look for the trailer at the end of the file.
            backwards_info = self._trailer_info(backwards = 1)
            
            trailer_pos, trailer_dict, xref_pos = backwards_info
            self.is_linearized = 0
        
        # Look for a valid trailer dictionary, containing a "Root" entry,
        # and a valid cross reference table.
        
        if trailer_dict.has_key("Root"):
        
            self.trailer_dict = trailer_dict
            self.trailer_pos = trailer_pos
        
        if xref_pos != 0:
        
            # Examine any cross reference tables present.
            self.used, self.free = self._xref_info(xref_pos)
            self.xref_pos = xref_pos
        
        if trailer_dict.has_key("Prev"):
        
            # Examine any previous cross reference dictionaries.
        
            used, free = self._xref_info(trailer_dict["Prev"])
            
            # Merge the used and free dictionaries.
            for key, value in used.items():
            
                if not self.used.has_key(key):
                    self.used[key] = value
            
            for key, value in free.items():
            
                if not self.free.has_key(key):
                    self.free[key] = value
        
        # Retrieve the document's catalogue.
        self.catalog = self._read_catalog()
    
    def _write_document(self, fh, linearized):
    
        # Write the PDF version to the file as a comment.
        fh.write("%%PDF-%s\r" % self.version)
        
        # Create the trailer from the objects in the file.
        trailer, xref_table, catalog = self._create_structure()
        
        if self.linearized:
        
            self._write_linearized(trailer)
            self._write_xref(xref_table)
            self._write_catalog(catalog)
        
        # Write the objects to the file.
        
        if not self.linearized:
        
            self._write_linearized(trailer)
            self._write_xref(xref_table)
            self._write_catalog(catalog)
        
        fh.write("%%EOF\r")


class Page(Abstract):

    """Page(Abstract)
    
    page = Page(document, page_dictionary)
    
    Create a page object to represent a given page in a document.
    The document parameter is the PDFDocument object from which the
    page_dictionary dictionary was obtained for a given page.
    
    These objects are usually created by the PDFDocument.read_page
    method.
    
    Useful methods:
    
        contents = read_contents(self)
    
    """
    
    def __init__(self, document, page_dictionary):
    
        # Keep a reference to the document as we will need to
        # use it to retrieve information required to read the page
        # contents.
        self.document = document
        
        # Record the page dictionary.
        self.page_dict = page_dictionary
        
        # Find required items and cache them for later use.
        self.required = {}
        
        # Read the page type.
        self.required["Type"] = \
            self.document._dereference(self.page_dict["Type"])
        
        # Fetch the MediaBox.
        self.required["MediaBox"] = \
            self.document._dereference(
                self.document._inherit(self.page_dict, 'MediaBox')
                )
        
        # Fetch the Parent and convert it into a Pages object.
        self.required["Parent"] = \
            Pages(
                self.document, 
                self.document._dereference(self.page_dict["Parent"])
                )
        
        # Fetch the Resources.
        resources = \
            self.document._dereference(
                self.document._inherit(self.page_dict, 'Resources')
                )
        
        # Collect all the resources in the Resources entry into one dictionary.
        self.required["Resources"] = self.document._collect_dict(resources)
        
        # Fetch the Contents (if present). This is not a required property
        # but it is useful to process this item here.
        
        contents_element = self.document._inherit(self.page_dict, 'Contents')
        
        if contents_element is not None:
        
            self.required["Contents"] = \
                self._read_contents_element(contents_element)
    
    def _read_contents_element(self, contents_element):
    
        if isinstance(contents_element, reference):
        
            # A reference to an object rather than a list. Enclose it in
            # a list for processing as for an array (list) of references.
            contents_element = [self.document._dereference(contents_element)]
        
        contents_list = map(
            lambda item: self.document._dereference(item), contents_element
            )
        
        contents_output = []
        
        for item in contents_list:
        
            # Each item in the contents list contains a dictionary with
            # various entries describing the stream and the stream itself.
            
            # The length of the stream is given in the dictionary.
            length = self.document._dereference(item[0].get('Length', 0))
            
            # A list of the filters to be used to process the stream is also
            # given.
            filters = self.document._dereference(item[0].get('Filter', []))
            
            # The second entry contains the stream. We check that the stream
            # start and end positions determined when the file was read agree
            # with the length provided by the dictionary entry.
            stream = self.document._dereference(item[1])
            
            start = stream.start
            end   = stream.end
            
            #print length, start, end, end - start
            #
            #if length != (end - start):
            #
            #    raise PDFError, "Problem found in reading stream at %x (" % \
            #                    start + \
            #                    "I may have made a mistake when reading the file)."
            
            # Read the stream contents.
            
            contents = self.document.file[start:start + length]
            
            if isinstance(filters, name):
            
                filters = [filters]
            
            # Examine the Contents dictionary
            for filter in filters:
            
                # print filter.name
                if filter.name == '_asciihexdecode':
                
                    contents = self._asciihexdecode(contents)
                
                elif filter.name == '_ascii85decode' or filter.name == 'ASCII85Decode':
                
                    contents = self._ascii85decode(contents)
                
                elif filter.name == 'FlateDecode':
                
                    contents = zlib.decompress(contents)
                
                else:
                    raise PDFError, 'Unknown Filter method: %s' % filter.name
            
            contents_output.append(contents)
        
        return string.join(contents_output, "")
    
    def __getitem__(self, key):
    
        # Check whether this item has been cached.
        if self.required.has_key(key):
        
            return self.required[key]
        
        # Try to find the requested key from the page dictionary, using
        # the document as appropriate.
        
        # Retrieve a value from the page dictionary or an ancestor, if it
        # is an inherited property.
        
        value = self.document._inherit(self.page_dict, key)
        
        if value is None:
        
            raise KeyError, key
        
        # Dereference the value provided; this can be done whether the
        # value is an indirect reference or not.
        
        return self.document._dereference(value)
    
    def keys(self):
    
        k = self.required.keys()
        return k + filter(lambda x: x not in k, self.page_dict.keys())
    
    def values(self):
    
        k = self.required.values()
        return k + filter(lambda x: x not in k, self.page_dict.values())
    
    def items(self):
    
        k = self.required.items()
        return k + filter(lambda x: x not in k, self.page_dict.items())
    
    def __getattr__(self, attr):
    
        if attr == "__call__" or attr == "__repr__":
        
            raise AttributeError, attr
        
        try:
        
            return self.__getitem__(attr)
        
        except KeyError:
        
            raise AttributeError, attr
    
    def read_contents(self):
    
        """content = read_contents(self)
        
        Return a PDFContents object containing the necessary information
        required to display the page.
        """
    
        return PDFContents(self)


class Pages(Abstract):

    """Pages(Abstract)
    
    pages = Pages(document, pages_dictionary)
    
    Create a pages object to represent a collection of pages in a document.
    The document parameter is the PDFDocument object from which the
    pages_dictionary dictionary was obtained for a given set of pages.
    
    These objects can be used to encapsulate pages dictionaries found by
    looking at the parents of Page objects.
    """
    
    def __init__(self, document, pages_dictionary):
    
        # Keep a reference to the document as we will need to
        # use it to retrieve information required to read the page
        # contents.
        self.document = document
        
        # Record the page dictionary.
        self.pages_dict = pages_dictionary
        
        # Find required items and cache them for later use.
        self.required = {}
        
        # Read the pages type.
        self.required["Type"] = \
            self.document._dereference(self.pages_dict["Type"])
        
        # Read the Kids property.
        self.required["Kids"] = self.pages_dict["Kids"]
        
        # Read the Count property (number of pages below this object).
        self.required["Count"] = self.pages_dict["Count"]
        
        # Fetch the Parent and convert it into a Pages object.
        # Every Pages object except the root Pages object has a Parent
        # property.
        
        if self.pages_dict.has_key("Parent"):
        
            self.required["Parent"] = \
                Pages(
                    self.document, 
                    self.document._dereference(self.pages_dict["Parent"])
                    )
    
    def __getitem__(self, key):
    
        # Check whether this item has been cached.
        if self.required.has_key(key):
        
            return self.required[key]
        
        # Try to find the requested key from the page dictionary, using
        # the document as appropriate.
        
        # Retrieve a value from the page dictionary or an ancestor, if it
        # is an inherited property.
        
        value = self.document._inherit(self.pages_dict, key)
        
        if value is None:
        
            raise KeyError, key
        
        # Dereference the value provided; this can be done whether the
        # value is an indirect reference or not.
        
        return self.document._dereference(value)
    
    def keys(self):
    
        k = self.required.keys()
        return k + filter(lambda x: x not in k, self.pages_dict.keys())
    
    def values(self):
    
        k = self.required.values()
        return k + filter(lambda x: x not in k, self.pages_dict.values())
    
    def items(self):
    
        k = self.required.items()
        return k + filter(lambda x: x not in k, self.pages_dict.items())
    
    def __getattr__(self, attr):
    
        if attr == "__call__" or attr == "__repr__":
        
            raise AttributeError, attr
        
        try:
        
            return self.__getitem__(attr)
        
        except KeyError:
        
            raise AttributeError, attr



class command:

    def __init__(self, command):

        self.command = command


# Define a graphics state class to contain the dictionaries created by the
# PDFContents class.

class GraphicsState:

    def __init__(self, graphics_state):
    
        # Make a copy of the dictionary to avoid problems with mutable
        # objects.
        
        self.graphics_state = graphics_state.copy()
    
    def __getitem__(self, key):
    
        return self.graphics_state[key]
    
    def get(self, key, default = None):
    
        return self.graphics_state.get(key, default)
    
    def keys(self):
    
        return self.graphics_state.keys()
    
    def values(self):
    
        return self.graphics_state.values()
    
    def items(self):
    
        return self.graphics_state.items()

class PushGS:

    def __init__(self, graphics_state):
    
        # Make a copy of the dictionary to avoid problems with mutable
        # objects.
        
        self.graphics_state = graphics_state.copy()

class PopGS:

    def __init__(self, graphics_state):
    
        # Make a copy of the dictionary to avoid problems with mutable
        # objects.
        
        self.graphics_state = graphics_state.copy()


# Define the characters used to start commands in stream objects for the
# benefit of the PDFContents class.

commands = string.letters+'*"'+"'"

class PDFContents(Abstract):

    """PDFContents(Abstract)
    
    Class used to interpret and render content streams.
    This is achieved by creating an instance for a particular MediaBox,
    Resources dictionary and content stream obtained from the
    Page._read_contents method.

    Example:

    doc = PDFDocument("MyFile.pdf")
    ...
    page = doc.read_page(123)
    co = PDFContents(page)
    
    Useful attributes:
    
        self.contents   # contains the objects found in the page whose
                        # contents this object represents.
    
    """
    def __init__(self, page):
    
        # Keep a reference to the page.
        self.page = page
        
        #self.mediabox = page.MediaBox
        #self.resources = page.Resources
        # Determine the media dimensions.
        self.mediabox = page.MediaBox
        
        # Define the graphics origin.
        self.origin = point(
            min(self.mediabox[0], self.mediabox[2]),
            min(self.mediabox[1], self.mediabox[3])
            )
        
        # Set the current point to the origin.
        self.current_point = self.origin
        
        # Set the rendering matrix to the unit matrix.
        self.rendering_matrix = identity(3)
        
        # Set the current transformation matrix to the unit matrix.
        self.CTM = identity(3)
        
        # Define a graphics state and a stack.
        self.graphics_state = \
        {
            "flatness": 0,
            # line end caps: 0 butt, 1 round end, 2 squared end
            "linecap": 0,
            # line dash pattern: solid line
            "linedash": ([], 0),
            # line join type: 0 mitre, 1 round, 2 bevel
            "linejoin": 0,
            # line width: 0 thinnest line on device
            "linewidth": 1,
            # mitre limit: >= 1
            "miterlimit": 10,
            # stroke adjust: true/false
            "stroke adjust": boolean("true"),
            # overprint strokes: other separations are left unchanged (true),
            #                    other separations are overwritten (false)
            "stroke overprint": boolean("false"),
            # overprint fills: as overprint strokes but for fills
            "fill overprint": boolean("false"),
            # overprint mode: 0 (see p328 of the PDF 1.3 specification)
            "overprint mode": 0,
            # smoothness: value in the range [0, 1] (default value unknown)
            "smoothness": 0,
            
            # Colour properties
            
            # Fill colour space
            "fill color space": "DeviceGray",
            
            # Use a dictionary to define a fill colour for each colour space
            # used.
            "fill color": {
                "DeviceGray": 0,
                "DeviceRGB": [0, 0, 0],
                "DeviceCMYK": [0, 0, 0, 0]
            },
            
            # Stroke colour space
            "stroke color space": "DeviceGray",
            
            # Use a dictionary to define a stroke colour for each colour space
            # used.
            "stroke color": {
                "DeviceGray": 0,
                "DeviceRGB": [0, 0, 0],
                "DeviceCMYK": [0, 0, 0, 0]
            }
        }
        self.graphics_state_stack = []
        
        # Read the contents.
        self.contents = []
        
        self.file = page.Contents
        
        self.length = len(self.file)
        
        self.contents = self._read_contents()
    
    def _read_next(self, offset, this_array):
    
        c = self.file[offset]
        
        # Comment
        if c == '%':
        
            # print 'comment'
            return self._read_comment(offset+1)
        
        # Boolean
        if c == 't':
        
            if self.file[offset:offset+4] == 'true':
            
                # print 'true'
                return offset + 4, true
        
        if c == 'f':
        
            if self.file[offset:offset+5] == 'false':
            
                # print 'false'
                return false, offset + 5
        
        # Integer or Real
        if c in integer:
        
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
            
            if is_real == 0:
                # print 'integer'
                return offset, int(value)
            else:
                # print 'real'
                return offset, float(value)
        
        if c in real:
        
            value = c
            offset = offset + 1
            while offset < self.length:
            
                n = self.file[offset]
                if n in real:
                    value = value + n
                else:
                    break
                
                offset = offset + 1
            
            return offset, float(value)
        
        # Name
        if c == '/':
        
            # print 'name'
            return self._read_name(offset+1)
        
        # String
        if c == '(':
        
            # print 'string'
            return self._read_string(offset+1)
        
        # Hexadecimal string or dictionary
        if c == '<':
        
            if self.file[offset+1] != '<':
            
                    # print 'hexadecimal string'
                return self._read_hexadecimal(offset+1)
            
            else:
                return self._read_dictionary(offset+2)
        
        # Array
        if c == '[':
        
            return self._read_array(offset+1)
        
        # null
        if c == 'n':
        
            if self.file[offset:offset+4] == 'null':
            
                # print 'null'
                return offset + 4, null
        
#        # Stream
#        if c == 's':
#    
#            at, element = self._read_stream(offset+6)
        
        # None of the above
        
        # Must be a command
        # Read until next whitespace
        at = offset
        while self.file[at] in commands:
        
            at = at + 1
        
        element = command(self.file[offset:at])
        
        return at, element
    
    def _read_contents(self):
    
        """Read a content stream.
        
        For example, assuming that "doc" is an instance of PDFDocument:
        
        page = doc.read_page(123)
        contents = page.read_contents()
        # contents._read_contents() is called by the PDFContents.__init__ method.
        page_contents = contents.contents
        """
        if self.page.MediaBox == None:
            print 'No MediaBox defined.'
            return []
        
        if self.page.Resources == None:
            print 'No associated resources.'
            return []
        
        if self.file == None:
            print 'No content stream to render.'
            return []
        
        # The items found while reading the contents
        items = []
        
        # The contents generated from the initial raw contents.
        contents = []
        
        at = self._skip_whitespace(0)
        
        while at < self.length:
        
            next, item = self._read_next(at, items)
            
            # if isinstance(item, command): print at, self.length, item.command
            
            if isinstance(item, command):
            
                com = item.command
                
                if com == 'q':
                
                    # Save graphics state on the graphics state stack.
                    self.graphics_state_stack.append(self.graphics_state)
                    contents.append(PushGS(self.graphics_state))
                
                elif com == 'Q':
                
                    # Restore the graphics state from the graphics state
                    # stack.
                    self.graphics_state = self.graphics_state_stack.pop()
                    contents.append(PopGS(self.graphics_state))
                
                elif com == 'cm':
                
                    # Modify the coordinate transformation matrix
                    # (for user to device space transformations) by
                    # concatenating a matrix defined by the given six
                    # numbers.
                    
                    render_matrix = matrix(
                        [items[-6:-4]+[0], items[-4:-2]+[0], items[-2:]+[1]]
                        )
                    
                    items = items[:-6]
                    
                    self.CTM = self.CTM * render_matrix
                
                elif com == 'i':
                
                    # Set the flatness parameter.
                    self.graphics_state["flatness"] = items.pop()
                
                elif com == 'J':
                
                    # Set the line end cap parameter.
                    self.graphics_state["linecap"] = items.pop()
                
                elif com == 'd':
                
                    # Set the line dash pattern.
                    phase = items.pop()
                    dash_array = items.pop()
                    
                    self.graphics_state["linedash"] = (dash_array, phase)
                
                elif com == 'j':
                
                    # Set the line join parameter.
                    self.graphics_state["linejoin"] = items.pop()
                
                elif com == 'w':
                
                    # Set the line width.
                    self.graphics_state["linewidth"] = items.pop()
                
                elif com == 'M':
                
                    # Set the mitre limit.
                    self.graphics_state["miterlimit"] = items.pop()
                
                elif com == 'gs':
                
                    # Use the generic graphics state operator to set a
                    # parameter in the general graphics state using an
                    # extended graphics state dictionary.
                    self.generic_graphics_state(items.pop())
                
                # Colour/Color operators
                
                elif com == 'g':
                
                    # Set the colour space to DeviceGray and set the grey
                    # tint for filling paths.
                    self.graphics_state["fill color space"] = "DeviceGray"
                    self.graphics_state["fill color"]["DeviceGray"] = \
                        items.pop()
                
                elif com == 'G':
                
                    # Set the colour space to DeviceGray and set the grey
                    # tint for path strokes.
                    self.graphics_state["stroke color space"] = "DeviceGray"
                    self.graphics_state["stroke color"]["DeviceGray"] = \
                        items.pop()
                
                elif com == 'rg':
                
                    # Set the colour space to DeviceRGB and set the colour
                    # for filling paths.
                    self.graphics_state["fill color space"] = "DeviceRGB"
                    self.graphics_state["fill color"]["DeviceRGB"] = items[-3:]
                    
                    items = items[:-3]
                
                elif com == 'RG':
                
                    # Set the colour space to DeviceRGB and set the colour
                    # for path strokes.
                    self.graphics_state["stroke color space"] = "DeviceRGB"
                    self.graphics_state["stroke color"]["DeviceRGB"] = \
                        items[-3:]
                    
                    items = items[:-3]
                
                elif com == 'k':
                
                    # Set the colour space to DeviceCMYK and set the colour
                    # for filling paths.
                    self.graphics_state["fill color space"] = "DeviceCMYK"
                    self.graphics_state["fill color"]["DeviceCMYK"] = items[-4:]
                    
                    items = items[:-4]
                
                elif com == 'K':
                
                    # Set the colour space to DeviceCMYK and set the colour
                    # for path strokes.
                    self.graphics_state["stroke color space"] = "DeviceCMYK"
                    self.graphics_state["stroke color"]["DeviceCMYK"] = \
                        items[-4:]
                    
                    items = items[:-4]
                
                elif com == 'cs':
                
                    # Set the colour space to use for filling paths.
                    space = items.pop()
                    
                    # The "space" variable should contain a name object.
                    self.graphics_state["fill color space"] = space.name
                
                elif com == 'CS':
                
                    # Set the colour space to use for path strokes.
                    space = items.pop()
                    
                    # The "space" variable should contain a name object.
                    self.graphics_state["stroke color space"] = space.name
                
                elif com == 'sc':
                
                    # Set the colour for filling paths.
                    
                    # The items list will be modified appropriately by the
                    # following method.
                    
                    items = self.set_colour(
                        items, self.graphics_state["fill color space"],
                        "fill color"
                        )
                
                elif com == 'SC':
                
                    # Set the colour for path strokes.
                    
                    # The items list will be modified appropriately by the
                    # following method.
                    
                    items = self.set_colour(
                        items, self.graphics_state["stroke color space"],
                        "stroke color"
                        )
                
                elif com == 'scn':
                
                    # Set the colour and/or pattern for filling paths.
                    
                    # Shorthand
                    fcs_name = self.graphics_state["fill color space"]
                    
                    if fcs_name == "Pattern":
                    
                        # Read the last item on the stack.
                        pattern_name = items.pop()
                        
                        # Find the pattern in the page's Resources dictionary.
                        pattern = self.page.Resources[pattern_name]
                        
                        if pattern["PatternType"] == 1:
                        
                            if pattern["PaintType"] == 1:
                            
                                # No colour components should be specified.
                                pass
                            
                            elif pattern["PaintType"] == 2:
                            
                                # Use the colour components to specify the
                                # colour.
                                
                                items = self.set_colour(
                                    items,
                                    self.graphics_state["fill color space"],
                                    "fill color"
                                    )
                        
                        elif pattern["PatternType"] == 2:
                        
                            # No colour components should be specified.
                            pass
                    
                    elif fcs_name == "Separation":
                    
                        # Set the tint using a single colour component.
                        # [Not implemented.]
                        items.pop()
                    
                    elif fcs_name == "ICCBased":
                    
                        # Set the fill colour using the colour components
                        # given.
                        # [Not implemented.]
                        pass
                    
                    else:
                    
                        # Fall back on the support method for the 'sc'
                        # command.
                        
                        items = self.set_colour(
                            items, self.graphics_state["fill color space"],
                            "fill color"
                            )
                
                elif com == 'SCN':
                
                    # Set the colour and/or pattern for path strokes.
                    
                    # Shorthand
                    scs_name = self.graphics_state["stroke color space"]
                    
                    if scs_name == "Pattern":
                    
                        # Read the last item on the stack.
                        pattern_name = items.pop()
                        
                        # Find the pattern in the page's Resources dictionary.
                        pattern = self.page.Resources["Pattern"][pattern_name]
                        
                        if pattern["PatternType"] == 1:
                        
                            if pattern["PaintType"] == 1:
                            
                                # No colour components should be specified.
                                pass
                            
                            elif pattern["PaintType"] == 2:
                            
                                # Use the colour components to specify the
                                # colour.
                                
                                items = self.set_colour(
                                    items,
                                    self.graphics_state["fill color space"],
                                    "fill color"
                                    )
                        
                        elif pattern["PatternType"] == 2:
                        
                            # No colour components should be specified.
                            pass
                    
                    elif scs_name == "Separation":
                    
                        # Set the tint using a single colour component.
                        # [Not implemented.]
                        items.pop()
                    
                    elif scs_name == "ICCBased":
                    
                        # Set the stroke colour using the colour components
                        # given.
                        # [Not implemented.]
                        pass
                    
                    else:
                    
                        # Fall back on the support method for the 'SC'
                        # command.
                        
                        items = self.set_colour(
                            items, self.graphics_state["stroke color space"],
                            "stroke color"
                            )
                
                elif com == 'ri':
                
                    # Colour rendering intent
                    # [Not implemented (see p333 of PDF 1.3 specification).]
                    items.pop()
                
                # Path objects
                
                elif com == 'm':
                
                    # Move the current point to a new position.
                    # (Start of a new path.)
                    
                    # Before reading this path, store the graphics state
                    # in the contents list for renderers to use.
                    #contents.append(GraphicsState(self.graphics_state))
                    
                    # Read the path information (re-reading this command
                    # and supplying the necessary operands).
                    #operands = items[-2:]
                    
                    items, path, next = self.read_path(at, items)
                    
                    contents.append(path)
                    
                    #items = items[:-2]
                
                elif com == 're':
                
                    # Draw a rectangle.
                    
                    # Before reading the rectangle, store the graphics state
                    # in the contents list for renderers to use.
                    #contents.append(GraphicsState(self.graphics_state))
                    
                    # Read the path information (re-reading this command
                    # and supplying the necessary operands).
                    #operands = items[-4:]
                    
                    items, path, next = self.read_path(at, items)
                    
                    contents.append(path)
                    
                    #items = items[:-4]
                
                # Objects
                
                elif com == 'BT':
                
                    # Text information is given.
                    
                    # Before reading this text, store the graphics state
                    # in the contents list for renderers to use.
                    #contents.append(GraphicsState(self.graphics_state))
                    
                    #end = string.find(self.file, 'ET', at)
                    
                    # Read from the content following this command.
                    text_contents, next = self.read_textobject(next, 'ET')
                    contents.append(text_contents)
                    #at = end + 2
                
                elif com == 'BI':
                
                    # In-line image object is given.
                    
                    # Read from the content following this command.
                    end = string.find(self.file, 'EI', next)
                    # self.read_inline_imageobject(at, end)
                    next = end + 2
                
                else:
                
                    # print 'Command', com, 'not known.'
                    pass
            
            else:
            
                # A command has not been found so this must be a parameter.
                items.append(item)
            
            # Skip any whitespace following the current offset into the content.
            at = self._skip_whitespace(next)
        
        # Return the contents found.
        
        return contents
    
    def generic_graphics_state(self, name):
    
        # Find the entry in the Resources dictionary corresponding to the
        # name supplied and set the appropriate parameter in the general
        # graphics state.
        
        # Find the "ExtGState" entry in the page's Resources dictionary.
        extgstate = self.page.Resources["ExtGState"]
        
        # Read a dictionary of parameters to change and their new values.
        
        # [If the name is not in the dictionary then a KeyError will be
        #  raised. We may want to catch this.]
        
        changes = extgstate[name.name]
        
        add_state = {}
        
        for key, value in changes.items():
        
            if key == 'SA':
            
                # Stroke adjustment
                add_state["stroke adjust"] = value
            
            elif key == 'OP':
            
                # Overprint for strokes
                add_state["stroke overprint"] = value
            
            elif key == 'op':
            
                # Overprint for fills
                add_state["fill overprint"] = value
            
            elif key == 'OPM':
            
                # Overprint mode
                add_state["overprint mode"] = value
            
            # Various missing commands from p328-329 of the PDF 1.3
            # specification.
            
            elif key == 'SM':
            
                # Smoothness
                add_state["smoothness"] = value
        
        # Copy the contents of the add_state dictionary into the graphics
        # state, taking into account any restrictions on values.
        
        # Ensure that the fill overprint parameter is set if the stroke
        # overprint parameter is defined.
        if add_state.has_key("OP") and not add_state.has_key("op"):
        
            add_state["op"] = add_state["OP"]
        
        for key, value in add_state.items():
        
            self.graphics_state[key] = value
    
    def set_colour(self, items, colour_space, colour_type):
    
        """set_colour(self, items, colour_space, colour_type)
        
        Set the colour (fill or stroke) in the colour space given using
        the relevant number of parameters from the items list.
        
        The items list will be modified by this method.
        """
        
        # Shorthand
        
        if isinstance(colour_space, name):
        
            cs_name = colour_space.name
        
        else:
        
            cs_name = colour_space
        
        if cs_name == "DeviceGray":
        
            # Expect only one operand.
            self.graphics_state[colour_type][cs_name] = items.pop()
        
        elif cs_name == "CalGray":
        
            # Expect only one operand.
            self.graphics_state[colour_type][cs_name] = items.pop()
        
        elif cs_name == "Indexed":
        
            # Expect only one operand.
            self.graphics_state[colour_type][cs_name] = items.pop()
        
        elif cs_name == "DeviceRGB":
        
            # Expect three operands.
            self.graphics_state[colour_type][cs_name] = items[-3:]
            items = items[:-3]
        
        elif cs_name == "CalRGB":
        
            # Expect three operands.
            self.graphics_state[colour_type][cs_name] = items[-3:]
            items = items[:-3]
        
        elif cs_name == "Lab":
        
            # Expect three operands.
            self.graphics_state[colour_type][cs_name] = items[-3:]
            items = items[:-3]
        
        elif cs_name == "DeviceCMYK":
        
            # Expect four operands.
            self.graphics_state[colour_type][cs_name] = items[-4:]
            items = items[:-4]
        
        elif cs_name == "CalCMYK":
        
            # Expect four operands.
            self.graphics_state[colour_type][cs_name] = items[-4:]
            items = items[:-4]
        
        else:
        
            # Unknown colour space.
            self.graphics_state[colour_type][cs_name] = items
            items = []
        
        return items
    
    def read_path(self, start, items):
    
        # Record the contents of the path.
        subpaths = []
        
        # Skip initial whitespace and read the path elements.

        # Path segment operators
        
        at = self._skip_whitespace(start)
        
        while at < self.length:
        
            next, item = self._read_next(at, items)
            
            if isinstance(item, command):
            
                com = item.command
                
                if com == 'm':
                
                    # Move the current point to a new position.
                    # (Start of a new subpath.)
                    
                    self.current_point = point(*items[-2:])
                    items = items[:-2]
                    
                    move = pdfpath.Move(self.current_point)
                    
                    # Read the subpath information, adding the move operation
                    # to the rest of that subpath. The items list is passed
                    # because parameters may be found when reading the
                    # subpath that will have to be used back at this level.
                    items, subpath, next = self.read_subpath(next, move, items)
                    
                    # Append the subpath to the list of subpaths.
                    subpaths.append(subpath)
                
                elif com == 're':
                
                    # Draw a rectangle.
                    
                    p = point(*items[-4:-2])
                    width, height = items[-2:]
                    
                    items = items[:-4]
                    
                    # Add the rectangle to the list of subpaths.
                    subpaths.append(
                        pdfpath.Rectangle(p, width, height)
                        )
                
                else:
                
                    # Not a list of path segments or a rectangle.
                    
                    # Leave the loop, maintaining the offset pointing
                    # to this command.
                    break
            
            else:
            
                # A command has not been found so this must be a parameter.
                items.append(item)
            
            # Skip any whitespace following the current offset into the content.
            at = self._skip_whitespace(next)
            
            #print "%i unused stack items" % len(items)
        
        # Path clipping operators
        
        clipping = []
        
        while at < self.length:
        
            next, item = self._read_next(at, items)
            
            if isinstance(item, command):
            
                com = item.command
                
                if com == 'W':
                
                    # Clip with the current path, using the non-zero winding
                    # rule to determine the regions inside the clipping path.
                    clipping.append(
                        pdfpath.Clip("non-zero")
                        )
                
                elif com == 'W*':
                
                    # Clip with the current path, using the even-odd winding
                    # rule to determine the regions inside the clipping path.
                    clipping.append(pdfpath.Clip("even-odd"))
                
                else:
                
                    # Not a clipping operator/command.
                    
                    # Leave the loop, maintaining the offset pointing
                    # to this command.
                    break
            
            else:
            
                # A command has not been found so this must be a parameter.
                items.append(item)
            
            # Skip any whitespace following the current offset into the content.
            at = self._skip_whitespace(next)
        
        # Path painting operators
        
        painting = []
        
        while at < self.length:
        
            next, item = self._read_next(at, items)
            
            if isinstance(item, command):
            
                com = item.command
                
                if com == 'n':
                
                    # End the path.
                    at = next
                    break
                
                elif com == 'S':
                
                    # Stroke the path.
                    painting.append(pdfpath.Stroke())
                    at = next
                    break
                
                elif com == 's':
                
                    # Close then stroke the path.
                    painting.append(pdfpath.Close())
                    painting.append(pdfpath.Stroke())
                    at = next
                    break
                
                elif com == 'f':
                
                    # Fill the path using the non-zero winding rule.
                    painting.append(pdfpath.Fill("non-zero"))
                    at = next
                    break
                
                elif com == 'F':
                
                    # Fill the path using the non-zero winding rule.
                    painting.append(pdfpath.Fill("non-zero"))
                    at = next
                    break
                
                elif com == 'f*':
                
                    # Fill the path using the even-odd winding rule.
                    painting.append(pdfpath.Fill("even-odd"))
                    at = next
                    break
                
                elif com == 'B':
                
                    # Fill and stroke the path using the non-zero winding rule.
                    # Equivalent to q f Q S
                    painting.append(pdfpath.Fill("non-zero"))
                    painting.append(pdfpath.Stroke())
                    at = next
                    break
                
                elif com == 'b':
                
                    # Close, fill and stroke the path using the non-zero
                    # winding rule. Equivalent to h B
                    painting.append(pdfpath.Close())
                    painting.append(pdfpath.Fill("non-zero"))
                    painting.append(pdfpath.Stroke())
                    at = next
                    break
                
                elif com == 'B*':
                
                    # Even-odd fill and stroke.
                    # Equivalent to q f* Q S
                    painting.append(pdfpath.Fill("even-odd"))
                    painting.append(pdfpath.Stroke())
                    at = next
                    break
                
                elif com == 'b*':
                
                    # Close path, perform an even-odd fill and stroke.
                    # Equivalent to h B*
                    painting.append(pdfpath.Close())
                    painting.append(pdfpath.Fill("even-odd"))
                    painting.append(pdfpath.Stroke())
                    at = next
                    break
                
                elif com == 'sh':
                
                    # Gradient fill using a Shading dictionary.
                    name = items.pop()
                    painting.append(pdfpath.Gradient(name))
                    at = next
                    break
                
                else:
                
                    # print 'Command', com, 'not known.'
                    
                    # Leave the loop, maintaining the offset pointing
                    # to this command.
                    break
            
            else:
            
                # A command has not been found so this must be a parameter.
                items.append(item)
            
            # Skip any whitespace following the current offset into the content.
            at = self._skip_whitespace(next)
        
        # Return the items found.
        
        return items, pdfpath.Path(subpaths, clipping, painting), at
    
    def read_subpath(self, start, initial, items):
    
        """subpath = read_subpath(self, start, initial)
        
        Return a subpath found in the contents starting at the offset given.
        The initial value is the operation which initiated this subpath.
        """
        
        # Path segment operators
        
        # Record the contents of the subpath including the initial
        # operation/command which started the subpath.
        contents = [initial]
        
        at = self._skip_whitespace(start)

        while at < self.length:
        
            next, item = self._read_next(at, items)
            
            if isinstance(item, command):
            
                com = item.command
                
                if com == 'l':
                
                    # Construct a straight line from the current point to the
                    # new current point specified.
                    new_point = point(*items[-2:])
                    
                    contents.append(
                        pdfpath.Line(self.current_point, new_point)
                        )
                    
                    # Set the new current point.
                    self.current_point = new_point
                    
                    items = items[:-2]
                
                elif com == 'c':
                
                    # Construct a cubic Bezier curve from the current point to
                    # a new current point using two control points.
                    c1 = point(*items[-6:-4])
                    c2 = point(*items[-4:-2])
                    new_point = point(*items[-2:])
                    
                    contents.append(
                        pdfpath.Bezier(self.current_point, c1, c2, new_point)
                        )
                    
                    # Set the new current point.
                    self.current_point = new_point
                    
                    items = items[:-6]
                
                elif com == 'v':
                
                    # Construct a cubic Bezier curve from the current point to
                    # a new current point using the current point as the first
                    # control point and the given control point as the second
                    # control point.
                    
                    c1 = self.current_point
                    c2 = point(*items[-4:-2])
                    new_point = point(*items[-2:])
                    
                    contents.append(
                        pdfpath.Bezier(self.current_point, c1, c2, new_point)
                        )
                    
                    # Set the new current point.
                    self.current_point = new_point
                    
                    items = items[:-4]
                
                elif com == 'y':
                
                    # Construct a cubic Bezier curve from the current point to
                    # a new current point using the given control point as the
                    # first control point and the current point as the second
                    # control point.
                    
                    c1 = point(*items[-4:-2])
                    c2 = point(*items[-2:])
                    new_point = c2
                    
                    contents.append(
                        pdfpath.Bezier(self.current_point, c1, c2, new_point)
                        )
                    
                    # Set the new current point.
                    self.current_point = new_point
                    
                    items = items[:-4]
                
                elif com == 'h':
                
                    # Close the path.
                    contents.append(
                        pdfpath.Close()
                        )
                
                elif com == 'm':
                
                    # A new subpath has been found.
                    
                    # Leave the loop, maintaining the offset pointing
                    # to this command.
                    break
                
                elif com == 're':
                
                    # A rectangle has been found.
                    
                    # Leave the loop, maintaining the offset pointing
                    # to this command.
                    break
                
                else:
                
                    # print 'Command', com, 'not known.'
                    
                    # Leave the loop, maintaining the offset pointing
                    # to this command.
                    break

            else:
            
                # A command has not been found so this must be a parameter.
                items.append(item)

            # Skip any whitespace following the current offset into the content.
            at = self._skip_whitespace(next)
            
            #print "%i unused stack items" % len(items)
        
        # Return the items found.
        
        return items, pdfpath.Subpath(contents), at
    
    def read_textobject(self, start, ending):
    
        """read_textobject(self, start, end)
        
        Implemented commands:
        
            Tf      <name> <size> Tf    Set font name and size
            Td      <x> <y> Td          Move to next line (displace following
                                        text)
            TD      <x> <y> TD          Move to next line (displace following
                                        text and set leading to -y)
            Tj      <string> Tj         Write text
            '       <string> '          Write text
                                        (equivalent to T* <string> Tj)
            "                           Write text with character and word space
                                        attributes.
                                        Equivalent to <word space> Tw
                                        <char space> Tc <string> '
            TJ
            Tc      <length> Tc         Text character spacing
            Tw      <length> Tw         Word spacing
            Tz      <percentage> Tz     Set horizontal scale to a percentage
                                        of its current value
            TL      <leading> TL        Set leading
            Tr      <render> Tr         Set rendering mode
            Ts      <rise> Ts           Set text rise in text space units
            Tm      <a> <b> <c> <d> <e>
                    <f> Tm              Define text matrix and text line matrix.
                                        Reset current point and line start
                                        position to the origin.
            T*      T*                  Move to the start of the next line
                                        (equivalent to 0 Tl Td).
        """
        
        items = []
        
        self.text_character_spacing = 0         # T_c
        self.text_word_spacing = 0              # T_w
        self.text_horizontal_scale = 100        # T_h
        self.text_leading = 0                   # T_l
        # self.text_font is initially undefined   T_f
        # self.text_size is initially undefined   T_fs
        self.text_rendering_mode = 0            # T_mode
        self.text_rise = 0                      # T_rise
        
        # Define the text matrix - this transforms coordinates from text
        # space to user space.
        self.text_matrix = identity(3)              # T_m
        self.line_matrix = identity(3)              # T_LM
        self.text_rendering_matrix = identity(3)    # T_RM
        self.text_line_start = self.origin
        
        # Record the contents of the text object.
        contents = []
        
        at = self._skip_whitespace(start)

        while at < self.length:
        
            at, item = self._read_next(at, items)
            
            if isinstance(item, command):
            
                com = item.command
                
                if com == 'Tf':
                
                    # Specify font <name> <size> Tf
                    text_font, self.text_size = \
                        self.select_font(items[-2].name, items[-1])
                    items.pop()
                    items.pop()
                    
                    self.text_font = pdftext.Font(
                        text_font, self.text_size
                        )
                    
                    # Add the font details to the contents found.
                    contents.append(self.text_font)
                
                elif com == 'Td':
                
                    # Displace text <x> <y> (in points)
                    tx, ty = items[-2:]
                    items.pop()
                    items.pop()
                    
                    self.text_matrix = self.move_text_to(
                        tx, ty, self.text_matrix, self.line_matrix
                        )
                    
                    self.line_matrix = self.text_matrix.copy()
                    self.text_line_start = self.text_line_start + point(tx, ty)
                    self.current_point = self.text_line_start
                
                elif com == 'TD':
                
                    # Move to the next line (equivalent to setting the
                    # leading to the first value then displacing the text
                    # by the following values).
                    self.text_leading = -items[-1]
                    
                    tx, ty = items[-2:]
                    items.pop()
                    items.pop()
                    
                    self.text_matrix = self.move_text_to(
                        tx, ty, self.text_matrix, self.line_matrix
                        )
                    self.line_matrix = self.text_matrix.copy()
                    self.text_line_start = self.text_line_start + point(tx, ty)
                    self.current_point = self.current_point + point(tx, ty)
    
                elif com == 'Tj':
                
                    # Write text <string>
                    text = items[-1]
                    
                    items.pop()
                    
                    # Calculate the text rendering matrix.
                    self.text_rendering_matrix = \
                        self.calculate_rendering_matrix(
                            self.text_size, self.text_horizontal_scale,
                            self.text_rise, self.text_matrix, self.CTM
                            )
                    
                    # Create a text object.
                    text_object = pdftext.Text(
                        text,
                        self.text_font, self.text_size,
                        self.text_character_spacing, self.text_word_spacing,
                        self.text_rendering_matrix,
                        self.current_point
                        )
                    
                    # Add the text to the contents list.
                    contents.append(text_object)
                    
                    # Update the current point using the relevant text object
                    # method.
                    self.current_point = \
                        self.current_point + text_object.after()
                
                elif com == "'":
                
                    # Write text (equivalent to T* <string> Tj)
                    tx = 0
                    ty = self.text_leading
                    
                    self.text_matrix = self.move_text_to(
                        tx, ty, self.text_matrix, self.line_matrix
                        )
                    
                    text = items[-1]
                    
                    items.pop()
                    
                    # Calculate the text rendering matrix.
                    self.text_rendering_matrix = \
                        self.calculate_rendering_matrix(
                            self.text_size, self.text_horizontal_scale,
                            self.text_rise, self.text_matrix, self.CTM
                            )
                    
                    # Create a text object.
                    text_object = pdftext.Text(
                        text,
                        self.text_font, self.text_size,
                        self.text_character_spacing, self.text_word_spacing,
                        self.text_rendering_matrix,
                        self.current_point
                        )
                    
                    # Add the text to the contents list.
                    contents.append(text_object)
                    
                    # Update the current point using the relevant text object
                    # method.
                    self.current_point = \
                        self.current_point + text_object.after()
                
                elif com == '"':
                
                    # Write text with character and word space attributes.
                    # (Equivalent to <word space> Tw <char space> Tc <string> ')
                    text = items.pop()
                    self.text_character_spacing = items.pop()
                    self.text_word_spacing = items.pop()
                    tx = 0
                    ty = self.text_leading
                    
                    self.text_matrix = self.move_text_to(
                        tx, ty, self.text_matrix, self.line_matrix
                        )
                    
                    # Calculate the text rendering matrix.
                    self.text_rendering_matrix = \
                        self.calculate_rendering_matrix(
                            self.text_size, self.text_horizontal_scale,
                            self.text_rise, self.text_matrix, self.CTM
                            )
                    
                    # Create a text object.
                    text_object = pdftext.Text(
                        text,
                        self.text_font, self.text_size,
                        self.text_character_spacing, self.text_word_spacing,
                        self.text_rendering_matrix,
                        self.current_point
                        )
                    
                    # Add the text to the contents list.
                    contents.append(text_object)
                    
                    # Update the current point using the relevant text object
                    # method.
                    self.current_point = \
                        self.current_point + text_object.after()
                
                elif com == 'TJ':
                
                    # Show text string with individual character positioning.
                    # <array> TJ
                    
                    # Iterate through the items in the array, treating them
                    # as individual text strings and position information.
                    for item in items[-1]:
                    
                        if type(item) == types.StringType:
                        
                            # Text
                            
                            # Calculate the text rendering matrix.
                            self.text_rendering_matrix = \
                                self.calculate_rendering_matrix(
                                    self.text_size, self.text_horizontal_scale,
                                    self.text_rise, self.text_matrix, self.CTM
                                    )
                            
                            # Create a text object.
                            text_object = pdftext.Text(
                                item,
                                self.text_font, self.text_size,
                                self.text_character_spacing,
                                self.text_word_spacing,
                                self.text_rendering_matrix,
                                self.current_point
                                )
                            
                            # Add the text to the contents list.
                            contents.append(text_object)
                            
                            # Update the current point using the relevant text
                            # object method.
                            self.current_point = \
                                self.current_point + text_object.after()
                        
                        else:
                        
                            # Position information
                            
                            # Subtract the value from the coordinate used to
                            # specify the position of words on a line for the
                            # current writing direction; x for horizontal
                            # text, y for vertical text.
                            
                            # User space coordinates correspond to points
                            # and these units are in thousandths of an em,
                            # so we have to divide the current text size by
                            # a thousand and multiply it by this number.
                            amount = item
                            
                            # * Assume horizontal writing for the moment. *
                            
                            self.current_point.x = self.current_point.x - (
                                self.text_size * amount / 1000.0
                                )
                    
                    #self.position_text(items)
                    #print "TJ ---"
                    #print repr(items[-1])
                    #print "--- TJ"
                
                elif com == 'Tc':
                
                    # Text character spacing
                    self.text_character_spacing = items.pop()
                
                elif com == 'Tw':
                
                    # Word spacing
                    self.text_word_spacing = items.pop()
                
                elif com == 'Tz':
                
                    # Horizontal scaling
                    self.text_horizontal_scale = (items.pop() / 100.0)
                
                elif com == 'TL':
                
                    # Leading
                    self.text_leading = items.pop()
                
                elif com == 'Tr':
                
                    # Rendering mode
                    self.text_rendering_mode = items.pop()
                
                elif com == 'Ts':
                
                    # Text rise
                    self.text_rise = items.pop()
                
                elif com == 'Tm':
                
                    # Set text and line matrices.
                    self.text_matrix = matrix(
                        [items[-6:-4]+[0], items[-4:-2]+[0], items[-2:]+[1]]
                        )
                    
                    items = items[:-6]
                    
                    self.line_matrix = self.text_matrix.copy()
                    
                    self.current_point = self.origin
                    self.text_line_start = self.origin
                
                elif com == "T*":
                
                    # Move to the next line using the leading parameter
                    # as the vertical displacment.
                    tx = 0
                    ty = self.text_leading
                    
                    self.text_matrix = self.move_text_to(
                        tx, ty, self.text_matrix, self.line_matrix
                        )
                    self.line_matrix = self.text_matrix.copy()
                    self.text_line_start = self.text_line_start + point(tx, ty)
                    self.current_point = self.current_point + point(tx, ty)
                
                elif com == ending:
                
                    # The ending of the text object has been found.
                    break
                
                else:
                    pass
                    # print 'Command', com, 'not known.'

            else:
            
                # A command has not been found so this must be a parameter.
                items.append(item)

            at = self._skip_whitespace(at)
            
            #print "%i unused stack items" % len(items)
        
        # Return the items found.
        
        return contents, at

    def move_text_to(self, tx, ty, text_matrix, line_matrix):
    
        text_matrix = matrix(
                [[1, 0, 0], [0, 1, 0], [tx, ty, 1]]
                ) * line_matrix
        
        return text_matrix
    
    def select_font(self, name, size):

        # Look in the resources dictionary for the font dictionary
        if self.page.Resources.has_key('Font') == 0:

            return -1    # Failed

        if self.page.Resources['Font'].has_key(name) == 0:

            return -1

        text_font = self.page.Resources['Font'][name]
        text_size = size
        
        return text_font, text_size
    
    def calculate_rendering_matrix(self, T_fs, T_h, T_rise, T_m, CTM):
    
        # Construct a matrix to modify the text matrix.
        render_matrix = matrix([[T_fs * T_h, 0, 0],[0, T_fs, 0], [0, T_rise, 0]])
        
        # Multiply the newly constructed matrix by the text matrix and the CTM.
        return render_matrix * (T_m * CTM)
    
    def read_text(self, objects = None, position = None, threshold = None):
    
        """read_text(self, objects = None, position = None, threshold = None)
        
        Read the contents of the PDFContents object and return a tuple
        containing all of the text found and the position of the final
        text object found on the page.
        
        None of the keyword arguments should be specified.
        """
        
        if objects is None: objects = self.contents
        if position is None: position = point(0, 0)
        
        text = []
        
        for obj in objects:
        
            if type(obj) == types.ListType:
            
                new_text, position = self.read_text(obj, position, threshold)
                
                text.append(new_text)
            
            elif isinstance(obj, pdftext.Text):
            
                if obj.position.x < position.x:
                
                    text.append("\n")
                    position = obj.position
                
                if obj.text != " ":
                
                    dp = abs(obj.position - position)
                    
                    # Assume horizontal writing.
                    if threshold is not None and dp > (threshold * obj.size):
                    
                        # Infer that a space could be inserted before this
                        # piece of text.
                        text.append(" " * int(dp/obj.size))
                
                text.append(obj.text)
                
                position = obj.position
        
        return "".join(text), position



if __name__ == '__main__':

    if len(sys.argv) > 1:

        doc = PDFDocument(sys.argv[1])

        print 'Version', doc.document_version()

    #sys.exit()
