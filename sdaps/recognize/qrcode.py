# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2014, Michael Batchelor <batchelor@nationbuilder.com>
# Copyright(C) 2014, Chuck Collins <chuck@nationbuilder.com>
# Copyright(C) 2014, Jacob Green <jacob@nationbuilder.com>
# Copyright(C) 2014, Dustin Ngo <dustin@nationbuilder.com>
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


class Image(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'style'
    obj_class = model.sheet.Image

    def get_page_rotation(self):
        code = self.find_bottom_right_barcode()
        if code is None:
            # Well, that failed, so try to search the upper left corner instead
            code = self.find_top_left_barcode()

            if code is not None:
                return True
            else:
                return None
        else:
            return False

    def get_page_number(self):
        code = self.find_bottom_right_barcode()

        if code is None or (not code.isdigit() and len(code) < 4):
            return None

        return int(code[-4:])

    def get_survey_id(self):
        code = self.find_bottom_right_barcode()

        if code is None or not code.isdigit() or len(code) <= 4:
            return None

        return int(code[:-4])

    def get_questionnaire_id(self):
        return self.find_bottom_left_barcode()

    def get_global_id(self):
        return self.find_bottom_center_barcode()

    def find_bottom_right_barcode(self):
      return read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                 self.paper_width() * 0.75,
                 self.paper_height() * 0.75,
                 self.paper_width() * 0.25,
                 self.paper_height() * 0.25,
                 "QRCODE")

    def find_top_left_barcode(self):
      return read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                     0, 0,
                     self.paper_width() * 0.25,
                     self.paper_height() * 0.25,
                     "QRCODE")

    def find_bottom_left_barcode(self):
      return read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                     0,
                     self.paper_height() * 0.75,
                     self.paper_width() * 0.25,
                     self.paper_height() * 0.25,
                     "QRCODE")

    def find_bottom_center_barcode(self):
      return read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                     self.paper_width() * 0.375,
                     self.paper_height() * 0.75,
                     self.paper_width() * 0.25,
                     self.paper_height() * 0.25,
                     "QRCODE")

    def paper_width(self):
      return self.obj.sheet.survey.defs.paper_width

    def paper_height(self):
      return self.obj.sheet.survey.defs.paper_height
