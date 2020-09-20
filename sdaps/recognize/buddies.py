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

import cairo
import math

from sdaps import model
from sdaps import matrix
from sdaps import surface
from sdaps import image
from sdaps import defs
from sdaps.utils.exceptions import RecognitionError
from sdaps import log

from sdaps.utils.barcode import read_barcode
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

pt_to_mm = 25.4 / 72.0

warned_multipage_not_correctly_scanned = False


class Sheet(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.sheet.Sheet

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)
        self.filter_image = None

    def recognize(self):
        global warned_multipage_not_correctly_scanned

        self.obj.valid = 1

        duplex_mode = self.obj.survey.defs.duplex

        # Load all images of this sheet
        for image in self.obj.images:
            if not image.ignored:
                image.rotated = 0
                image.surface.load()

        failed_pages = set()

        # Matrix recognition for all of them
        matrix_errors = set()
        for page, image in enumerate(self.obj.images):
            try:
                image.recognize.calculate_matrix()
            except RecognitionError:
                matrix_errors.add(page)

        # We need to check the matrix_errors. Some are expected in simplex mode
        for page in matrix_errors:
            # in simplex mode every page will have a matrix; it might be a None
            # matrix though

            log.warn(_('%s, %i: Matrix not recognized.') % (self.obj.images[page].filename, self.obj.images[page].tiff_page + 1))
            failed_pages.add(page)

        # Rotation for all of them
        for page, image in enumerate(self.obj.images):
            try:
                # This may set the rotation to "None" for unknown
                image.recognize.calculate_rotation()
            except RecognitionError:
                log.warn(_('%s, %i: Rotation not found.') % (image.filename, image.tiff_page + 1))
                failed_pages.add(page)

        # Copy the rotation over (if required) and print warning if the rotation is unknown
        self.duplex_copy_image_attr(failed_pages, 'rotated', _("Neither %s, %i or %s, %i has a known rotation!"))

        # Reload any image that is rotated.
        for page, image in enumerate(self.obj.images):
            if image.rotated and not image.ignored:
                image.surface.load()
                # And redo the whole matrix stuff ...
                # XXX: It would be better to manipulate the matrix instead.
                try:
                    image.recognize.calculate_matrix()
                except RecognitionError:
                    if duplex_mode:
                        log.warn(_('%s, %i: Matrix not recognized (again).') % (image.filename, image.tiff_page + 1))
                        failed_pages.add(page)

        ############
        # At this point we can extract the page numbers and IDs as neccessary.
        ############

        # Figure out the page numbers
        # ***************************
        for page, image in enumerate(self.obj.images):
            try:
                # This may set the page_number to "None" for unknown
                image.recognize.calculate_page_number()
            except RecognitionError:
                log.warn(_('%s, %i: Could not get page number.') % (image.filename, image.tiff_page + 1))
                image.page_number = None
                failed_pages.add(page)

        i = 0
        while i < len(self.obj.images):
            # We try to recover at least the page number of failed pages
            # this way.
            # NOTE: In simplex mode dummy pages will be inserted, so one page
            # always has no page number, and the other one has one.
            # This is exactly what we want, so we don't need to do anything
            # (except warn if we did not find any page!)
            failed = (i in failed_pages or i + 1 in failed_pages)

            first = self.obj.images[i]
            second = self.obj.images[i + 1]

            if first.page_number is None and second.page_number is None:
                if not failed:
                    # Whoa, that should not happen.
                    log.warn(_("Neither %s, %i or %s, %i has a known page number!" %
                             (first.filename, first.tiff_page + 1, second.filename, second.tiff_page + 1)))
                    failed_pages.add(i)
                    failed_pages.add(i + 1)

            elif duplex_mode == False:
                # Simplex mode is special, as we know that one has to be unreadable
                # we need to ensure one of the page numbers is None
                if first.page_number is not None and second.page_number is not None:
                    # We don't touch the ignore flag in this case
                    # Simply print a message as this should *never* happen
                    log.error(_("Got a simplex document where two adjacent pages had a known page number. This should never happen as even simplex scans are converted to duplex by inserting dummy pages. Maybe you did a simplex scan but added it in duplex mode? The pages in question are %s, %i and %s, %i.") % (first.filename, first.tiff_page + 1, second.filename, second.tiff_page + 1))

                # Set the ignored flag for the unreadable page. This is a valid
                # operation as the back side of a readable page is known to be
                # empty.
                elif first.page_number is None:
                    first.ignored = True
                else:
                    second.ignored = True

            elif first.page_number is None:
                # One based, odd -> +1, even -> -1
                first.page_number = second.page_number - 1 + 2 * (second.page_number % 2)
            elif second.page_number is None:
                second.page_number = first.page_number - 1 + 2 * (first.page_number % 2)
            elif first.page_number != (second.page_number - 1 + 2 * (second.page_number % 2)):
                if not failed:
                    log.warn(_("Images %s, %i and %s, %i do not have consecutive page numbers!" %
                             (first.filename, first.tiff_page + 1, second.filename, second.tiff_page + 1)))

                    failed_pages.add(i)
                    failed_pages.add(i + 1)

            i += 2

        # Check that every page has a non None value, and each page exists once.
        pages = set()
        for i, image in enumerate(self.obj.images):
            # Ignore known blank pages
            if image.ignored:
                continue

            if image.page_number is None:
                log.warn(_("No page number for page %s, %i exists." % (image.filename, image.tiff_page + 1)))
                failed_pages.add(i)
                continue

            if image.page_number in pages:
                log.warn(_("Page number for page %s, %i already used by another image.") %
                         (image.filename, image.tiff_page + 1))
                failed_pages.add(i)
                continue

            if image.page_number <= 0 or image.page_number > self.obj.survey.questionnaire.page_count:
                log.warn(_("Page number %i for page %s, %i is out of range.") %
                         (image.page_number, image.filename, image.tiff_page + 1))
                failed_pages.add(i)
                continue

            pages.add(image.page_number)

        # Figure out the suvey ID if neccessary
        # *************************************
        if self.obj.survey.defs.print_survey_id:
            for page, image in enumerate(self.obj.images):
                try:
                    if not duplex_mode or (image.page_number is not None and image.page_number % 2 == 0):
                        image.recognize.calculate_survey_id()
                    else:
                        image.survey_id = None
                except RecognitionError:
                    log.warn(_('%s, %i: Could not read survey ID, but should be able to.') %
                             (image.filename, image.tiff_page + 1))
                    failed_pages.add(page)

            self.duplex_copy_image_attr(failed_pages, "survey_id", _("Could not read survey ID of either %s, %i or %s, %i!"))

            # Simply use the survey ID from the first image globally
            self.obj.survey_id = self.obj.images[0].survey_id

            if self.obj.survey_id != self.obj.survey.survey_id:
                # Broken survey ID ...
                log.warn(_("Got a wrong survey ID (%s, %i)! It is %s, but should be %i.") %
                         (self.obj.images[0].filename,
                          self.obj.images[0].tiff_page + 1,
                          self.obj.survey_id,
                          self.obj.survey.survey_id))
                self.obj.valid = 0
        else:
            # Assume that the data is from the correct survey
            self.obj.survey_id = self.obj.survey.survey_id
            for image in self.obj.images:
                image.survey_id = self.obj.survey.survey_id

        # Figure out the questionnaire ID if neccessary
        # *********************************************
        if self.obj.survey.defs.print_questionnaire_id:
            questionnaire_ids = []

            for page, image in enumerate(self.obj.images):
                try:
                    if not duplex_mode or (image.page_number is not None and image.page_number % 2 == 0):
                        image.recognize.calculate_questionnaire_id()
                except RecognitionError:
                    log.warn(_('%s, %i: Could not read questionnaire ID, but should be able to.') % \
                             (image.filename, image.tiff_page + 1))
                    failed_pages.add(page)
                if image.questionnaire_id is not None:
                    questionnaire_ids.append(image.questionnaire_id)

            self.duplex_copy_image_attr(failed_pages, "questionnaire_id", _("Could not read questionnaire ID of either %s, %i or %s, %i!"))

            if len(questionnaire_ids):
                self.obj.questionnaire_id = questionnaire_ids[0]
            else:
                self.obj.questionnaire_id = self.obj.images[0].questionnaire_id

        # Try to load the global ID. If it does not exist we will get None, if
        # it does, then it will be non-None. We don't care much about it
        # internally anyways.
        # However, we do want to ensure that it is the same everywhere if it
        # can be read in.
        # *********************************************
        for page, image in enumerate(self.obj.images):
            try:
                if not duplex_mode or (image.page_number is not None and image.page_number % 2 == 0):
                    image.recognize.calculate_global_id()
            except RecognitionError:
                pass

        self.duplex_copy_image_attr(failed_pages, "global_id")

        self.obj.global_id = self.obj.images[0].global_id

        for image in self.obj.images:
            if (image.global_id is not None and self.obj.global_id != image.global_id) or \
                (image.survey_id is not None and self.obj.survey_id != image.survey_id) or \
                (image.questionnaire_id is not None and self.obj.questionnaire_id != image.questionnaire_id):

                if not warned_multipage_not_correctly_scanned:
                    log.warn(_("Got different IDs on different pages for at least one sheet! Do *NOT* try to use filters with this survey! You have to run a \"reorder\" step for this to work properly!"))

                    warned_multipage_not_correctly_scanned = True

        # Done
        if failed_pages:
            self.obj.valid = 0

    def clean(self):
        for image in self.obj.images:
            image.recognize.clean()

    def duplex_copy_image_attr(self, failed_pages, attr, error_msg=None):
        """If in duplex mode, this function will copy the given attribute
        from the image that defines it over to the one that does not.
        ie. if the attribute is None in one and differently in the other image
        it is copied.

        """

        i = 0
        while i < len(self.obj.images):
            failed = (i in failed_pages or i + 1 in failed_pages)

            first = self.obj.images[i]
            second = self.obj.images[i + 1]

            if getattr(first, attr) is None and getattr(second, attr) is None:
                if error_msg is not None and not failed:
                    log.warn(error_msg % (first.filename, first.tiff_page + 1, second.filename, second.tiff_page + 1))
            elif getattr(first, attr) is None:
                setattr(first, attr, getattr(second, attr))
            elif getattr(second, attr) is None:
                setattr(second, attr, getattr(first, attr))

            i += 2

    def get_page_image(self, page_number):
        img = self.obj.get_page_image(page_number)
        if self.filter_image is not None:
            return img if img == self.filter_image else None
        return img


