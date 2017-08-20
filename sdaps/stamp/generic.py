
import sys

try:
    import cStringIO as StringIO
except:
    import StringIO

import os
import subprocess
import tempfile
import shutil

import reportlab.pdfgen.canvas
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import createBarcodeDrawing, qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import units

from sdaps import log
from sdaps import defs

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

mm = units.mm


def draw_survey_id(canvas, survey):
    if 0:
        assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)

    pos = survey.defs.get_survey_id_pos()

    canvas.saveState()
    canvas.setFont(defs.codebox_text_font, defs.codebox_text_font_size)
    canvas.drawCentredString(pos[3] * mm, pos[4] * mm, _(u'Survey-ID: %i') % survey.survey_id)
    draw_codebox(canvas, pos[0] * mm, pos[2] * mm, survey.survey_id >> 16)
    draw_codebox(canvas, pos[1] * mm, pos[2] * mm, survey.survey_id & ((1 << 16) - 1))
    canvas.restoreState()


def draw_questionnaire_id(canvas, survey, questionnaire_id):
    if 0:
        assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)

    pos = survey.defs.get_questionnaire_id_pos()

    canvas.saveState()
    canvas.setFont(defs.codebox_text_font, defs.codebox_text_font_size)
    canvas.drawCentredString(pos[3] * mm, pos[4] * mm, _(u'Questionnaire-ID: %i') % questionnaire_id)
    draw_codebox(canvas, pos[0] * mm, pos[2] * mm, questionnaire_id)
    draw_codebox(canvas, pos[1] * mm, pos[2] * mm, questionnaire_id)
    canvas.restoreState()


def draw_codebox(canvas, x, y, code):
    if 0:
        assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
    size = defs.codebox_step * mm
    length = defs.codebox_length # 2 Bytes
    canvas.saveState()
    canvas.translate(x, y)
    canvas.rect(0, 0, defs.codebox_width * mm, defs.codebox_height * mm)
    for i in range(length):
        if code & (1 << i):
            canvas.rect((length - i - 1) * size, 0,
                         size, defs.codebox_height * mm,
                         stroke=1, fill=1)
    canvas.restoreState()


def draw_corner_marks(survey, canvas):
    if 0:
        assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)

    length = defs.corner_mark_length
    x, y = (defs.corner_mark_left, defs.corner_mark_top)
    canvas.line(x * mm, y * mm, (x + length) * mm, y * mm)
    canvas.line(x * mm, y * mm, x * mm, (y + length) * mm)

    x, y = (survey.defs.paper_width - defs.corner_mark_right, defs.corner_mark_top)
    canvas.line(x * mm, y * mm, (x - length) * mm, y * mm)
    canvas.line(x * mm, y * mm, x * mm, (y + length) * mm)

    x, y = (defs.corner_mark_left, survey.defs.paper_height - defs.corner_mark_bottom)
    canvas.line(x * mm, y * mm, (x + length) * mm, y * mm)
    canvas.line(x * mm, y * mm, x * mm, (y - length) * mm)

    x, y = (survey.defs.paper_width - defs.corner_mark_right, survey.defs.paper_height - defs.corner_mark_bottom)
    canvas.line(x * mm, y * mm, (x - length) * mm, y * mm)
    canvas.line(x * mm, y * mm, x * mm, (y - length) * mm)


# top left, top right, bottom left, bottom right
corners = [
    [0, 1, 1, 1],
    [1, 1, 0, 0],
    [1, 0, 1, 1],
    [1, 0, 1, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 1],
]


def draw_corner_boxes(survey, canvas, page):
    if 0:
        assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)

    width = defs.corner_box_width
    height = defs.corner_box_height
    padding = defs.corner_box_padding

    corner_boxes_positions = [
        (defs.corner_mark_left + padding,
         defs.corner_mark_top + padding),
        (survey.defs.paper_width - defs.corner_mark_right - padding - width,
         defs.corner_mark_top + padding),
        (defs.corner_mark_left + padding,
         survey.defs.paper_height - defs.corner_mark_bottom - padding - height),
        (survey.defs.paper_width - defs.corner_mark_right - padding - width,
         survey.defs.paper_height - defs.corner_mark_bottom - padding - height)
    ]

    for i in xrange(4):
        x, y = corner_boxes_positions[i]
        canvas.rect(x * mm, y * mm, width * mm, height * mm, fill=corners[page][i])


