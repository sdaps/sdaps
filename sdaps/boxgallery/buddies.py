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

from sdaps import model
from sdaps import surface
from sdaps import matrix


class Sheet(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'boxgallery'
    obj_class = model.sheet.Sheet

    def load(self):
        for image in self.obj.images:
            if not image.ignored:
                image.surface.load()

    def clean(self):
        for image in self.obj.images:
            if not image.ignored:
                image.surface.clean()


class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'boxgallery'
    obj_class = model.questionnaire.Questionnaire

    def init(self, debugrecognition):
        self.checkboxes = list()
        self.debugrecognition = debugrecognition

    def clean(self):
        del self.checkboxes

    def get_checkbox_images(self):
        if self.obj.survey.sheet.valid:
            self.obj.survey.sheet.boxgallery.load()
            for qobject in self.obj.qobjects:
                self.checkboxes.extend(qobject.boxgallery.get_checkbox_images(self.debugrecognition))
            self.obj.survey.sheet.boxgallery.clean()


class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'boxgallery'
    obj_class = model.questionnaire.QObject

    def get_checkbox_images(self, debugrecognition):
        return []


class Question(QObject, metaclass=model.buddy.Register):

    name = 'boxgallery'
    obj_class = model.questionnaire.Question

    def get_checkbox_images(self, debugrecognition):
        boxes = []

        for box in self.obj.boxes:
            new_box = box.boxgallery.get_checkbox_image(debugrecognition)
            if new_box:
                boxes.append(new_box)
        return boxes


class Box(model.buddy.Buddy, metaclass=model.buddy.Register):
    name = 'boxgallery'
    obj_class = model.questionnaire.Box

    def get_checkbox_image(self, debugrecognition):
        return None


class Checkbox(model.buddy.Buddy, metaclass=model.buddy.Register):
    name = 'boxgallery'
    obj_class = model.questionnaire.Checkbox

    def get_checkbox_image(self, debugrecognition):
        image = self.obj.sheet.get_page_image(self.obj.page_number)

        border = 1.5
        mm_to_px = image.matrix.mm_to_px()

        px_x, px_y = mm_to_px.transform_point(
            self.obj.data.x - border, self.obj.data.y - border)
        px_x, px_y = int(px_x), int(px_y)
        px_width, px_height = mm_to_px.transform_distance(
            self.obj.data.width + 2 * border, self.obj.data.height + 2 * border)

        dest = cairo.ImageSurface(
            cairo.FORMAT_A1, int(px_width), int(px_height))
        src = image.surface.surface

        cr = cairo.Context(dest)
        cr.set_source_surface(src, -px_x, -px_y)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        del cr
        dest.flush()

        debug = {}
        if debugrecognition:
            # Run the recognition for this checkbox
            self.obj.recognize.recognize()

            debug = self.obj.recognize.debug

        return (self.obj.data.state, self.obj.data.metrics, (dest, px_x, px_y), debug)



