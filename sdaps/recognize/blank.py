# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008,2013, Benjamin Berg <benjamin@sipsolutions.net>
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

# Example of using this to preload your own custom buddy. This first sets up the
# paths, below the call into sdaps happens
if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sdaps import defs

from sdaps import model
from sdaps.utils.exceptions import RecognitionError

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


class Image(model.buddy.Buddy, metaclass=model.buddy.Register):
    """Example buddy class for a "blank" style. It simply assumes
    that everything is good about the page. ie. first page, no rotation,
    correct survey ID, and no other IDs."""
    name = 'style'
    obj_class = model.sheet.Image

    def get_page_rotation(self):
        """Return the rotation of the passed image."""
        # Assume not rotated
        return False

    def get_page_number(self):
        """Return page number or None if not known."""
        # Assume only one page
        return 1

    def get_survey_id(self):
        """Return the survey ID as read from the image, or None."""
        # Return the expected survey ID
        return self.obj.sheet.survey.survey_id

    def get_questionnaire_id(self):
        """Return the questionnaire ID as read from the image."""
        # Assume no (useful) questionnaire ID exists
        return None

    def get_global_id(self):
        """Return the global ID as read from the image."""
        # Assume no (useful) global ID exists
        return None

# Example of using this to preload your own custom buddy. This assume a local run.
# You can of course use the API directly too.
if __name__ == '__main__':
    import sdaps
    sys.exit(sdaps.main(local_run = True))