class Image(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.sheet.Image

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)

        if self.obj.sheet.survey.defs.style == "classic":
            from . import classic
        elif self.obj.sheet.survey.defs.style == "code128":
            from . import code128
        elif self.obj.sheet.survey.defs.style == "qr":
            from . import qrcode
        elif self.obj.sheet.survey.defs.style == "custom":
            if not hasattr(self.obj, "style"):
                import sys
                log.error(_("No style buddy loaded. This needs to be done for the \"custom\" style!"))
                sys.exit(1)
        else:
            raise AssertionError

    def calculate_rotation(self):
        if self.obj.ignored:
            self.obj.rotated = None
        else:
            self.obj.rotated = self.obj.style.get_page_rotation()

    def calculate_page_number(self):
        if self.obj.ignored:
            self.obj.page_number = None
        else:
            self.obj.page_number = self.obj.style.get_page_number()

    def calculate_survey_id(self):
        if self.obj.ignored:
            self.obj.survey_id = None
        else:
            self.obj.survey_id = self.obj.style.get_survey_id()

    def calculate_questionnaire_id(self):
        if self.obj.ignored:
            self.obj.questionnaire_id = None
        else:
            self.obj.questionnaire_id = self.obj.style.get_questionnaire_id()

    def calculate_global_id(self):
        if self.obj.ignored:
            self.obj.global_id = None
        else:
            self.obj.global_id = self.obj.style.get_global_id()

    def clean(self):
        self.obj.surface.clean()

    def calculate_matrix(self):
        if self.obj.ignored:
            self.obj.matrix.set_px_to_mm(None)
            return

        try:
            # Reset matrix, so that we do not use some existing (and broken)
            # matrix for the resolution estimation.
            self.obj.matrix.set_px_to_mm(None)

            matrix = image.calculate_matrix(
                self.obj.surface.surface,
                self.obj.matrix.mm_to_px(),
                self.obj.sheet.survey.defs.corner_mark_left, self.obj.sheet.survey.defs.corner_mark_top,
                self.obj.sheet.survey.defs.paper_width - self.obj.sheet.survey.defs.corner_mark_left - self.obj.sheet.survey.defs.corner_mark_right,
                self.obj.sheet.survey.defs.paper_height - self.obj.sheet.survey.defs.corner_mark_top - self.obj.sheet.survey.defs.corner_mark_bottom,
            )
        except AssertionError:
            self.obj.matrix.set_px_to_mm(None)
            raise RecognitionError
        else:
            self.obj.matrix.set_px_to_mm(matrix)

    def get_coverage(self, x, y, width, height):
        assert(not self.obj.ignored)

        return image.get_coverage(
            self.obj.surface.surface,
            self.matrix,
            x, y, width, height
        )

    def get_masked_coverage(self, mask, x, y):
        assert(not self.obj.ignored)

        return image.get_masked_coverage(
            self.obj.surface.surface,
            mask,
            x, y
        )

    def get_masked_coverage_without_lines(self, mask, x, y, line_width, line_count):
        assert(not self.obj.ignored)

        return image.get_masked_coverage_without_lines(
            self.obj.surface.surface,
            mask, x, y,
            line_width, line_count
        )

    def get_masked_white_area_count(self, mask, x, y, min_size, max_size):
        assert(not self.obj.ignored)

        return image.get_masked_white_area_count(
            self.obj.surface.surface,
            mask, x, y,
            min_size, max_size
        )

    def correction_matrix_masked(self, x, y, mask):
        assert(not self.obj.ignored)

        return image.calculate_correction_matrix_masked(
            self.obj.surface.surface,
            mask,
            self.matrix,
            x, y
        )

    def find_box_corners(self, x, y, width, height):
        assert(not self.obj.ignored)

        tl, tr, br, bl = image.find_box_corners(
            self.obj.surface.surface,
            self.matrix,
            x, y,
            width, height)

        tolerance = defs.find_box_corners_tolerance
        if(abs(x - tl[0]) > tolerance or
            abs(y - tl[1]) > tolerance or
            abs(x + width - tr[0]) > tolerance or
            abs(y - tr[1]) > tolerance or
            abs(x + width - br[0]) > tolerance or
            abs(y + height - br[1]) > tolerance or
            abs(x - bl[0]) > tolerance or
            abs(y + height - bl[1]) > tolerance
           ):
            raise AssertionError("The found values differ too much from where the box should be.")
        return tl, tr, br, bl

    @property
    def matrix(self):
        return self.obj.matrix.mm_to_px(fallback=False)

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.questionnaire.Questionnaire

    def identify(self, clean=True):
        # recognize image
        try:
            self.obj.sheet.recognize.recognize()
            result = True

            # Mark sheet as invalid if any page is missing,
            for page in range(self.obj.page_count):
                img = self.obj.sheet.get_page_image(page + 1)

                if img is None or img.recognize.matrix is None:
                    self.obj.sheet.valid = False
        except RecognitionError:
            self.obj.sheet.quality = 0
            result = False

        # clean up
        if clean:
            self.obj.sheet.recognize.clean()

        return result

    def recognize(self, skip_identify=False, image=None):
        # recognize image
        if not skip_identify:
            assert image is None
            res = self.identify(clean=False)
        elif image is None:
            for img in self.obj.images:
                if not img.ignored:
                    img.surface.load()
            res = True
        else:
            image.surface.load()
            res = True

        if res:
            # iterate over qobjects
            self.obj.sheet.recognize.filter_image = image
            for qobject in self.obj.qobjects:
                qobject.recognize.recognize()
            self.obj.sheet.recognize.filter_image = None

            quality = 1
            for qobject in self.obj.qobjects:
                quality = min(quality, qobject.recognize.get_quality())
            self.obj.sheet.quality = quality

        # Mark the image as "recognized". It might have failed, but even if that
        # happened, we don't want to retry all the time.
        self.obj.sheet.recognized = True
        # Any newly recognized sheet is definately not verified.
        # This is relevant for reruns.
        for img in self.obj.sheet.images:
            img.verified = False

        # clean up
        self.obj.sheet.recognize.clean()


