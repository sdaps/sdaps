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
from sdaps.utils import RecognitionError
from sdaps import log

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

pt_to_mm = 25.4 / 72.0

warned_multipage_not_correctly_scanned = False


class Sheet(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'recognize'
    obj_class = model.sheet.Sheet

    def recognize(self):
        global warned_multipage_not_correctly_scanned

        self.obj.valid = 1

        duplex_mode = self.obj.survey.defs.duplex

        # Load all images of this sheet
        for image in self.obj.images:
            image.rotated = 0
            image.surface.load()

        failed_pages = set()

        # Matrix recognition for all of them
        for page, image in enumerate(self.obj.images):
            try:
                image.recognize.calculate_matrix()
            except RecognitionError:
                log.warn(_('%s, %i: Matrix not recognized.') % (image.filename, image.tiff_page))
                failed_pages.add(page)

        # Rotation for all of them
        for page, image in enumerate(self.obj.images):
            try:
                # This may set the rotation to "None" for unknown
                image.recognize.calculate_rotation()
            except RecognitionError:
                log.warn(_('%s, %i: Rotation not found.') % (image.filename, image.tiff_page))
                failed_pages.add(page)

        # In simplex mode, all rotations have to be there now,
        # in duplex mode we may need to copy them over from the other page.
        if duplex_mode:
            i = 0
            while i < len(self.obj.images):
                # Try to recover the page rotation
                failed = (i in failed_pages or i + 1 in failed_pages)

                first = self.obj.images[i]
                second = self.obj.images[i + 1]

                if first.rotated is None and second.rotated is None:
                    # Whoa, that should not happen.
                    if not failed:
                        log.warn(_("Neither %s, %i or %s, %i has a known rotation!" %
                                 (first.filename, first.tiff_page, second.filename, second.tiff_page)))
                        failed_pages.add(i)
                        failed_pages.add(i + 1)
                elif first.rotated is None:
                    first.rotated = second.rotated
                elif second.rotated is None:
                    second.rotated = first.rotated
                elif first.rotated != second.rotated:
                    if not failed:
                        log.warn(_("Found inconsistency. %s, %i and %s, %i should have the same rotation, but don't!" %
                                 (first.filename, first.tiff_page, second.filename, second.tiff_page)))
                        failed_pages.add(i)
                        failed_pages.add(i + 1)

                i += 2

        # Reload any image that is rotated.
        for page, image in enumerate(self.obj.images):
            if image.rotated:
                image.surface.load()
                # And redo the whole matrix stuff ...
                # XXX: It would be better to manipulate the matrix instead.
                try:
                    image.recognize.calculate_matrix()
                except RecognitionError:
                    log.warn(_('%s, %i: Matrix not recognized (again).') % (image.filename, image.tiff_page))
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
                log.warn(_('%s, %i: Could not get page number.') % (image.filename, image.tiff_page))
                image.page_number = None
                failed_pages.add(page)

        if duplex_mode:
            i = 0
            while i < len(self.obj.images):
                # We try to recover at least the page number of failed pages
                # this way.
                failed = (i in failed_pages or i + 1 in failed_pages)

                first = self.obj.images[i]
                second = self.obj.images[i + 1]

                if first.page_number is None and second.page_number is None:
                    if not failed:
                        # Whoa, that should not happen.
                        log.warn(_("Neither %s, %i or %s, %i has a known page number!" %
                                 (first.filename, first.tiff_page, second.filename, second.tiff_page)))
                        failed_pages.add(i)
                        failed_pages.add(i + 1)
                elif first.page_number is None:
                    # One based, odd -> +1, even -> -1
                    first.page_number = second.page_number - 1 + 2 * (second.page_number % 2)
                elif second.page_number is None:
                    second.page_number = first.page_number - 1 + 2 * (first.page_number % 2)
                elif first.page_number != (second.page_number - 1 + 2 * (second.page_number % 2)):
                    if not failed:
                        log.warn(_("Images %s, %i and %s, %i do not have consecutive page numbers!" %
                                 (first.filename, first.tiff_page, second.filename, second.tiff_page)))

                        failed_pages.add(i)
                        failed_pages.add(i + 1)

                i += 2

        # Check that every page has a non None value, and each page exists once.
        pages = set()
        for i, image in enumerate(self.obj.images):
            if image.page_number is None:
                log.warn(_("No page number for page %s, %i exists." % (image.filename, image.tiff_page)))
                failed_pages.add(i)
                continue

            if image.page_number in pages:
                log.warn(_("Page number for page %s, %i already used by another image.") %
                         (image.filename, image.tiff_page))
                failed_pages.add(i)
                continue

            if image.page_number <= 0 or image.page_number > self.obj.survey.questionnaire.page_count:
                log.warn(_("Page number %i for page %s, %i is out of range.") %
                         (image.page_number, image.filename, image.tiff_page))
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
                except RecognitionError:
                    log.warn(_('%s, %i: Could not read survey ID, but should be able to.') %
                             (image.filename, image.tiff_page))
                    failed_pages.add(page)

            self.duplex_copy_image_attr(failed_pages, "survey_id")

            # Simply use the survey ID from the first image globally
            self.obj.survey_id = self.obj.images[0].survey_id

            for image in self.obj.images:
                if self.obj.survey_id != image.survey_id:
                    if not warned_multipage_not_correctly_scanned:
                        log.warn(_("Got different Survey-IDs on different pages for one sheet!"))
                        warned_multipage_not_correctly_scanned = True

            if self.obj.survey_id != self.obj.survey.survey_id:
                # Broken survey ID ...
                log.warn(_("Got a wrong survey ID (%s, %i)! It is %s, but should be %i.") %
                         (self.obj.images[0].filename,
                          self.obj.images[0].tiff_page,
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
                             (image.filename, image.tiff_page))
                    failed_pages.add(page)

            self.duplex_copy_image_attr(failed_pages, "questionnaire_id")

            self.obj.questionnaire_id = self.obj.images[0].questionnaire_id
            for image in self.obj.images:
                if self.obj.questionnaire_id != image.questionnaire_id:
                    if not warned_multipage_not_correctly_scanned:
                        log.warn(_("Got different Questionnaire-IDs on different pages for in at least one sheet! Do *NOT* try to use filters on this!"))
                        warned_multipage_not_correctly_scanned = True

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
            if self.obj.questionnaire_id != image.questionnaire_id:
                log.warn(_('%s, %i: Global ID is different to an earlier page.') % \
                         (image.filename, image.tiff_page))

        # Done
        if failed_pages:
            self.obj.valid = 0

    def clean(self):
        for image in self.obj.images:
            image.recognize.clean()

    def duplex_copy_image_attr(self, failed_pages, attr):
        u"""If in duplex mode, this function will copy the given attribute
        from the image that defines it over to the one that does not.
        ie. if the attribute is None in one and differently in the other image
        it is copied.
        
        """

        if not self.obj.survey.defs.duplex:
            return

        i = 0
        while i < len(self.obj.images):
            failed = (i in failed_pages or i + 1 in failed_pages)

            first = self.obj.images[i]
            second = self.obj.images[i + 1]

            if getattr(first, attr) is None and getattr(second, attr) is None:
                # Nothing to do ...
                pass
            elif getattr(first, attr) is None:
                setattr(first, attr, getattr(second, attr))
            elif getattr(second, attr) is None:
                setattr(second, attr, getattr(first, attr))

            i += 2



class Image(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'recognize'
    obj_class = model.sheet.Image

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)

        if self.obj.sheet.survey.defs.style == "classic":
            import classic as style_funcs
        elif self.obj.sheet.survey.defs.style == "code128":
            import code128 as style_funcs
        else:
            raise AssertionError

        self.style_funcs = style_funcs

    def calculate_rotation(self):
        self.obj.rotated = self.style_funcs.get_page_rotation(self)

    def calculate_page_number(self):
        self.obj.page_number = self.style_funcs.get_page_number(self)

    def calculate_survey_id(self):
        self.obj.survey_id = self.style_funcs.get_survey_id(self)

    def calculate_questionnaire_id(self):
        self.obj.questionnaire_id = self.style_funcs.get_questionnaire_id(self)

    def calculate_global_id(self):
        self.obj.global_id = self.style_funcs.get_global_id(self)

    def clean(self):
        self.obj.surface.clean()

    def calculate_matrix(self):
        try:
            matrix = image.calculate_matrix(
                self.obj.surface.surface,
                self.obj.matrix.mm_to_px(),
                defs.corner_mark_left, defs.corner_mark_top,
                self.obj.sheet.survey.defs.paper_width - defs.corner_mark_left - defs.corner_mark_right,
                self.obj.sheet.survey.defs.paper_height - defs.corner_mark_top - defs.corner_mark_bottom,
            )
        except AssertionError:
            self.obj.matrix.set_px_to_mm(None)
            raise RecognitionError
        else:
            self.obj.matrix.set_px_to_mm(matrix)

    def get_coverage(self, x, y, width, height):
        return image.get_coverage(
            self.obj.surface.surface,
            self.matrix,
            x, y, width, height
        )

    def get_coverage_without_lines(self, x, y, width, height, line_width, line_count):
        return image.get_coverage_without_lines(
            self.obj.surface.surface,
            self.matrix,
            x, y, width, height,
            line_width, line_count
        )

    def get_white_area_count(self, x, y, width, height, min_size, max_size):
        return image.get_white_area_count(
            self.obj.surface.surface,
            self.matrix,
            x, y, width, height,
            min_size, max_size
        )

    def correction_matrix(self, x, y, width, height):
        return image.calculate_correction_matrix(
            self.obj.surface.surface,
            self.matrix,
            x, y,
            width, height
        )

    def find_box_corners(self, x, y, width, height):
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
        return self.obj.matrix.mm_to_px()

class Questionnaire(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'recognize'
    obj_class = model.questionnaire.Questionnaire

    def recognize(self):
        # recognize image
        try:
            self.obj.sheet.recognize.recognize()
        except RecognitionError:
            self.obj.sheet.quality = 0
        else:
            # iterate over qobjects
            for qobject in self.obj.qobjects:
                qobject.recognize.recognize()

            quality = 1
            for qobject in self.obj.qobjects:
                quality = min(quality, qobject.recognize.get_quality())
            self.obj.sheet.quality = quality

        # clean up
        self.obj.sheet.recognize.clean()


class QObject(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'recognize'
    obj_class = model.questionnaire.QObject

    def recognize(self):
        pass

    def get_quality(self):
        return 1


class Question(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
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

#class Choice(Question):

    #__metaclass__ = model.buddy.Register
    #name = 'recognize'
    #obj_class = model.questionnaire.Choice


#class Mark(Question):

    #__metaclass__ = model.buddy.Register
    #name = 'recognize'
    #obj_class = model.questionnaire.Mark


class Box(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'recognize'
    obj_class = model.questionnaire.Box

    def recognize(self):
        pass


class Checkbox(Box):

    __metaclass__ = model.buddy.Register
    name = 'recognize'
    obj_class = model.questionnaire.Checkbox

    def recognize(self):
        image = self.obj.sheet.get_page_image(self.obj.page_number)

        if image is None or image.recognize.matrix is None:
            self.obj.sheet.valid = 0
            return

        matrix = image.recognize.correction_matrix(
            self.obj.x, self.obj.y,
            self.obj.width, self.obj.height
        )
        x, y = matrix.transform_point(self.obj.x, self.obj.y)
        width, height = matrix.transform_distance(self.obj.width, self.obj.height)
        self.obj.data.x = x
        self.obj.data.y = y
        self.obj.data.width = width
        self.obj.data.height = height

        coverage = image.recognize.get_coverage(
            x + 1.5 * pt_to_mm, y + 1.5 * pt_to_mm,
            width - 3 * pt_to_mm, height - 3 * pt_to_mm)
        self.obj.data.metrics['coverage'] = coverage

        # Remove 3 lines with width 1.2pt(about 5px).
        coverage = image.recognize.get_coverage_without_lines(
            x + 1.5 * pt_to_mm, y + 1.5 * pt_to_mm,
            width - 3 * pt_to_mm, height - 3 * pt_to_mm,
            1.2 * 25.4 / 72.0, 3)
        self.obj.data.metrics['cov-lines-removed'] = coverage

        count, coverage = image.recognize.get_white_area_count(
            x + 1.5 * pt_to_mm, y + 1.5 * pt_to_mm,
            width - 3 * pt_to_mm, height - 3 * pt_to_mm,
            0.05, 1.0)
        self.obj.data.metrics['cov-min-size'] = coverage

        state = 0
        quality = -1
        # Iterate the ranges
        for metric, value in self.obj.data.metrics.iteritems():
            metric = defs.checkbox_metrics[metric]

            for lower, upper in zip(metric[:-1], metric[1:]):
                if value >= lower[0] and value < upper[0]:
                    # Interpolate quality value
                    metric_quality = lower[2] + (upper[2] - lower[2]) * (value - lower[0]) / (upper[0] - lower[0])

                    if metric_quality > quality:
                        state = lower[1]
                        quality = metric_quality

        self.obj.data.state = state
        self.obj.data.quality = quality


class Textbox(Box):

    __metaclass__ = model.buddy.Register
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
                for step in xrange(int(length / step_x)):
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
                for step in xrange(int(length / step_x)):
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
                for step in xrange(int(length / step_y)):
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
                for step in xrange(int(length / step_y)):
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
        image = self.obj.sheet.get_page_image(self.obj.page_number)

        if image is None or image.recognize.matrix is None:
            self.obj.sheet.valid = 0
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
            quad = Quadrilateral(*image.recognize.find_box_corners(x, y, width, height))
            # Lower padding, as we found the corners and are therefore more acurate
            scan_padding = defs.textbox_scan_padding
        except AssertionError:
            pass

        for x, y in quad.iterate(step_x, step_y, test_width, test_height, scan_padding):
            coverage = image.recognize.get_coverage(x, y, test_width, test_height)
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

