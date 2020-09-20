# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2012 Benjamin Berg <benjamin@sipsolutions.net>
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

from sdaps import defs

from sdaps import model
from sdaps.utils.exceptions import RecognitionError
from sdaps.utils.barcode import read_barcode


# Reading the metainformation of CODE-128 style questionnaires. See classic.py
# for some more information.

class Image(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'style'
    obj_class = model.sheet.Image

    def get_page_rotation(self):
        # Returns page rotation or "None" if it cannot be retrieved

        # Figure out wether the page is rotated by looking for a barcode first
        # at the bottom right, then at the top left.
        # Note that we do not care about the value of the barcode, we are happy
        # to simply know that it exists.

        paper_width = self.obj.sheet.survey.defs.paper_width
        paper_height = self.obj.sheet.survey.defs.paper_height

        # Search for the barcode in the lower right corner.
        # Note that we cannot find another barcode this way, because the one in the
        # center of the page is not complete
        code = \
            read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                         paper_width / 2,
                         paper_height - self.obj.sheet.survey.defs.corner_mark_bottom - defs.code128_vpad - defs.code128_height - 5,
                         paper_width / 2,
                         self.obj.sheet.survey.defs.corner_mark_bottom + defs.code128_vpad + defs.code128_height + 5)

        if code is None:
            # Well, that failed, so try to search the upper left corner instead
            code = \
                read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                             0, 0,
                             paper_width / 2,
                             self.obj.sheet.survey.defs.corner_mark_bottom + defs.code128_vpad + defs.code128_height + 5)

            if code is not None:
                return True
            else:
                return None
        else:
            return False


    def get_page_number(self):
        # Returns page number or "None" if it cannot be retrieved

        # In this function assume that the rotation is correct already.
        paper_width = self.obj.sheet.survey.defs.paper_width
        paper_height = self.obj.sheet.survey.defs.paper_height

        # Search for the barcode in the lower right corner.
        code = \
            read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                         paper_width / 2,
                         paper_height - self.obj.sheet.survey.defs.corner_mark_bottom - defs.code128_vpad - defs.code128_height - 5,
                         paper_width / 2,
                         self.obj.sheet.survey.defs.corner_mark_bottom + defs.code128_vpad + defs.code128_height + 5)

        # The code needs to be entirely numeric and at least 4 characters for the page
        if code is None or(not code.isdigit() and len(code) < 4):
            return None

        # The page number is in the lower four digits, simply extract it and convert
        # to integer
        return int(code[-4:])

    def get_survey_id(self):
        # Returns the survey ID or "None" if it cannot be retrieved

        # In this function assume that the rotation is correct already.
        paper_width = self.obj.sheet.survey.defs.paper_width
        paper_height = self.obj.sheet.survey.defs.paper_height

        # Search for the barcode in the lower left corner.
        code = \
            read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                         paper_width / 2,
                         paper_height - self.obj.sheet.survey.defs.corner_mark_bottom - defs.code128_vpad - defs.code128_height - 5,
                         paper_width / 2,
                         self.obj.sheet.survey.defs.corner_mark_bottom + defs.code128_vpad + defs.code128_height + 5)

        if code is None or not code.isdigit() or len(code) <= 4:
            return None

        return int(code[:-4])

    def get_questionnaire_id(self):
        # Returns the questionnaire ID or "None" if it cannot be retrieved

        # In this function assume that the rotation is correct already.
        paper_width = self.obj.sheet.survey.defs.paper_width
        paper_height = self.obj.sheet.survey.defs.paper_height

        # Search for the barcode on the bottom left of the page
        code = \
            read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                         0,
                         paper_height - self.obj.sheet.survey.defs.corner_mark_bottom - defs.code128_vpad - defs.code128_height - 5,
                         paper_width / 2,
                         self.obj.sheet.survey.defs.corner_mark_bottom + defs.code128_vpad + defs.code128_height + 5)

        # Simply return the code, it may be alphanumeric, we don't care here
        # XXX: Is that assumption sane?
        return code

    def get_global_id(self):
        # Returns the global ID or "None" if it cannot be retrieved

        # In this function assume that the rotation is correct already.
        paper_width = self.obj.sheet.survey.defs.paper_width
        paper_height = self.obj.sheet.survey.defs.paper_height

        # Search for the barcode in the bottom center of the page
        code = \
            read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                         paper_width / 4,
                         paper_height - self.obj.sheet.survey.defs.corner_mark_bottom - defs.code128_vpad - defs.code128_height - 5,
                         paper_width / 2,
                         self.obj.sheet.survey.defs.corner_mark_bottom + defs.code128_vpad + defs.code128_height + 5)

        # Simply return the code, it may be alphanumeric, we don't care here
        return code
