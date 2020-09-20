# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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
from sdaps import defs
from sdaps import image
from sdaps.image import TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT

LINE_WIDTH = 25.4/72
MIN_FREETEXT_SIZE = 4.0

_LEFT = 1
_RIGHT = 2
_TOP = 3
_BOTTOM = 4


def inner_box(cr, x, y, width, height):
    line_width = cr.get_line_width()

    cr.rectangle(x + line_width / 2.0, y + line_width / 2.0,
                 width - line_width, height - line_width)

def ellipse(cr, x, y, width, height):
    cr.save()

    cr.translate(x + width / 2.0, y + height / 2.0)

    line_width = cr.get_line_width()

    cr.scale(width / 2.0, height / 2.0)
    cr.arc(0, 0, 1.0, 0, 2*math.pi)
    cr.close_path()

    # Restore old matrix (without removing the current path)
    cr.restore()

def inner_ellipse(cr, x, y, width, height):
    cr.save()

    cr.translate(x + width / 2.0, y + height / 2.0)

    line_width = cr.get_line_width()

    cr.scale((width - line_width) / 2.0, (height - line_width) / 2.0)
    cr.arc(0, 0, 1.0, 0, 2*math.pi)
    cr.close_path()

    # Restore old matrix (without removing the current path)
    cr.restore()

def centered_circle(cr, x, y, radius):
    inner_ellipse(cr, x - radius, y - radius, 2*radius, 2*radius)

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'gui'
    obj_class = model.questionnaire.Questionnaire

    def __init__(self, *args):
        self._fixed_points = [TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT]
        super().__init__(*args)

    def draw(self, cr, _image):
        cr.save()
        # Draw an outline for the content area
        cr.set_source_rgba(1.0, 0.0, 0.0, 0.6)
        cr.set_line_width(LINE_WIDTH)
        cr.rectangle(self.obj.survey.defs.corner_mark_left, self.obj.survey.defs.corner_mark_top,
                     self.obj.survey.defs.paper_width - self.obj.survey.defs.corner_mark_left - self.obj.survey.defs.corner_mark_right,
                     self.obj.survey.defs.paper_height - self.obj.survey.defs.corner_mark_top - self.obj.survey.defs.corner_mark_bottom)
        cr.stroke()

        # Draw draggable corner circles
        cr.set_source_rgba(0.0, 0.0, 1.0, 0.6)
        centered_circle(cr, self.obj.survey.defs.corner_mark_left, self.obj.survey.defs.corner_mark_top, 5*LINE_WIDTH)
        if TOP_LEFT in self._fixed_points:
            cr.fill()
        else:
            cr.stroke()
        centered_circle(cr, self.obj.survey.defs.paper_width - self.obj.survey.defs.corner_mark_right, self.obj.survey.defs.corner_mark_top, 5*LINE_WIDTH)
        if TOP_RIGHT in self._fixed_points:
            cr.fill()
        else:
            cr.stroke()
        centered_circle(cr, self.obj.survey.defs.corner_mark_left, self.obj.survey.defs.paper_height - self.obj.survey.defs.corner_mark_bottom, 5*LINE_WIDTH)
        if BOTTOM_LEFT in self._fixed_points:
            cr.fill()
        else:
            cr.stroke()
        centered_circle(cr, self.obj.survey.defs.paper_width - self.obj.survey.defs.corner_mark_right, self.obj.survey.defs.paper_height - self.obj.survey.defs.corner_mark_bottom, 5*LINE_WIDTH)
        if BOTTOM_RIGHT in self._fixed_points:
            cr.fill()
        else:
            cr.stroke()

        cr.restore()

        for qobject in self.obj.qobjects:
            qobject.gui.draw(cr, _image.page_number)

    def find_box(self, _image, x, y):
        for qobject in self.obj.qobjects:
            result = qobject.gui.find_box(_image.page_number, x, y)
            if result:
                return result
        return None

    def find_edge(self, _image, x, y, tollerance_x, tollerance_y):
        # Not technically edges, but first try to find the corner circles
        corner = -1
        if math.sqrt((x - self.obj.survey.defs.corner_mark_left) ** 2 +
                     (y - self.obj.survey.defs.corner_mark_top) ** 2) < 5 * LINE_WIDTH + tollerance_x:
            corner = TOP_LEFT

        if math.sqrt((x + self.obj.survey.defs.corner_mark_right - self.obj.survey.defs.paper_width) ** 2 +
                     (y - self.obj.survey.defs.corner_mark_top) ** 2) < 5 * LINE_WIDTH + tollerance_x:
            corner = TOP_RIGHT

        if math.sqrt((x - self.obj.survey.defs.corner_mark_left) ** 2 +
                     (y + self.obj.survey.defs.corner_mark_bottom - self.obj.survey.defs.paper_height) ** 2) < 5 * LINE_WIDTH + tollerance_x:
            corner = BOTTOM_LEFT

        if math.sqrt((x + self.obj.survey.defs.corner_mark_right - self.obj.survey.defs.paper_width) ** 2 +
                     (y + self.obj.survey.defs.corner_mark_bottom - self.obj.survey.defs.paper_height) ** 2) < 5 * LINE_WIDTH + tollerance_x:
            corner = BOTTOM_RIGHT

        if corner > -1:
            try:
                self._fixed_points.remove(corner)
            except:
                pass
            self._fixed_points = [corner] + self._fixed_points[:2]

            return (self.obj, (_image, corner))

        for qobject in self.obj.qobjects:
            result = qobject.gui.find_edge(_image.page_number, x, y, tollerance_x, tollerance_y)
            if result:
                return result
        return None

    def move_edge(self, args, x, y):
        # Corner was moved, we need to update the matrix in a way to fit the
        # moved point and the other three "fixed" points
        # This is largely copy of the calculation in image.c calculate_matrix()

        _image, corner = args

        corners = [None, None, None, None]
        if TOP_LEFT in self._fixed_points:
            corners[TOP_LEFT] = (self.obj.survey.defs.corner_mark_left, self.obj.survey.defs.corner_mark_top)
        if TOP_RIGHT in self._fixed_points:
            corners[TOP_RIGHT] = (self.obj.survey.defs.paper_width - self.obj.survey.defs.corner_mark_right, self.obj.survey.defs.corner_mark_top)
        if BOTTOM_LEFT in self._fixed_points:
            corners[BOTTOM_LEFT] = (self.obj.survey.defs.corner_mark_left, self.obj.survey.defs.paper_height - self.obj.survey.defs.corner_mark_bottom)
        if BOTTOM_RIGHT in self._fixed_points:
            corners[BOTTOM_RIGHT] = (self.obj.survey.defs.paper_width - defs.corner_mark_right, self.obj.survey.defs.paper_height - defs.corner_mark_bottom)

        # Put in the location of the corner that is being adjusted
        corners[corner] = (x, y)

        # Transform each corner into pixel space
        m = _image.matrix.mm_to_px()
        corners = [m.transform_point(*c) if c is not None else None for c in corners]

        # Useful constants
        mm_x = self.obj.survey.defs.corner_mark_left
        mm_width = self.obj.sheet.survey.defs.paper_width - self.obj.survey.defs.corner_mark_left - self.obj.survey.defs.corner_mark_right
        mm_y = self.obj.survey.defs.corner_mark_top
        mm_height = self.obj.sheet.survey.defs.paper_height - self.obj.survey.defs.corner_mark_top - self.obj.survey.defs.corner_mark_bottom

        m = image.matrix_from_corners_2d(corners, mm_x, mm_y, mm_width, mm_height)
        _image.matrix.set_px_to_mm(m)

