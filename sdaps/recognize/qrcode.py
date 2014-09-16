from sdaps import defs

from sdaps import model
from sdaps.utils.exceptions import RecognitionError
from sdaps.utils.barcode import read_barcode


class Image(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
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

        return 1

    def get_survey_id(self):
        code = self.find_bottom_right_barcode()
        if code is None or not code.isdigit() or len(code) <= 4:
            return None

        return int(code)

    def get_questionnaire_id(self):
        return self.find_bottom_left_barcode()

    def get_global_id(self):
        return None

    def find_bottom_right_barcode(self):
      return read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                 self.paper_width() / 2,
                 self.paper_height() - (self.paper_height() / 2),
                 self.paper_width() / 2,
                 self.paper_height() / 2,
                 "QR")

    def find_top_left_barcode(self):
      return read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                     0, 0,
                     self.paper_width() / 2,
                     self.paper_height() / 2,
                     "QR")

    def find_bottom_left_barcode(self):
      return read_barcode(self.obj.surface.surface, self.obj.matrix.mm_to_px(),
                     0,
                     self.paper_height() - (self.paper_height() / 2),
                     self.paper_width() / 2,
                     self.paper_height() / 2,
                     "QR")

    def paper_width(self):
      return self.obj.sheet.survey.defs.paper_width

    def paper_height(self):
      return self.obj.sheet.survey.defs.paper_height
