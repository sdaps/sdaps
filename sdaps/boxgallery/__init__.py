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
from gi.repository import Pango
from gi.repository import PangoCairo

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

import copy
from . import buddies


def paint_box(cr, mm_to_pt, x, y, box, key):
    cr.save()
    cr.set_matrix(mm_to_pt)
    cr.translate(x, y)

    cr.scale(25.4 / 300.0, 25.4 / 300.0)

    cr.set_source_rgb(0, 0, 0)
    cr.mask_surface(box[2][0], 0, 0)

    if box[3] and key in box[3] and box[3][key] is not None:
        cr.set_source_surface(box[3][key][0], box[3][key][1] - box[2][1], box[3][key][2] - box[2][2])
        cr.paint()

    cr.restore()

    cr.save()

    tmp_x, tmp_y = mm_to_pt.transform_point(x, y)
    tmp_width, tmp_height = mm_to_pt.transform_distance(8, 13)

    tmp_x, tmp_y = mm_to_pt.transform_point(x, y + 8.0)
    # Print bold if detected ON
    value = box[1][key] if key in box[1] else -1
    if box[0]:
        t = "<b>%.2f</b>" % value
    else:
        t = "%.2f" % value

    cr.move_to(tmp_x, tmp_y)

    layout = PangoCairo.create_layout(cr)
    layout.set_markup(t, -1)
    font = Pango.FontDescription("serif 6")
    layout.set_font_description(font)

    PangoCairo.show_layout(cr, layout)

    cr.restore()


def fill_page(cr, mm_to_pt, checkboxes, key):
    y = 15
    y_step = 13
    x_step = 10
    x_max = 210 - 15 - 8
    y_max = 297 - 15 - 8

    while y < y_max:
        x = 15
        while x < x_max:

            if len(checkboxes) == 0:
                return
            box = checkboxes.pop(0)

            paint_box(cr, mm_to_pt, x, y, box, key)

            x += x_step
        y += y_step


def boxgallery(survey, debugrecognition):
    # Enable debug image creation in the C module
    if debugrecognition:
        from sdaps import image
        image.enable_debug_surface_creation(True)

    survey.questionnaire.boxgallery.init(debugrecognition)
    survey.iterate_progressbar(survey.questionnaire.boxgallery.get_checkbox_images)
    checkboxes = survey.questionnaire.boxgallery.checkboxes
    survey.questionnaire.boxgallery.clean()

    keys = set()
    for checkbox in checkboxes:
        keys = keys.union(iter(checkbox[1].keys()))

    for key in keys:
        print(_("Rendering boxgallery for metric \"%s\"." % key))
        draw_list = copy.copy(checkboxes)
        draw_list.sort(key=lambda x: x[1][key] if key in x[1] else 0)

        # Hardcode 300dpi
        # Hardcode the mm size:
        # 3.5 + 0.4mm = 3.9mm
        mm_to_pt = cairo.Matrix(72.0 / 25.4, 0, 0, 72.0 / 25.4, 0, 0)

        page = 1
        pdf = cairo.PDFSurface(survey.path('boxgallery-%s.pdf' % key), 595, 842)
        cr = cairo.Context(pdf)

        while len(draw_list) > 0:
            fill_page(cr, mm_to_pt, draw_list, key)
            cr.show_page()
            pdf.flush()

            page += 1

        del pdf
        del cr