# CODE 128 support

def draw_code128_questionnaire_id(canvas, survey, id):
    # Only supports ascii for now (see also defs.py)
    barcode_value = unicode(id).encode('ascii')
    barcode = createBarcodeDrawing("Code128",
                                   value=barcode_value,
                                   barWidth=defs.code128_barwidth / 25.4 * 72.0,
                                   height=defs.code128_height / 25.4 * 72.0,
                                   quiet=False)

    y = survey.defs.paper_height - defs.corner_mark_bottom
    x = defs.corner_mark_left

    barcode_y = y - defs.code128_vpad - defs.code128_height
    barcode_x = x + defs.code128_hpad

    # The barcode should be flush left.
    barcode_x = barcode_x

    renderPDF.draw(barcode, canvas, barcode_x * mm, barcode_y * mm)

    # Label
    text_x = barcode_x + barcode.width / mm / 2.0
    text_y = barcode_y + defs.code128_height + 1 + \
             defs.code128_text_font_size / 72.0 * 25.4 / 2.0

    canvas.saveState()
    canvas.setFont(defs.code128_text_font, defs.code128_text_font_size)
    canvas.drawCentredString(text_x * mm, text_y * mm, barcode_value)
    canvas.restoreState()


def draw_code128_global_id(canvas, survey):
    if survey.global_id is None:
        raise AssertionError

    # Only allow ascii
    barcode_value = survey.global_id.encode('ascii')

    barcode = createBarcodeDrawing("Code128",
                                   value=barcode_value,
                                   barWidth=defs.code128_barwidth / 25.4 * 72.0,
                                   height=defs.code128_height / 25.4 * 72.0,
                                   quiet=False)

    y = survey.defs.paper_height - defs.corner_mark_bottom
    x = (survey.defs.paper_width - defs.corner_mark_right + defs.corner_mark_left) / 2

    barcode_y = y - defs.code128_vpad - defs.code128_height
    barcode_x = x

    # Center
    barcode_x = barcode_x - barcode.width / mm / 2.0

    renderPDF.draw(barcode, canvas, barcode_x * mm, barcode_y * mm)

    # Label
    text_x = barcode_x + barcode.width / mm / 2.0
    text_y = barcode_y + defs.code128_height + 1 + defs.code128_text_font_size / 72.0 * 25.4 / 2.0

    canvas.saveState()
    canvas.setFont(defs.code128_text_font, defs.code128_text_font_size)
    canvas.drawCentredString(text_x * mm, text_y * mm, barcode_value)
    canvas.restoreState()


def draw_code128_sdaps_info(canvas, survey, page):
    # The page number is one based here already
    # The survey_id is a 32bit number, which means we need
    # 10 decimal digits to encode it, then we need to encode the
    # the page with at least 3 digits(just in case someone is insane enough
    # to have a questionnaire with more than 99 pages.
    # So use 10+4 digits

    barcode_value = "%010d%04d" % (survey.survey_id, page)
    barcode = createBarcodeDrawing("Code128",
                                   value=barcode_value,
                                   barWidth=defs.code128_barwidth / 25.4 * 72.0,
                                   height=defs.code128_height / 25.4 * 72.0,
                                   quiet=False)

    y = survey.defs.paper_height - defs.corner_mark_bottom
    x = survey.defs.paper_width - defs.corner_mark_right

    barcode_y = y - defs.code128_vpad - defs.code128_height
    barcode_x = x - defs.code128_hpad

    # The barcode should be flush left.
    barcode_x = barcode_x - barcode.width / mm

    renderPDF.draw(barcode, canvas, barcode_x * mm, barcode_y * mm)

    # Label
    text_x = barcode_x + barcode.width / mm / 2.0
    text_y = barcode_y + defs.code128_height + 1 + defs.code128_text_font_size / 72.0 * 25.4 / 2.0

    canvas.saveState()
    canvas.setFont(defs.code128_text_font, defs.code128_text_font_size)
    canvas.drawCentredString(text_x * mm, text_y * mm, barcode_value)
    canvas.restoreState()