class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'gui'
    obj_class = model.questionnaire.QObject

    def draw(self, cr, page_number):
        pass

    def find_box(self, page_number, x, y):
        pass

    def find_edge(self, page_number, x, y, tollerance_x, tollerance_y):
        return None


class Question(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'gui'
    obj_class = model.questionnaire.Question

    def draw(self, cr, page_number):
        # Does the sheet contain this question?
        if page_number == self.obj.page_number:
            # iterate over boxes
            for box in self.obj.boxes:
                box.gui.draw(cr)

    def find_box(self, page_number, x, y):
        # Does the sheet contain this question?
        if page_number == self.obj.page_number:
            # iterate over boxes
            for box in self.obj.boxes:
                result = box.gui.find(x, y)
                if result is not None:
                    return result
        return None

    def find_edge(self, page_number, x, y, tollerance_x, tollerance_y):
        # Does the sheet contain this question?
        if page_number == self.obj.page_number:
            # iterate over boxes
            for box in self.obj.boxes:
                result = box.gui.find_edge(x, y, tollerance_x, tollerance_y)
                if result is not None:
                    return result
        return None


class Box(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'gui'
    obj_class = model.questionnaire.Checkbox

    def draw(self, cr):
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)

        cr.set_source_rgba(0.57, 1.0, 0.0, 0.5)
        cr.set_line_width(self.obj.lw)

        inner_box(cr, self.obj.data.x, self.obj.data.y, self.obj.data.width, self.obj.data.height)
        cr.stroke()

    def find(self, x, y):
        if self.obj.data.x < x < self.obj.data.x + self.obj.data.width:
            if self.obj.data.y < y < self.obj.data.y + self.obj.data.height:
                return self.obj
        return None

    def find_edge(self, x, y, tollerance_x, tollerance_y):
        return None


class Checkbox(Box, metaclass=model.buddy.Register):

    name = 'gui'
    obj_class = model.questionnaire.Checkbox

    def find(self, x, y):
        if self.obj.data.x - 2*LINE_WIDTH < x < self.obj.data.x + self.obj.data.width + 2*LINE_WIDTH:
            if self.obj.data.y - 2*LINE_WIDTH < y < self.obj.data.y + self.obj.data.height + 2*LINE_WIDTH:
                return self.obj
        return None


    def draw(self, cr):
        cr.save()

        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)

        if self.obj.data.quality < 0.5:
            cr.save()
            cr.set_line_width(2*LINE_WIDTH)
            cr.set_source_rgba(1.0, 0.0, 0.2, 0.6)

            if self.obj.form == "box":
                inner_box(cr, self.obj.data.x - 4*LINE_WIDTH, self.obj.data.y - 4*LINE_WIDTH,  self.obj.data.width+8*LINE_WIDTH, self.obj.data.height+8*LINE_WIDTH)
                cr.stroke()
            elif self.obj.form == "ellipse":
                inner_ellipse(cr, self.obj.data.x - 4*LINE_WIDTH, self.obj.data.y - 4*LINE_WIDTH,  self.obj.data.width+8*LINE_WIDTH, self.obj.data.height+8*LINE_WIDTH)
                cr.stroke()

            cr.restore()

        cr.set_source_rgba(0.57, 1.0, 0.0, 0.5)
        cr.set_line_width(self.obj.lw)

        if self.obj.data.state:
            if self.obj.form == "box":
                cr.rectangle(self.obj.data.x - 2*LINE_WIDTH, self.obj.data.y - 2*LINE_WIDTH, self.obj.data.width + 4*LINE_WIDTH, self.obj.data.height + 4*LINE_WIDTH)
                cr.fill()
            elif self.obj.form == "ellipse":
                ellipse(cr, self.obj.data.x - 2*LINE_WIDTH, self.obj.data.y - 2*LINE_WIDTH, self.obj.data.width + 4*LINE_WIDTH, self.obj.data.height + 4*LINE_WIDTH)
                cr.fill()
        else:
            if self.obj.form == "box":
                inner_box(cr, self.obj.data.x, self.obj.data.y, self.obj.data.width, self.obj.data.height)
                cr.stroke()
            elif self.obj.form == "ellipse":
                inner_ellipse(cr, self.obj.data.x, self.obj.data.y, self.obj.data.width, self.obj.data.height)
                cr.stroke()

        cr.restore()


