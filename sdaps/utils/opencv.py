# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2013, Benjamin Berg <benjamin@sipsolutions.net>
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

import os.path
import errno
import cv2
import numpy as np
from sdaps import image
import cairo
from sdaps import defs
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

try:
    import gi
    gi.require_version('Poppler', '0.18')
    from gi.repository import Poppler, Gio
except:
    log.warn(_("Cannot convert PDF files as poppler is not installed or usable!"))

def iter_images_and_pages(images):
    """This function iterates over a images and also the contained pages. As
    OpenCV is not able to handle multipage TIFF files, we use the SDAPS internal
    loading method for those."""

    for filename in images:
        if not os.path.exists(filename):
            raise IOError(errno.ENOENT, _("File does not exist"), filename)

        pages = 1
        is_tiff = False
        is_pdf = False

        try:
            # Check whether this is a TIFF file (ie. try to retrieve the page count)
            pages = image.get_tiff_page_count(filename)
            is_tiff = True
        except AssertionError:
            pass

        if not is_tiff:
            try:
                gfile = Gio.File.new_for_path(filename)
                pdf_doc = Poppler.Document.new_from_gfile(gfile, None, None)
                pages = pdf_doc.get_n_pages()
                is_pdf = True
            except:
                # Either not PDF/damaged or poppler not installed properly
                pass


        for page in range(pages):
            if is_tiff:
                # TIFF pages are zero based
                surf = image.get_rgb24_from_tiff(filename, page, False)

                img = to_opencv(surf)

            elif is_pdf:
                # Try to retrieve a single fullpage image, if that fails, render
                # document at 300dpi.

                THRESH = 10 #pt

                pdfpage = pdf_doc.get_page(page)
                page_width, page_height = pdfpage.get_size()

                images = pdfpage.get_image_mapping()
                if len(images) == 1 and (
                        abs(images[0].area.x1) < THRESH and
                        abs(images[0].area.y1) < THRESH and
                        abs(images[0].area.x2 - page_width) < THRESH and
                        abs(images[0].area.y2 - page_height) < THRESH):
                    # Assume one full page image, and simply use that.
                    surf = pdfpage.get_image(images[0].image_id)

                else:
                    dpi = 0
                    # Try to detect the DPI of the scan
                    for img in images:
                        if img.area.y2 - img.area.y1 < page_height / 2:
                            continue

                        surf = pdfpage.get_image(img.image_id)
                        # Calculate DPI from height
                        dpi_x = round(surf.get_height() / (img.area.y2 - img.area.y1) * 72)
                        dpi_y = round(surf.get_width() / (img.area.x2 - img.area.x1) * 72)
                        if abs(dpi_x - dpi_y) <= 1:
                            dpi = max(dpi, dpi_x, dpi_y)

                    # Fall back to 300dpi for odd values
                    if dpi < 199 or dpi > 601:
                        dpi = 300

                    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, int(dpi / 72 * page_width), int(dpi / 72 * page_height))
                    cr = cairo.Context(surf)
                    cr.scale(dpi / 72, dpi / 72)
                    cr.set_source_rgb(1, 1, 1)
                    cr.paint()

                    pdfpage.render_for_printing(cr)

                    del cr

                img = to_opencv(surf)

            else:
                img = cv2.imread(filename)

            yield img, filename, page

def sharpen(img):
    blured = cv2.GaussianBlur(img, (0,0), 5)
    img = cv2.addWeighted(img, 1.5, blured, -0.5, 0)

    return img

def to_opencv(surf):
    width = surf.get_width()
    height = surf.get_height()
    stride = surf.get_stride()

    # We need to ensure a sane stride!
    np_width = stride // 4

    # This converts by doing a copy; first create target numpy array
    # We need a dummy alpha channel ...
    target = np.empty((height, np_width), dtype=np.uint32)

    tmp_surf = cairo.ImageSurface.create_for_data(target.data, cairo.FORMAT_RGB24, width, height, stride)
    cr = cairo.Context(tmp_surf)
    # Handle A1 surfaces?
    cr.set_source_surface(surf)
    cr.paint()
    del cr
    tmp_surf.flush()
    del tmp_surf

    # Now, we need a bit of reshaping
    img = np.empty((height, width, 3), dtype=np.uint8)

    # order should be BGR
    img[:,:,2] = 0xff & (target[:,:] >> 16)
    img[:,:,1] = 0xff & (target[:,:] >> 8)
    img[:,:,0] = 0xff & target[:,:]

    return img

