# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, 2013, Benjamin Berg <benjamin@sipsolutions.net>
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

# This file duplicates some drawing code from the gui module.

from gi.repository import Pango
from gi.repository import PangoCairo
import cairo
import math

from sdaps import model
from sdaps import defs

colorcycle_pos = 0
colorcycle = [(1, 0, 0), (0.5, 0.5, 0), (0, 0.5, 0.5), (0.5, 0, 0.5)]

LINE_WIDTH = 25.4/72
MIN_FREETEXT_SIZE = 4.0

def cycle_color():
    global colorcycle_pos
    colorcycle_pos = (colorcycle_pos + 1) % len(colorcycle)

def set_rgb_from_color_cycle(cr):
    global colorcycle_pos, colorcycle
    cr.set_source_rgba(*(colorcycle[colorcycle_pos] + (0.5,)))

def inner_box(cr, x, y, width, height):
    line_width = cr.get_line_width()

    cr.rectangle(x + line_width / 2.0, y + line_width / 2.0,
                 width - line_width, height - line_width)

def inner_ellipse(cr, x, y, width, height):
    cr.save()

    cr.translate(x + width / 2.0, y + height / 2.0)

    line_width = cr.get_line_width()

    cr.scale((width - line_width) / 2.0, (height - line_width) / 2.0)
    cr.arc(0, 0, 1.0, 0, 2*math.pi)

    # Restore old matrix (without removing the current path)
    cr.restore()

def create_layout(cr, text, layout_info, indent=0):
    layout = PangoCairo.create_layout(cr)
    text = text.encode('utf-8')
    layout.set_text(text, len(text))
    # Dont recreate the description all the time?
    font = Pango.FontDescription(layout_info['font'])
    layout.set_font_description(font)
    layout.set_width(layout_info['twidth'] * Pango.SCALE)
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)

    layout.indent = indent

    return layout

def show_layout(cr, layout, layout_info, skip=1.25):
    x, y = layout_info['xshift'] + layout.indent, layout_info['ypos'] + skip
    cr.move_to(x, y)

    cr.set_source_rgb(0, 0, 0)
    PangoCairo.show_layout(cr, layout)

    layout_info['ypos'] = layout_info['ypos'] + layout.get_pixel_size()[1] + skip

    # Return the position of the baseline
    y += layout.get_baseline() / Pango.SCALE

    return x, y

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.Questionnaire

    def draw(self, cr, page_number, layout_info):
        cr.set_source_rgba(0.0, 0.0, 1.0, 0.5)
        cr.set_line_width(LINE_WIDTH)

        # Draw corner marks.
        cr.move_to(defs.corner_mark_left + defs.corner_mark_length, defs.corner_mark_top)
        cr.line_to(defs.corner_mark_left, defs.corner_mark_top)
        cr.line_to(defs.corner_mark_left, defs.corner_mark_top+defs.corner_mark_length)

        cr.move_to(self.obj.survey.defs.paper_width - defs.corner_mark_right - defs.corner_mark_length, defs.corner_mark_top)
        cr.line_to(self.obj.survey.defs.paper_width - defs.corner_mark_right, defs.corner_mark_top)
        cr.line_to(self.obj.survey.defs.paper_width - defs.corner_mark_right, defs.corner_mark_top + defs.corner_mark_length)

        cr.move_to(defs.corner_mark_left + defs.corner_mark_length, self.obj.survey.defs.paper_height - defs.corner_mark_bottom)
        cr.line_to(defs.corner_mark_left, self.obj.survey.defs.paper_height - defs.corner_mark_top)
        cr.line_to(defs.corner_mark_left, self.obj.survey.defs.paper_height - defs.corner_mark_top - defs.corner_mark_length)

        cr.move_to(self.obj.survey.defs.paper_width - defs.corner_mark_right - defs.corner_mark_length, self.obj.survey.defs.paper_height - defs.corner_mark_top)
        cr.line_to(self.obj.survey.defs.paper_width - defs.corner_mark_right, self.obj.survey.defs.paper_height - defs.corner_mark_top)
        cr.line_to(self.obj.survey.defs.paper_width - defs.corner_mark_right, self.obj.survey.defs.paper_height - defs.corner_mark_top - defs.corner_mark_length)

        cr.stroke()

        for qobject in self.obj.qobjects:
            cycle_color()
            qobject.annotate.draw(cr, page_number, layout_info)