class Textbox(Box, metaclass=model.buddy.Register):

    name = 'gui'
    obj_class = model.questionnaire.Textbox

    def draw(self, cr):
        cr.save()

        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)

        cr.set_source_rgba(0.57, 1.0, 0.0, 0.5)

        if self.obj.data.state:
            cr.set_line_width(2 * LINE_WIDTH + self.obj.lw)
        else:
            cr.set_line_width(self.obj.lw)

        inner_box(cr, self.obj.data.x, self.obj.data.y, self.obj.data.width, self.obj.data.height)
        cr.stroke()

        cr.restore()

    def find_edge(self, x, y, tollerance_x, tollerance_y):
        if self.obj.data.x - tollerance_x <= x and \
           self.obj.data.x + tollerance_x >= x and \
           self.obj.data.y <= y and \
           self.obj.data.y + self.obj.data.height >= y:
            return(self.obj, _LEFT)

        if self.obj.data.x + self.obj.data.width - tollerance_x <= x and \
           self.obj.data.x + self.obj.data.width + tollerance_x >= x and \
           self.obj.data.y <= y and \
           self.obj.data.y + self.obj.data.height >= y:
            return(self.obj, _RIGHT)

        if self.obj.data.y - tollerance_y <= y and \
           self.obj.data.y + tollerance_y >= y and \
           self.obj.data.x <= x and \
           self.obj.data.x + self.obj.data.width >= x:
            return(self.obj, _TOP)

        if self.obj.data.y + self.obj.data.height - tollerance_y <= y and \
           self.obj.data.y + self.obj.data.height + tollerance_y >= y and \
           self.obj.data.x <= x and \
           self.obj.data.x + self.obj.data.width >= x:
            return(self.obj, _BOTTOM)

    def move_edge(self, side, x, y):
        if side == _LEFT:
            x = max(x, self.obj.survey.defs.corner_mark_left)
            new_width = max(MIN_FREETEXT_SIZE, self.obj.data.width + self.obj.data.x - x)
            x = self.obj.data.x + (self.obj.data.width - new_width)

            self.obj.data.width = new_width
            self.obj.data.x = x
        elif side == _RIGHT:
            x = min(x, self.obj.question.questionnaire.survey.defs.paper_width - self.obj.survey.defs.corner_mark_right)
            new_width = max(MIN_FREETEXT_SIZE, x - self.obj.data.x)
            new_width = min(new_width, self.obj.data.x + self.obj.data.width)

            self.obj.data.width = new_width
        elif side == _TOP:
            y = max(y, self.obj.survey.defs.corner_mark_top)
            new_height = max(MIN_FREETEXT_SIZE, self.obj.data.height + self.obj.data.y - y)
            new_y = self.obj.data.y + (self.obj.data.height - new_height)

            self.obj.data.height = new_height
            self.obj.data.y = new_y
        elif side == _BOTTOM:
            y = min(y, self.obj.question.questionnaire.survey.defs.paper_height - self.obj.survey.defs.corner_mark_bottom)
            new_height = max(MIN_FREETEXT_SIZE, y - self.obj.data.y)

            self.obj.data.height = new_height


