#!/usr/bin/env python
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2014, Michael Batchelor <batchelor@nationbuilder.com>
# Copyright(C) 2014, Chuck Collins <chuck@nationbuilder.com>
# Copyright(C) 2014, Jacob Green <jacob@nationbuilder.com>
# Copyright(C) 2014, Dustin Ngo <dustin@nationbuilder.com>
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
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
import os.path
import sys

code = sys.argv[1]
size = 65
filename = "barcode_%s.pdf" % str(code)
print "Barcode file: %s" % filename

if not os.path.exists(filename):
  c = canvas.Canvas(filename, pagesize=[size, size])

  # draw a QR code
  qr_code = qr.QrCodeWidget(str(code), barLevel='H')
  bounds = qr_code.getBounds()
  width = bounds[2] - bounds[0]
  height = bounds[3] - bounds[1]
  d = Drawing(size, size, transform=[float(size)/width,0,0,float(size)/height,0,0])
  d.add(qr_code)
  renderPDF.draw(d, c, 0, 0)
  c.save()
