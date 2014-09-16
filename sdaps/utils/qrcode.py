from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
import os.path

def create_qr_code(code, size=50, barcode_path="/tmp"):
    filename = "%s/barcode_%s.pdf" % (barcode_path, str(code))

    if not os.path.exists(filename):
      c = canvas.Canvas(filename, pagesize=[size, size])

      # draw a QR code
      qr_code = qr.QrCodeWidget(str(code))
      bounds = qr_code.getBounds()
      width = bounds[2] - bounds[0]
      height = bounds[3] - bounds[1]
      d = Drawing(size, size, transform=[float(size)/width,0,0,float(size)/height,0,0])
      d.add(qr_code)
      renderPDF.draw(d, c, 0, 0)

      c.save()
      
    return filename
