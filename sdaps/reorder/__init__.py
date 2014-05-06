# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2012, Benjamin Berg <benjamin@sipsolutions.net>
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

u"""
This module reorders already recognized data according to the questoinnaire IDs.
"""

from collections import defaultdict
from sdaps import model

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def reorder(survey):
    """We can assume quite some things in this function, because recognize
    properly handles it. ie.

     * Every image will be tagged correctly (as long as the data is known)
     * in duplex mode both the front/back image will be tagged, so we don't
       need to care about that here!
    """

    # First, go over all sheets and figure out which ones need reordering.
    # For every sheet that isn't quite right, we extract the images, and delete
    # the sheet.
    # The images are put into a dictionnary using the questionnaire ID.
    # Each entry in the dictionary is a list.
    images = defaultdict(lambda : [])
    for sheet in survey.sheets[:]: # Use a flat copy to iterate over

        # Drop from the list of sheets and always reoder
        survey.sheets.remove(sheet)

        for image in sheet.images:
            images[(image.questionnaire_id, image.global_id)].append(image)

    # We have dictionnary of lists of images that needs to be put into sheets
    # again.
    # This could probably be more robust. We don't care about the questionnaire
    # ID itself here, just put each list into sheets, splitting it into many
    # if there are too many images.
    c = survey.questionnaire.page_count
    pages = {} 

    for img_list in images.itervalues():
        while len(img_list) > 0:
            img = img_list.pop(0)
            found = 0
            for sheet in survey.sheets[:]:
                if (img.questionnaire_id == sheet.questionnaire_id) and (img.questionnaire_id != None):
                    found = 1
                    try:
			# try if we already have that page, if yes insert a DUMMY image and go on 
                        pages[img.questionnaire_id,img.page_number]

                        img = model.sheet.Image()
                        sheet.add_image(img)
                        img.filename = "DUMMY"
                        img.tiff_page = -1
                        img.ignored = True
                    except KeyError:
			# image not in pages, add it
                        sheet.add_image(img)
                        pages[img.questionnaire_id,img.page_number] = True

            if (found == 0) and (img.questionnaire_id != None):
                newsheet = model.sheet.Sheet()
                survey.add_sheet(newsheet)
                newsheet.questionnaire_id = img.questionnaire_id
                newsheet.add_image(img)
                pages[img.questionnaire_id,img.page_number] = True


    survey.save()

