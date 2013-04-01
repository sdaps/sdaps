

import sys
from gamera import core
core.init_gamera()

# To import/export data from/to cairo. We have custom C routines to do the
# conversions of the string data.
from gamera.plugins import string_io
from sdaps import image

import cairo

def _gamera_image_from_surface_a1(surface, x, y, width, height):
    pos = core.Point(0, 0)
    size = core.Dim(width, height)

    # Create a subsurface of the correct size
    subsurface = cairo.ImageSurface(cairo.FORMAT_A1, width, height)
    cr = cairo.Context(subsurface)
    cr.set_source_surface(surface, -x, -y)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.paint()
    del cr
    subsurface.flush()

    # Retrieve a string in gameras ONEBIT format
    string = image.get_gamera_onebit(subsurface)
    del subsurface

    # Create gamera image
    img = string_io._from_raw_string(pos, size, core.ONEBIT, core.DENSE, string)
    # Set resolution
    #img.resolution = float(resolution)

    return img

def from_surface(surface, x=0, y=0, width=None, height=None):
    surface_format = surface.get_format()

    if width == None:
        width = surface.get_width() - x
    if height == None:
        height == surface.get_height() - y

    if surface_format == cairo.FORMAT_A1:
        return _gamera_image_from_surface_a1(surface, x, y, width, height)
    else:
        raise AssertionError("Cannot convert surfaces of type %s to gamera images" % surface_format)

def _surface_from_gamera_image_rgb(gamera_image):
    width, height = gamera_image.ncols, gamera_image.nrows

    img_data = gamera_image._to_raw_string()

    surface = image.get_surface_from_rgb_string(img_data, width, height)

    return surface

def to_surface(image):

    if image.data.pixel_type == core.RGB:
        return _surface_from_gamera_image_rgb(image)
    else:
        raise AssertionError("Cannot convert gamera image with format %s to cairo" % image.data.pixel_type_name)