# QR-Code support

def draw_qr_questionnaire_id(canvas, survey, id):
    # Only supports ascii for now (see also defs.py)
    value = unicode(id).encode('ascii')

    y = survey.defs.paper_height - defs.corner_mark_bottom
    x = defs.corner_mark_left

    qr_code = qr.QrCodeWidget(value, barLevel='H')
    bounds = qr_code.getBounds()

    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    # Squeeze into the space between corner mark and content
    size = defs.bottom_page_margin - defs.corner_mark_bottom

    code_y = y
    code_x = x

    d = Drawing(size*mm, size*mm, transform=[float(size*mm)/width,0,0,-float(size*mm)/height,0,0])
    d.add(qr_code)

    renderPDF.draw(d, canvas, code_x*mm, code_y*mm)

def draw_qr_global_id(canvas, survey):
    if survey.global_id is None:
        raise AssertionError

    # Only allow ascii
    value = survey.global_id.encode('ascii')

    y = survey.defs.paper_height - defs.corner_mark_bottom
    x = (survey.defs.paper_width - defs.corner_mark_right + defs.corner_mark_left) / 2

    qr_code = qr.QrCodeWidget(value, barLevel='H')
    bounds = qr_code.getBounds()

    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    # Squeeze into the space between corner mark and content
    size = defs.bottom_page_margin - defs.corner_mark_bottom

    code_y = y
    code_x = x - size / 2.0

    d = Drawing(size*mm, size*mm, transform=[float(size*mm)/width,0,0,-float(size*mm)/height,0,0])
    d.add(qr_code)

    renderPDF.draw(d, canvas, code_x*mm, code_y*mm)

def draw_qr_sdaps_info(canvas, survey, page):
    # The page number is one based here already
    # The survey_id is a 32bit number, which means we need
    # 10 decimal digits to encode it, then we need to encode the
    # the page with at least 3 digits(just in case someone is insane enough
    # to have a questionnaire with more than 99 pages.
    # So use 10+4 digits

    value = "%010d%04d" % (survey.survey_id, page)

    y = survey.defs.paper_height - defs.corner_mark_bottom
    x = survey.defs.paper_width - defs.corner_mark_right

    qr_code = qr.QrCodeWidget(value, barLevel='H')
    bounds = qr_code.getBounds()

    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    # Squeeze into the space between corner mark and content
    size = defs.bottom_page_margin - defs.corner_mark_bottom

    code_y = y
    code_x = x - size

    d = Drawing(size*mm, size*mm, transform=[float(size*mm)/width,0,0,-float(size*mm)/height,0,0])
    d.add(qr_code)

    renderPDF.draw(d, canvas, code_x*mm, code_y*mm)


