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

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'gui'
    obj_class = model.questionnaire.Questionnaire

    def draw(self, cr, page_number):
        for qobject in self.obj.qobjects:
            qobject.gui.draw(cr, page_number)

    def find_box(self, page_number, x, y):
        for qobject in self.obj.qobjects:
            result = qobject.gui.find_box(page_number, x, y)
            if result:
                return result
        return None

    def find_edge(self, page_number, x, y, tollerance_x, tollerance_y):
        for qobject in self.obj.qobjects:
            result = qobject.gui.find_edge(page_number, x, y, tollerance_x, tollerance_y)
            if result:
                return result
        return None


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
            x = max(x, defs.corner_mark_left)
            new_width = max(MIN_FREETEXT_SIZE, self.obj.data.width + self.obj.data.x - x)
            x = self.obj.data.x + (self.obj.data.width - new_width)

            self.obj.data.width = new_width
            self.obj.data.x = x
        elif side == _RIGHT:
            x = min(x, self.obj.question.questionnaire.survey.defs.paper_width - defs.corner_mark_right)
            new_width = max(MIN_FREETEXT_SIZE, x - self.obj.data.x)
            new_width = min(new_width, self.obj.data.x + self.obj.data.width)

            self.obj.data.width = new_width
        elif side == _TOP:
            y = max(y, defs.corner_mark_top)
            new_height = max(MIN_FREETEXT_SIZE, self.obj.data.height + self.obj.data.y - y)
            new_y = self.obj.data.y + (self.obj.data.height - new_height)

            self.obj.data.height = new_height
            self.obj.data.y = new_y
        elif side == _BOTTOM:
            y = min(y, self.obj.question.questionnaire.survey.defs.paper_height - defs.corner_mark_bottom)
            new_height = max(MIN_FREETEXT_SIZE, y - self.obj.data.y)

            self.obj.data.height = new_height


