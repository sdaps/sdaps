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

from sdaps import image
from sdaps.utils import opencv
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def convert_images(images, outfile, paper_width, paper_height, transform=False):

    portrait = paper_height >= paper_width

    for i, (img, filename, page) in enumerate(opencv.iter_images_and_pages(images)):
        img = opencv.ensure_orientation(img, portrait)
        img = opencv.sharpen(img)

        if transform:
            try:
                img = opencv.transform_using_corners(img, paper_width, paper_height)
            except AssertionError:
                log.warn(_("Could not apply 3D-transformation to image '%s', page %i!") % (filename, page))

        mono = opencv.convert_to_monochrome(img)
        image.write_a1_to_tiff(outfile, opencv.to_a1_surf(mono))


