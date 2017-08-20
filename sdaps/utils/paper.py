# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2013, Benjamin Berg <benjamin@sipsolutions.net>
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

_fallback = "A4", (210., 297.)

def _get_gtk_ppd_papersize(paper=None):
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
    except:
        return paper, None
    else:
        def _find_papersize_by_ppd_name(paper=None):
            if not paper:
                return None

            paper = paper.lower()
            for papersize in Gtk.PaperSize.get_paper_sizes(False):
                if paper == papersize.get_ppd_name().lower():
                    return papersize

        papersize = _find_papersize_by_ppd_name(paper)
        if papersize is None:
            # Retrieve default paper size
            paper_name = Gtk.PaperSize.get_default()
            papersize = Gtk.PaperSize.new(paper_name)

        width = papersize.get_width(Gtk.Unit.MM)
        height = papersize.get_height(Gtk.Unit.MM)

        return papersize.get_ppd_name(), (width, height)

def get_tex_papersize(paper=None):
    # Assume that the name is the PPD name in lowercase + 'paper'
    paper, size = _get_gtk_ppd_papersize(paper)

    if paper is None:
        paper = _fallback[0]

    return paper.lower() + 'paper'

def get_reportlab_papersize(paper=None):
    paper, size = _get_gtk_ppd_papersize(paper)

    if size:
        size = (size[0] / 25.4 * 72.0, size[1] / 25.4 * 72.0)

    if size is None:
        if paper:
            from reportlab.lib import pagesizes
            if hasattr(pagesizes, paper.upper()):
                size = getattr(pagesizes, paper.upper())

    if size is None:
        size = (_fallback[1][0] / 25.4 * 72.0, _fallback[1][1] / 25.4 * 72.0)

    return size