def create_stamp_pdf(survey, output_filename, questionnaire_ids):
    sheets = 1 if questionnaire_ids is None else len(questionnaire_ids)

    questionnaire_length = survey.questionnaire.page_count

    have_pdftk = False
    # Test if pdftk is present, if it is we can use it to be faster
    try:
        result = subprocess.Popen(['pdftk', '--version'], stdout=subprocess.PIPE)
        # Just assume pdftk is there, if it was executed sucessfully
        if result is not None:
            have_pdftk = True
    except OSError:
        pass

    if not have_pdftk:
        try:
            import pyPdf
        except:
            log.error(_(u'You need to have either pdftk or pyPdf installed. pdftk is the faster method.'))
            sys.exit(1)

    # Write the "stamp" out to tmp.pdf if are using pdftk.
    if have_pdftk:
        stampsfile = file(survey.path('tmp.pdf'), 'wb')
    else:
        stampsfile = StringIO.StringIO()

    canvas = \
        reportlab.pdfgen.canvas.Canvas(stampsfile,
                                       bottomup=False,
                                       pagesize=(survey.defs.paper_width * mm,
                                                 survey.defs.paper_height * mm))
    # bottomup = False =>(0, 0) is the upper left corner

    print ungettext(u'Creating stamp PDF for %i sheet', u'Creating stamp PDF for %i sheets', sheets) % sheets
    log.progressbar.start(sheets)
    for i in range(sheets):
        if questionnaire_ids is not None:
            id = questionnaire_ids.pop(0)

        for j in range(questionnaire_length):
            if survey.defs.style == "classic":
                draw_corner_marks(survey, canvas)
                draw_corner_boxes(survey, canvas, j)
                if not survey.defs.duplex or j % 2:
                    if questionnaire_ids is not None:
                        draw_questionnaire_id(canvas, survey, id)

                    if survey.defs.print_survey_id:
                        draw_survey_id(canvas, survey)

            elif survey.defs.style == "code128":
                draw_corner_marks(survey, canvas)

                if not survey.defs.duplex or j % 2:
                    if questionnaire_ids is not None:
                        draw_code128_questionnaire_id(canvas, survey, id)

                    # Survey ID has to be printed in CODE128 mode, because it
                    # contains the page number and rotation.
                    draw_code128_sdaps_info(canvas, survey, j + 1)

                    if survey.global_id is not None:
                        draw_code128_global_id(canvas, survey)

            elif survey.defs.style == "qr":
                draw_corner_marks(survey, canvas)

                if not survey.defs.duplex or j % 2:
                    if questionnaire_ids is not None:
                        draw_qr_questionnaire_id(canvas, survey, id)

                    # Survey ID has to be printed in QR mode, because it
                    # contains the page number and rotation.
                    draw_qr_sdaps_info(canvas, survey, j + 1)

                    if survey.global_id is not None:
                        draw_qr_global_id(canvas, survey)

            elif survey.defs.style == "custom":
                # Only draw corner marker
                draw_corner_marks(survey, canvas)

                pass
            else:
                raise AssertionError()

            canvas.showPage()
        log.progressbar.update(i + 1)

    canvas.save()

    print ungettext(u'%i sheet; %f seconds per sheet', u'%i sheet; %f seconds per sheet', log.progressbar.max_value) % (
        log.progressbar.max_value,
        float(log.progressbar.elapsed_time) /
        float(log.progressbar.max_value)
    )

    if have_pdftk:
        stampsfile.close()
        # Merge using pdftk
        print _("Stamping using pdftk")
        tmp_dir = tempfile.mkdtemp(prefix='sdaps-stamp-')

        if sheets == 1:
            # Shortcut if we only have one sheet.
            # In this case form data in the PDF will *not* break, in
            # the other code path it *will* break.
            print _(u"pdftk: Overlaying the original PDF with the markings.")
            subprocess.call(['pdftk',
                             survey.path('questionnaire.pdf'),
                             'multistamp',
                             survey.path('tmp.pdf'),
                             'output',
                             output_filename])
        else:
            for page in xrange(1, questionnaire_length + 1):
                print ungettext(u"pdftk: Splitting out page %d of each sheet.", u"pdftk: Splitting out page %d of each sheet.", page) % page
                args = []
                args.append('pdftk')
                args.append(survey.path('tmp.pdf'))
                args.append('cat')
                cur = page
                for i in range(sheets):
                    args.append('%d' % cur)
                    cur += questionnaire_length
                args.append('output')
                args.append(os.path.join(tmp_dir, 'stamp-%d.pdf' % page))

                subprocess.call(args)

            print _(u"pdftk: Splitting the questionnaire for watermarking.")
            subprocess.call(['pdftk', survey.path('questionnaire.pdf'),
                             'dump_data', 'output',
                             os.path.join(tmp_dir, 'doc_data.txt')])
            for page in xrange(1, questionnaire_length + 1):
                subprocess.call(['pdftk', survey.path('questionnaire.pdf'), 'cat',
                                 '%d' % page, 'output',
                                 os.path.join(tmp_dir, 'watermark-%d.pdf' % page)])

            if sheets == 1:
                for page in xrange(1, questionnaire_length + 1):
                    print ungettext(u"pdftk: Watermarking page %d of all sheets.", u"pdftk: Watermarking page %d of all sheets.", page) % page
                    subprocess.call(['pdftk',
                                     os.path.join(tmp_dir, 'stamp-%d.pdf' % page),
                                     'background',
                                     os.path.join(tmp_dir, 'watermark-%d.pdf' % page),
                                     'output',
                                     os.path.join(tmp_dir, 'watermarked-%d.pdf' % page)])
            else:
                for page in xrange(1, questionnaire_length + 1):
                    print ungettext(u"pdftk: Watermarking page %d of all sheets.", u"pdftk: Watermarking page %d of all sheets.", page) % page
                    subprocess.call(['pdftk',
                                     os.path.join(tmp_dir, 'stamp-%d.pdf' % page),
                                     'background',
                                     os.path.join(tmp_dir, 'watermark-%d.pdf' % page),
                                     'output',
                                     os.path.join(tmp_dir, 'watermarked-%d.pdf' % page)])

            args = []
            args.append('pdftk')
            for page in xrange(1, questionnaire_length + 1):
                char = chr(ord('A') + page - 1)
                args.append('%s=' % char + os.path.join(tmp_dir, 'watermarked-%d.pdf' % page))

            args.append('cat')

            for i in range(sheets):
                for page in xrange(1, questionnaire_length + 1):
                    char = chr(ord('A') + page - 1)
                    args.append('%s%d' % (char, i + 1))

            args.append('output')
            args.append(os.path.join(tmp_dir, 'final.pdf'))
            print _(u"pdftk: Assembling everything into the final PDF.")
            subprocess.call(args)

            subprocess.call(['pdftk', os.path.join(tmp_dir, 'final.pdf'),
                             'update_info', os.path.join(tmp_dir, 'doc_data.txt'),
                             'output', output_filename])

        # Remove tmp.pdf
        os.unlink(survey.path('tmp.pdf'))
        # Remove all the temporary files
        shutil.rmtree(tmp_dir)

    else:
        # Merge using pyPdf
        stamped = pyPdf.PdfFileWriter()
        stamped._info.getObject().update({
            pyPdf.generic.NameObject('/Producer'): pyPdf.generic.createStringObject(u'sdaps'),
            pyPdf.generic.NameObject('/Title'): pyPdf.generic.createStringObject(survey.title),
        })

        subject = []
        for key, value in survey.info.iteritems():
            subject.append(u'%(key)s: %(value)s' % {'key': key, 'value': value})
        subject = u'\n'.join(subject)

        stamped._info.getObject().update({
            pyPdf.generic.NameObject('/Subject'): pyPdf.generic.createStringObject(subject),
        })

        stamps = pyPdf.PdfFileReader(stampsfile)

        del stampsfile

        questionnaire = pyPdf.PdfFileReader(
            file(survey.path('questionnaire.pdf'), 'rb')
        )

        print _(u'Stamping using pyPdf. For faster stamping, install pdftk.')
        log.progressbar.start(sheets)

        for i in range(sheets):
            for j in range(questionnaire_length):
                s = stamps.getPage(i * questionnaire_length + j)
                if not have_pdftk:
                    q = questionnaire.getPage(j)
                    s.mergePage(q)
                stamped.addPage(s)
            log.progressbar.update(i + 1)

        stamped.write(open(output_filename, 'wb'))

        print ungettext(u'%i sheet; %f seconds per sheet', u'%i sheet; %f seconds per sheet',
                        log.progressbar.max_value) % (
                            log.progressbar.max_value,
                            float(log.progressbar.elapsed_time) /
                            float(log.progressbar.max_value))

