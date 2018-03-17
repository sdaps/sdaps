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

import math

from reportlab import pdfgen
from reportlab import platypus
from reportlab.lib import styles
from reportlab.lib import units
from reportlab.lib import pagesizes
from reportlab.lib import enums

from sdaps import template


mm = units.mm

stylesheet = template.stylesheet

stylesheet['Right'] = styles.ParagraphStyle(
    'Right',
    parent=stylesheet['Normal'],
    alignment=enums.TA_RIGHT,
)


class Box(platypus.Flowable):
    '''3d box
    '''

    def __init__(self, a, b, c, margin=0):
        platypus.Flowable.__init__(self)
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.margin = float(margin)
        self.alpha = 1.0 / 3.0 * math.pi
        self.cx = math.sin(self.alpha) * self.c
        self.cy = math.cos(self.alpha) * self.c
        self.fill = 0
        self.transparent = 1
        self.fill_color = (255, 255, 255)

    def wrap(self, available_width, available_height):
        self.width = self.a + self.cx
        self.height = self.b + self.cy + 2 * self.margin
        return self.width, self.height

    def draw(self):
        if 0:
            assert isinstance(self.canv, pdfgen.canvas.Canvas)
        self.canv.setLineJoin(1)
        self.canv.setLineWidth(0.2)
        self.canv.setFillColorRGB(*self.fill_color)
        # back
        if self.transparent:
            self.draw_front(self.cx, self.margin + self.cy)
        # left side
        if self.transparent:
            self.draw_side(0, self.margin)
        # bottom
        if self.transparent:
            self.draw_top(0, self.margin)
        # right side
        self.draw_side(self.a, self.margin)
        # top
        self.draw_top(0, self.margin + self.b)
        # front
        self.draw_front(0, self.margin)

    def draw_side(self, x, y):
        path = self.canv.beginPath()
        path.moveTo(x, y)
        path.lineTo(x + self.cx, y + self.cy)
        path.lineTo(x + self.cx, y + self.cy + self.b)
        path.lineTo(x, y + self.b)
        path.lineTo(x, y)
        self.canv.drawPath(path, fill=self.fill)

    def draw_top(self, x, y):
        path = self.canv.beginPath()
        path.moveTo(x, y)
        path.lineTo(x + self.a, y)
        path.lineTo(x + self.a + self.cx, y + self.cy)
        path.lineTo(x + self.cx, y + self.cy)
        path.lineTo(x, y)
        self.canv.drawPath(path, fill=self.fill)

    def draw_front(self, x, y):
        path = self.canv.beginPath()
        path.moveTo(x, y)
        path.lineTo(x + self.a, y)
        path.lineTo(x + self.a, y + self.b)
        path.lineTo(x, y + self.b)
        path.lineTo(x, y)
        self.canv.drawPath(path, fill=self.fill)


#class ChoiceBar(platypus.Flowable):

    #def __init__(self, value):
        #platypus.Flowable.__init__(self)
        #self.a = 200
        #self.b = 12
        #self.depth_x = 6
        #self.depth_y = 3
        #self.value = value

    #def wrap(self, available_width, available_height):
        #self.width = self.a + self.depth_x
        #self.height = self.height + self.depth_y
        #return self.width, self.height

    #def draw(self):
        #if 0: assert isinstance(self.canv, pdfgen.canvas.Canvas)
        #self.canv.setLineJoin(1)
        #self.canv.setLineWidth(0.1)
        #self.canv.setFillGray(0.5)
        ## filling
        #self.draw_side(self.value, 1)
        #self.draw_top(self.value, 1)
        #self.draw_front(self.value, 1)
        ## line
        #self.canv.line(self.a * self.value,                0,            self.a,                0)
        #self.canv.line(self.a * self.value + self.depth_x, self.depth_y, self.a + self.depth_x, self.depth_y)
        #self.canv.line(self.a * self.value,                self.b,                self.a,                self.b)
        #self.canv.line(self.a * self.value + self.depth_x, self.b + self.depth_y, self.a + self.depth_x, self.b + self.depth_y)
        ## bar
        #self.draw_side(1, 0)

    #def draw_front(self, value, fill):
        #path = self.canv.beginPath()
        #path.moveTo(0, 0)
        #path.lineTo(self.a * value, 0)
        #path.lineTo(self.a * value, self.b)
        #path.lineTo(0, self.b)
        #path.lineTo(0, 0)
        #self.canv.drawPath(path, fill=fill)

    #def draw_top(self, value, fill):
        #path = self.canv.beginPath()
        #path.moveTo(0, self.b)
        #path.lineTo(self.a * value, self.b)
        #path.lineTo(self.a * value + self.depth_x, self.b + self.depth_y)
        #path.lineTo(self.depth_x, self.b + self.depth_y)
        #path.lineTo(0, self.b)
        #self.canv.drawPath(path, fill=fill)

    #def draw_side(self, value, fill):
        #path = self.canv.beginPath()
        #path.moveTo(self.a * value, 0)
        #path.lineTo(self.a * value, self.b)
        #path.lineTo(self.a * value + self.depth_x, self.b + self.depth_y)
        #path.lineTo(self.a * value + self.depth_x, self.depth_y)
        #path.lineTo(self.a * value, 0)
        #self.canv.drawPath(path, fill=fill)


