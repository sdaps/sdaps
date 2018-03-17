# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008,2011, Benjamin Berg <benjamin@sipsolutions.net>
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

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

# Note, while it is possible to cache data in the image object, this data
# will not change when the image is switched to the next sheet. So one needs
# to be careful when to invalidate it.


# All of these functions can assume that the matrix has been recognized
# for the image.
# They may throw a RecognitionError if there was an unrecoverable error.
# If no data can be retrieved(because eg. it is not printed on that
# page) they may return None to indicate this.

class Image(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'style'
    obj_class = model.sheet.Image

    def get_page_rotation(self):
        # Returns page rotation or "None" if it cannot be retrieved

        res = get_pagenumber_and_rotation(self)
        if res is None:
            return None

        return res[0]

    def get_page_number(self):
        # Returns page number or "None" if it cannot be retrieved
        # Returns page number rotation or "None" if it cannot be retrieved

        res = get_pagenumber_and_rotation(self)
        if res is None:
            return None
        # The page may not be rotated at this point
        if res[0]:
            raise RecognitionError

        return res[1]

    def get_survey_id(self):
        # Returns the survey ID or "None" if it cannot be retrieved

        if self.obj.page_number % 2 == 0 or \
           self.obj.sheet.survey.questionnaire.page_count == 1:
            pos = self.obj.sheet.survey.defs.get_survey_id_pos()

            survey_id = read_codebox(self,
                                     pos[0], pos[2])
            survey_id = read_codebox(self,
                                     pos[1], pos[2],
                                     survey_id)

            return survey_id
        else:
            return None

    def get_questionnaire_id(self):
        # Returns the questionnaire ID or "None" if it cannot be retrieved

        if self.obj.page_number % 2 == 0 or \
           self.obj.sheet.survey.questionnaire.page_count == 1:
            pos = self.obj.sheet.survey.defs.get_questionnaire_id_pos()

            questionnaire_id = read_codebox(self,
                                            pos[0], pos[2])

            return questionnaire_id
        else:
            return None

    def get_global_id(self):
        # The classic style does not support a global ID property.
        return None


############################
# Internal Helpers
############################

def read_codebox(self, x, y, code=0):
    for i in range(defs.codebox_length):
        code <<= 1
        coverage = self.obj.recognize.get_coverage(
            x + (i * defs.codebox_step) + defs.codebox_offset,
            y + defs.codebox_offset,
            defs.codebox_step - 2 * defs.codebox_offset,
            defs.codebox_height - 2 * defs.codebox_offset
        )
        if coverage > defs.codebox_on_coverage:
            code += 1
    return code


def get_pagenumber_and_rotation(self):
    # The coordinates in defs are the center of the line, not the bounding box of the box ...
    # Its a bug im stamp
    # So we need to adjust them
    half_pt = 0.5 / 72.0 * 25.4
    pt = 1.0 / 72.0 * 25.4

    # Check whether there is a valid transformation matrix. If not simply return.
    if self.obj.matrix.mm_to_px(False) is None:
        return

    width = defs.corner_box_width
    height = defs.corner_box_height
    padding = defs.corner_box_padding
    survey = self.obj.sheet.survey
    corner_boxes_positions = [
        (defs.corner_mark_left + padding, defs.corner_mark_top + padding),
        (survey.defs.paper_width - defs.corner_mark_right - padding - width, defs.corner_mark_top + padding),
        (defs.corner_mark_left + padding, survey.defs.paper_height - defs.corner_mark_bottom - padding - height),
        (survey.defs.paper_width - defs.corner_mark_right - padding - width,
         survey.defs.paper_height - defs.corner_mark_bottom - padding - height)
    ]
    corners = [
        int(self.obj.recognize.get_coverage(
            corner[0] - half_pt,
            corner[1] - half_pt,
            width + pt,
            height + pt
        ) > defs.cornerbox_on_coverage)
        for corner in corner_boxes_positions
    ]

    try:
        page_number = defs.corner_boxes.index(corners) + 1
        rotated = False
    except ValueError:
        try:
            page_number = defs.corner_boxes.index(corners[::-1]) + 1
            rotated = True
        except ValueError:
            raise RecognitionError

    return rotated, page_number