def to_a1_surf(img):
    # Assume that x is the second position
    assert(len(img.strides) == 2)
    assert(img.strides[1] == 1)

    if img.strides[0] % 4:
        # Need to reshape, lets just cut off up to 3 pixel
        target = np.empty((img.shape[0], img.shape[1] - img.shape[1] % 4), dtype=np.uint8)
        target[:,:] = img[:,:target.shape[1]]

        img = target

    height, width = img.shape
    surf_a8 = cairo.ImageSurface.create_for_data(img.data, cairo.FORMAT_A8, width, height, img.strides[0])

    surf_a1 = cairo.ImageSurface(cairo.FORMAT_A1, width, height)
    cr = cairo.Context(surf_a1)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.set_source_surface(surf_a8)
    cr.paint()

    return surf_a1

def ensure_orientation(img, portrait):
    img_portrait = img.shape[1] <= img.shape[0]
    if img_portrait != portrait:
        # Rotate into new array (CV does not like negative strides and such)
        new = np.empty((img.shape[1],img.shape[0])+img.shape[2:], dtype=img.dtype)
        new[:] = np.rot90(img)
        img = new

    return img

def ensure_greyscale(img):
    if len(img.shape) == 2:
        # Well, seems to be greyscale/monochrome already
        return img

    # Average the color samples, and convert back to uint8
    img = np.average(img, 2)
    img = np.array(img, dtype=np.uint8)

    return img

def convert_to_monochrome(img, size=201, thresh_adjust=5):
    img = ensure_greyscale(img)

    img = cv2.adaptiveThreshold(img, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, size, thresh_adjust)

    return img
   
def save(img, filename):
    cv2.imwrite(img, filename)


def _fallback_matrix(width, height, paper_width, paper_height):
    """Calcualte a fallback matrix. Basically the same as in matrix.py, should
    be merged somehow!"""
    xres = width / float(paper_width)
    yres = height / float(paper_height)

    # Assume the smaller size fits better ...
    res = min(xres, yres)

    scan_width = width / res
    scan_height = height / res

    dx = (paper_width - scan_width) / 2.0
    dy = (paper_height - scan_height) / 2.0

    matrix = cairo.Matrix()

    # Center the image
    matrix.translate(dx, dy)
    matrix.scale(1.0 / res, 1.0 / res)

    matrix.invert()

    return matrix, res


def transform_using_corners(img, paper_width, paper_height):
    surf = to_a1_surf(convert_to_monochrome(img))

    matrix, res = _fallback_matrix(surf.get_width(), surf.get_height(), paper_width, paper_height)

    top_left = image.find_corner_marker(surf, matrix, 1)
    top_right = image.find_corner_marker(surf, matrix, 2)
    bottom_right = image.find_corner_marker(surf, matrix, 3)
    bottom_left = image.find_corner_marker(surf, matrix, 4)

    scale = 1 * res

    x0 = scale * defs.corner_mark_left
    y0 = scale * defs.corner_mark_top
    x1 = scale * (paper_width - defs.corner_mark_right)
    y1 = scale * (paper_height - defs.corner_mark_bottom)

    width, height = int(scale * paper_width), int(scale * paper_height)
    # Increase width to be a multiple of 4
    if width % 4:
        width = width + 4 - width % 4

    transform_matrix = cv2.getPerspectiveTransform(
        np.array((top_left, top_right, bottom_right, bottom_left), dtype=np.float32),
        np.array(((x0, y0), (x1, y0), (x1, y1), (x0, y1)), dtype=np.float32))

    transformed = cv2.warpPerspective(img, transform_matrix, dsize=(width, height))

    return transformed