#class ChoiceAnswer(platypus.Flowable):

    #def __init__(self, answer, value):
        #platypus.Flowable.__init__(self)
        #self.answer = platypus.Paragraph(answer, template.stylesheet['Right'])
        #self.value = platypus.Paragraph(u'%.2f %%' %(value * 100), template.stylesheet['Right'])
        #self.bar = ChoiceBar(value)
        #self.gap = 3
        #self.value_width = 42

    #def wrap(self, available_width, available_height):
        #self.width = available_width
        #self.bar.wrap(self.width, available_height)
        #available_width -= self.bar.width
        #available_width -= self.gap
        #self.value.wrap(self.value_width, available_height)
        #available_width -= self.value.width
        #self.answer.wrap(available_width, available_height)
        #self.height = max(self.answer.height, self.bar.height, self.value.height)
        #return self.width, self.height


    #def draw(self):
        #if 0: assert isinstance(self.canv, pdfgen.canvas.Canvas)
        #self.answer.drawOn(self.canv, 0, 0)
        #self.value.drawOn(self.canv, self.answer.width, 0)
        #self.bar.drawOn(self.canv, self.answer.width + self.value.width + self.gap, 0)

#class MarkAnswer(platypus.Flowable):

    #def __init__(self):
        #platypus.Flowable.__init__(self)
        #self.box_width = 40
        #self.box_height = 60
        #self.box_depth = 6
        #self.mean_width = 2
        #self.mean_height = 6
        #self.margin = 6
        ##self.values = [0.2, 0.20, 0.2, 0.20, 0.20]
        #self.values = [0.25, 0.10, 0.35, 0.20, 0.10]
        #self.mean = sum([(mark + 1) * value for mark, value in enumerate(self.values)])


    #def wrap(self, available_width, available_height):
        #self.width = available_width #self.box_width * 5
        #self.offset = self.width - self.box_width * 5 - self.margin
        #self.height = max(self.values) * self.box_height + self.mean_height
        #return self.width, self.height

    #def draw(self):
        #if 0: assert isinstance(self.canv, pdfgen.canvas.Canvas)
        #self.canv.setLineJoin(1)
        #self.canv.setLineWidth(0.1)
        #self.canv.setFillGray(0.5)
        ## mean
        #Box(self.mean_width, self.mean_height, self.box_depth).drawOn(self.canv, self.offset +(self.mean - 0.5) * self.box_width - self.mean_width / 2.0, 0)
        ## boxes
        #for i, value in enumerate(self.values):
            #Box(self.box_width, value * self.box_height, self.box_depth).drawOn(self.canv, self.offset + i * self.box_width, self.mean_height)
        ## skala
        #for i in range(41):
            #if i % 10 == 0:
                #self.canv.setLineWidth(0.2)
                #self.canv.line(self.offset +(i / 10.0 + 0.5) * self.box_width, 1, self.offset +(i / 10.0 + 0.5) * self.box_width, 5)
            #elif i % 5 == 0:
                #self.canv.line(self.offset +(i / 10.0 + 0.5) * self.box_width, 1.5, self.offset +(i / 10.0 + 0.5) * self.box_width, 4.5)
            #else:
                #self.canv.line(self.offset +(i / 10.0 + 0.5) * self.box_width, 2, self.offset +(i / 10.0 + 0.5) * self.box_width, 4)
            #if i % 10 == 0:
                #self.canv.setLineWidth(0.1)


