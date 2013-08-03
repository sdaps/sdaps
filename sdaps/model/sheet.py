# -*- coding: utf8 -*-
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

import buddy


class Sheet(buddy.Object):

    _pickled_attrs = {'survey', 'data', 'images', 'survey_id',
                      'questionnaire_id', 'global_id', 'valid',
                      'quality', 'recognized', 'verified'}

    def __init__(self):
        self.survey = None
        self.data = dict()
        self.images = list()
        self.survey_id = None
        self.questionnaire_id = None
        self.global_id = None
        self.valid = 1
        self.quality = 1

        self.recognized = False
        self.verified = False

    def add_image(self, image):
        self.images.append(image)
        image.sheet = self

    def get_page_image(self, page):
        # Simply return the image for the requested page.
        # Note: We return the first one we find; this means in the error case
        #       that a page exists twice, we return the first one.
        for image in self.images:
            if image.page_number == page and image.survey_id == self.survey.survey_id:
                return image
        return None

    def reinit_state(self):
        for k, v in self.data.iteritems():
            obj = self.survey.questionnaire.find_object(k)

            v._parent = obj

    @property
    def empty(self):
        for k, v in self.data.iteritems():
            if not v.empty:
                return False

        return True

    @property
    def complete(self):
        """A boolean whether this sheet is complete in the sense that
        every page of the questionnaire has been identified.
        ie. it is false if there are missing pages"""

        # Simply retrieve every page, and see if it is not None
        for page in xrange(self.survey.questionnaire.page_count):
            if self.get_page_image(page + 1) is None:
                return False
        return True

    def __setattr__(self, attr, value):
        # Nonexisting attributes should never be set.
        if attr.startswith('_'):
            object.__setattr__(self, attr, value)
            return

        assert attr in self._pickled_attrs

        # We need to fall back to "None" for __init__ to work.
        try:
            old_value = getattr(self, attr)
            force = False
        except AttributeError:
            old_value = None
            force = True

        if force or value != old_value:
            object.__setattr__(self, attr, value)
            # survey may be None if the sheet does not belong to a survey yet.
            if self.survey is not None:
                self.survey.questionnaire.notify_data_changed(None, None, attr, old_value)


class Image(buddy.Object):

    def __init__(self):
        self.sheet = None
        self.filename = str()
        self.tiff_page = 0
        self.rotated = 0
        self.raw_matrix = None
        self.page_number = None
        self.survey_id = None
        self.global_id = None
        self.questionnaire_id = None
        #: Whether the page should be ignored (because it is a blank back side)
        self.ignored = False