class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.questionnaire.QObject

    def recognize(self):
        pass

    def get_quality(self):
        return 1


class Question(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.questionnaire.Question

    def recognize(self):
        # iterate over boxes
        for box in self.obj.boxes:
            box.recognize.recognize()

    def get_quality(self):
        result = 1
        for box in self.obj.boxes:
            result = min(result, box.data.quality)
        return result


class Box(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.questionnaire.Box

    def recognize(self):
        pass


class Checkbox(Box, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.questionnaire.Checkbox

    def prepare_mask(self):
        img = self.obj.sheet.recognize.get_page_image(self.obj.page_number)
        width, height = self.obj.width, self.obj.height
        line_width = self.obj.lw

        matrix = list(img.recognize.matrix)
        # Remove any offset from the matrix
        matrix[4] = 0
        matrix[5] = 0
        matrix = cairo.Matrix(*matrix)

        px_width, px_height = matrix.transform_distance(width, height)
        px_width, px_height = int(math.ceil(px_width)), int(math.ceil(px_height))

        surf = cairo.ImageSurface(cairo.FORMAT_A1, px_width, px_height)
        cr = cairo.Context(surf)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        # Move to center and apply matrix
        cr.translate(0.5 * px_width, 0.5 * px_height)
        cr.transform(matrix)

        cr.set_source_rgba(0, 0, 0, 1)

        cr.set_line_width(line_width)

        matrix.invert()
        xoff, yoff = matrix.transform_distance(px_width / 2.0, px_height / 2.0)
        xoff = xoff - width / 2
        yoff = yoff - height / 2

        return cr, surf, line_width, width, height, xoff, yoff

    def get_outline_mask(self):
        cr, surf, line_width, width, height, xoff, yoff = self.prepare_mask()

        if self.obj.form == "ellipse":
            cr.save()

            cr.scale((width - line_width) / 2.0, (height - line_width) / 2.0)
            cr.arc(0, 0, 1.0, 0, 2*math.pi)

            # Restore old matrix (without removing the current path)
            cr.restore()
        else:
            cr.translate(-0.5 * width, -0.5 * height)
            cr.rectangle(line_width / 2, line_width / 2, width - line_width / 2, height - line_width / 2)

        cr.stroke()
        surf.flush()
        del cr

        return surf, xoff, yoff

    def get_inner_mask(self):
        """Note this discards half a line width inside the box!"""
        cr, surf, line_width, width, height, xoff, yoff = self.prepare_mask()

        if self.obj.form == "ellipse":
            cr.save()

            cr.scale((width - 3*line_width) / 2.0, (height - 3*line_width) / 2.0)
            cr.arc(0, 0, 1.0, 0, 2*math.pi)

            # Restore old matrix (without removing the current path)
            cr.restore()
        else:
            cr.translate(-0.5 * width, -0.5 * height)
            cr.rectangle(1.5 * line_width, 1.5 * line_width, width - 3 * line_width, height - 3 * line_width)

        cr.fill()
        surf.flush()
        del cr

        return surf, xoff, yoff


    def recognize(self):
        img = self.obj.sheet.recognize.get_page_image(self.obj.page_number)

        if img is None or img.recognize.matrix is None:
            return

        surf, xoff, yoff = self.get_outline_mask()

        matrix, covered = img.recognize.correction_matrix_masked(
            self.obj.x, self.obj.y,
            surf
        )
        # Calculate some sort of quality for the checkbox position
        if covered < defs.image_line_coverage:
            pos_quality = 0
        else:
            pos_quality = min(covered + 0.2, 1)

        x, y = matrix.transform_point(self.obj.x, self.obj.y)
        width, height = matrix.transform_distance(self.obj.width, self.obj.height)
        self.obj.data.x = x + xoff
        self.obj.data.y = y + yoff
        self.obj.data.width = width
        self.obj.data.height = height

        # The debug struct will be filled in if debugging is enabled in the
        # C library. This is done by the boxgallery script currently.
        self.debug = {}

        mask, xoff, yoff = self.get_inner_mask()
        x, y = self.obj.data.x, self.obj.data.y
        x, y = x + xoff, y + yoff

        x, y = img.recognize.matrix.transform_point(x, y)
        x, y = int(x), int(y)

        # This is not the outline, but the width of the drawn stroke!
        remove_line_width = 1.2 * pt_to_mm
        remove_line_width_px = max(img.recognize.matrix.transform_distance(remove_line_width, remove_line_width))

        coverage = img.recognize.get_masked_coverage(mask, x, y)
        self.obj.data.metrics['coverage'] = coverage
        self.debug['coverage'] = image.get_debug_surface()

        # Remove 3 lines with width 1.2pt(about 5px).
        coverage = img.recognize.get_masked_coverage_without_lines(mask, x, y, remove_line_width_px, 3)
        self.obj.data.metrics['cov-lines-removed'] = coverage
        self.debug['cov-lines-removed'] = image.get_debug_surface()

        count, coverage = img.recognize.get_masked_white_area_count(mask, x, y, 0.05, 1.0)
        self.obj.data.metrics['cov-min-size'] = coverage
        self.debug['cov-min-size'] = image.get_debug_surface()

        state = 0
        quality = -1
        # Iterate the ranges
        for metric, value in self.obj.data.metrics.items():
            metric = defs.checkbox_metrics[self.obj.sheet.survey.defs.checkmode][metric]

            for lower, upper in zip(metric[:-1], metric[1:]):
                if value >= lower[0] and value <= upper[0]:
                    # Interpolate quality value
                    if lower[0] != upper[0]:
                        metric_quality = lower[2] + (upper[2] - lower[2]) * (value - lower[0]) / (upper[0] - lower[0])
                    else:
                        metric_quality = lower[2]

                    if metric_quality > quality:
                        state = lower[1]
                        quality = metric_quality

        self.obj.data.state = state
        self.obj.data.quality = min(quality, pos_quality)


class Textbox(Box, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.questionnaire.Textbox

    def recognize(self):
        class Quadrilateral():
            """This class iterates through small box areas in a quadriliteral.
            This is usefull because some scanners have trapezoidal distortions."""
            # Assumes top left, top right, bottom right, bottom left
            # corner.
            def __init__(self, p0, p1, p2, p3):
                self.x0 = p0[0]
                self.y0 = p0[1]
                self.x1 = p1[0]
                self.y1 = p1[1]
                self.x2 = p2[0]
                self.y2 = p2[1]
                self.x3 = p3[0]
                self.y3 = p3[1]

                # 0 -> 1
                self.m0 = (self.y1 - self.y0) / (self.x1 - self.x0)
                self.m1 = (self.x2 - self.x1) / (self.y2 - self.y1)
                self.m2 = (self.y3 - self.y2) / (self.x3 - self.x2)
                self.m3 = (self.x0 - self.x3) / (self.y0 - self.y3)

                self.top = min(self.y0, self.y1)
                self.bottom = max(self.y2, self.y3)
                self.left = min(self.x0, self.x3)
                self.right = max(self.x1, self.x2)

            def iterate_bb(self, step_x, step_y, test_width, test_height, padding):
                y = self.top
                while y + test_height < self.bottom:
                    x = self.left
                    while x + test_width < self.right:
                        yield x, y
                        x += step_x

                    y += step_y

            def iterate_outline(self, step_x, step_y, test_width, test_height, padding):
                # Top
                x, y = self.x0, self.y0
                x += padding
                y += padding

                dest_x = self.x1 - padding - test_width
                dest_y = self.y1 + padding

                dist_x = dest_x - x
                dist_y = dest_y - y

                length = math.sqrt(dist_x ** 2 + dist_y ** 2)
                for step in range(int(length / step_x)):
                    yield x + dist_x * step / (length / step_x), y + dist_y * step / (length / step_x)
                yield dest_x, dest_y

                # Bottom
                x, y = self.x3, self.y3
                x = x + padding
                y = y - padding - test_height

                dest_x = self.x2 - padding - test_width
                dest_y = self.y2 - padding - test_height

                dist_x = dest_x - x
                dist_y = dest_y - y

                length = math.sqrt(dist_x ** 2 + dist_y ** 2)
                for step in range(int(length / step_x)):
                    yield x + dist_x * step / (length / step_x), y + dist_y * step / (length / step_x)
                yield dest_x, dest_y

                # Left
                x, y = self.x0, self.y0
                x += padding
                y += padding

                dest_x = self.x3 + padding
                dest_y = self.y3 - padding - test_height

                dist_x = dest_x - x
                dist_y = dest_y - y

                length = math.sqrt(dist_x ** 2 + dist_y ** 2)
                for step in range(int(length / step_y)):
                    yield x + dist_x * step / (length / step_y), y + dist_y * step / (length / step_y)
                yield dest_x, dest_y

                # Right
                x, y = self.x1, self.y1
                x = x - padding - test_width
                y = y + padding

                dest_x = self.x2 - padding - test_width
                dest_y = self.y2 - padding - test_height

                dist_x = dest_x - x
                dist_y = dest_y - y

                length = math.sqrt(dist_x ** 2 + dist_y ** 2)
                for step in range(int(length / step_y)):
                    yield x + dist_x * step / (length / step_y), y + dist_y * step / (length / step_y)
                yield dest_x, dest_y

            def iterate(self, step_x, step_y, test_width, test_height, padding):
                for x, y in self.iterate_bb(step_x, step_y, test_width, test_height, padding):
                    ly = self.y0 + self.m0 * (x - self.x0)
                    if not ly + padding < y:
                        continue

                    ly = self.y2 + self.m2 * (x - self.x2)
                    if not ly - padding > y + test_height:
                        continue

                    lx = self.x1 + self.m1 * (y - self.y1)
                    if not lx - padding > x + test_width:
                        continue

                    lx = self.x3 + self.m3 * (y - self.y3)
                    if not lx + padding < x:
                        continue

                    yield x, y

                for x, y in self.iterate_outline(step_x, step_y, test_width, test_height, padding):
                    yield x, y

        bbox = None
        img = self.obj.sheet.recognize.get_page_image(self.obj.page_number)

        if img is None or img.recognize.matrix is None:
            return

        x = self.obj.x
        y = self.obj.y
        width = self.obj.width
        height = self.obj.height

        # Scanning area and stepping
        step_x = defs.textbox_scan_step_x
        step_y = defs.textbox_scan_step_x
        test_width = defs.textbox_scan_width
        test_height = defs.textbox_scan_height

        # extra_padding is always added to the box side at the end.
        extra_padding = defs.textbox_extra_padding
        scan_padding = defs.textbox_scan_uncorrected_padding

        quad = Quadrilateral((x, y), (x + width, y), (x + width, y + height), (x, y + height))
        try:
            quad = Quadrilateral(*img.recognize.find_box_corners(x, y, width, height))
            # Lower padding, as we found the corners and are therefore more acurate
            scan_padding = defs.textbox_scan_padding
        except AssertionError:
            pass

        surface = img.surface.surface
        matrix = img.recognize.matrix
        for x, y in quad.iterate(step_x, step_y, test_width, test_height, scan_padding):
            # Use the image module directly as we are calling in *a lot*
            coverage = image.get_coverage(surface, matrix, x, y, test_width, test_height)
            if coverage > defs.textbox_scan_coverage:
                if not bbox:
                    bbox = [x, y, test_width, test_height]
                else:
                    bbox_x = min(bbox[0], x)
                    bbox_y = min(bbox[1], y)
                    bbox[2] = max(bbox[0] + bbox[2], x + test_width) - bbox_x
                    bbox[3] = max(bbox[1] + bbox[3], y + test_height) - bbox_y
                    bbox[0] = bbox_x
                    bbox[1] = bbox_y

        if bbox and (bbox[2] > defs.textbox_minimum_writing_width or
                     bbox[3] > defs.textbox_minimum_writing_height):
            # Do not accept very small bounding boxes.
            self.obj.data.state = True

            self.obj.data.x = bbox[0] - (scan_padding + extra_padding)
            self.obj.data.y = bbox[1] - (scan_padding + extra_padding)
            self.obj.data.width = bbox[2] + 2 * (scan_padding + extra_padding)
            self.obj.data.height = bbox[3] + 2 * (scan_padding + extra_padding)
        else:
            self.obj.data.state = False

            self.obj.data.x = self.obj.x
            self.obj.data.y = self.obj.y
            self.obj.data.width = self.obj.width
            self.obj.data.height = self.obj.height

class Codebox(Textbox, metaclass=model.buddy.Register):

    name = 'recognize'
    obj_class = model.questionnaire.Codebox

    def recognize(self):
        img = self.obj.sheet.recognize.get_page_image(self.obj.page_number)

        if img is None or img.recognize.matrix is None:
            return

        x = self.obj.x
        y = self.obj.y
        width = self.obj.width
        height = self.obj.height

        surface = img.surface.surface
        matrix = img.recognize.matrix

        res = read_barcode(surface, matrix,
                           x, y, width, height,
                           "QRCODE")

        # This is maybe a bit odd, but we accept empty string as a valid
        # content (if there was a barcode which was just the empty string).
        if res is not None:
            self.obj.data.state = True
            self.obj.data.text = res
        else:
            self.obj.data.state = False
            self.obj.data.text = None