class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.QObject

    def draw(self, cr, page_number, layout_info):
        pass


class Head(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.Head

    def draw(self, cr, page_number, layout_info):
        # There is no page number for head objects.
        layout = create_layout(cr, self.obj.id_str() + " " + self.obj.title, layout_info)
        xpos, ypos = show_layout(cr, layout, layout_info)


class Question(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.Question

    def draw(self, cr, page_number, layout_info):
        # Does the sheet contain this question?
        if page_number == self.obj.page_number:
            layout = create_layout(cr, self.obj.id_str() + " " + self.obj.question, layout_info, 3)
            xpos, ypos = show_layout(cr, layout, layout_info, 3)

            # iterate over boxes
            for box in self.obj.boxes:
                box.annotate.draw(cr, layout_info)

class Range(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.Range

    def draw(self, cr, page_number, layout_info):
        # Does the sheet contain this question?
        if page_number == self.obj.page_number:
            layout = create_layout(cr, self.obj.id_str() + " " + self.obj.question, layout_info, 3)
            xpos, ypos = show_layout(cr, layout, layout_info, 3)

            # Lower range
            layout = create_layout(cr, self.obj.answers[0], layout_info, 10)
            xpos, ypos = show_layout(cr, layout, layout_info, 3)

            cr.move_to(self.obj.boxes[self.obj.range[0]].x, self.obj.boxes[self.obj.range[0]].y)
            cr.line_to(xpos, ypos)
            cr.set_line_width(LINE_WIDTH)
            set_rgb_from_color_cycle(cr)
            cr.stroke()

            # Upper range
            layout = create_layout(cr, self.obj.answers[1], layout_info, 10)
            xpos, ypos = show_layout(cr, layout, layout_info, 3)

            cr.move_to(self.obj.boxes[self.obj.range[1]].x, self.obj.boxes[self.obj.range[1]].y)
            cr.line_to(xpos, ypos)
            cr.set_line_width(LINE_WIDTH)
            set_rgb_from_color_cycle(cr)
            cr.stroke()

            for i, box in enumerate(self.obj.boxes):
                hide_if_empty = (self.obj.range[0] <= i <= self.obj.range[1])

                box.annotate.draw(cr, layout_info, hide_if_empty=hide_if_empty)

class Box(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.Checkbox

    def draw_box(self, cr):
        inner_box(cr, self.obj.x, self.obj.y, self.obj.width, self.obj.height)
        cr.stroke()

    def draw(self, cr, layout_info, hide_if_empty=False):
        if not hide_if_empty or self.obj.text:
            layout = create_layout(cr, self.obj.id_str() + " " + self.obj.text, layout_info, 6)
            xpos, ypos = show_layout(cr, layout, layout_info)

            cr.move_to(self.obj.x, self.obj.y)
            cr.line_to(xpos, ypos)
            cr.set_line_width(LINE_WIDTH)
            set_rgb_from_color_cycle(cr)
            cr.stroke()

        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)

        cr.set_source_rgba(0.0, 0.0, 1.0, 0.5)
        cr.set_line_width(LINE_WIDTH)

        self.draw_box(cr)

        text = str(self.obj.id[-1])
        layout = PangoCairo.create_layout(cr)
        layout.set_text(text, len(text))
        # Dont recreate the description all the time?
        font = Pango.FontDescription(layout_info['boxfont'])
        layout.set_font_description(font)

        cr.move_to(self.obj.x + LINE_WIDTH, self.obj.y + LINE_WIDTH)
        PangoCairo.show_layout(cr, layout)
        cr.new_path()


class Checkbox(Box, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.Checkbox

    def draw_box(self, cr):
        if self.obj.form == "box":
            inner_box(cr, self.obj.x, self.obj.y, self.obj.width, self.obj.height)
            cr.stroke()
        elif self.obj.form == "ellipse":
            inner_ellipse(cr, self.obj.x, self.obj.y, self.obj.width, self.obj.height)
            cr.stroke()



class Textbox(Box, metaclass=model.buddy.Register):

    name = 'annotate'
    obj_class = model.questionnaire.Textbox


