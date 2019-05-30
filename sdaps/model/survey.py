# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008,2018, Benjamin Berg <benjamin@sipsolutions.net>
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

import os
import sys
import struct

import json
import sqlite3
import weakref
from contextlib import closing
 
from . import db
from . import questionnaire
from .sheet import Sheet
from sdaps import defs
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

valid_styles = ['classic', 'code128', 'custom', 'qr']
valid_checkmodes = ['checkcorrect', 'check', 'fill']

_db_schema = """
CREATE TABLE surveys (
    json TEXT
);
CREATE TRIGGER survey_delete AFTER DELETE ON surveys FOR EACH ROW
  BEGIN
    DELETE FROM sheets WHERE survey_rowid = OLD.rowid;
  END;


CREATE TABLE sheets (
    survey_rowid REFERENCES surveys(rowid) NOT NULL,
    sort INTEGER(8),

    json TEXT
);
"""



class Defs(object):
    """General definitions that are valid for this survey.

    :ivar paper_width: Width of the paper in mm.
    :ivar paper_height: Height of the paper in mm.
    :ivar print_questionnaire_id: Whether a questionnaire ID is printed on each sheet.
    :ivar print_survey_id: Whether a survey ID is printed on each sheet.
    :ivar style: The style that is used for ID marking.
    :ivar duplex: Whether the questionnaire is duplex or not.
    """

    # Force a certain set of options using slots
    __slots__ = ['paper_width', 'paper_height', 'print_questionnaire_id',
                 'print_survey_id', 'style', 'duplex', 'checkmode',
                 'engine']

    def get_survey_id_pos(self):
        assert(self.style == 'classic')

        y_pos = self.paper_height - defs.corner_mark_bottom - defs.corner_box_padding
        y_pos -= defs.codebox_height

        left_padding = defs.corner_mark_left + 2 * defs.corner_box_padding + defs.corner_box_width
        right_padding = defs.corner_mark_right + 2 * defs.corner_box_padding + defs.corner_box_width

        text_y_pos = y_pos + defs.codebox_text_baseline_shift
        x_center = left_padding + (self.paper_width - left_padding - right_padding) / 2.0

        msb_box_x = left_padding
        lsb_box_x = self.paper_width - right_padding - defs.codebox_width

        text_x_pos = left_padding + (self.paper_width - right_padding - left_padding) / 2

        return msb_box_x, lsb_box_x, y_pos, text_x_pos, text_y_pos

    def get_questionnaire_id_pos(self):
        assert(self.style == 'classic')

        msb_box_x, lsb_box_x, y_pos, text_x_pos, text_y_pos = self.get_survey_id_pos()

        if self.print_survey_id:
            # Just move the y positions up if neccessary
            y_pos -= defs.codebox_height + defs.corner_box_padding
            text_y_pos -= defs.codebox_height + defs.corner_box_padding

        return msb_box_x, lsb_box_x, y_pos, text_x_pos, text_y_pos


class Survey(object):

    """The main survey object.

    :ivar defs: The :py:class:`model.survey.Defs` instance for this survey.
    :ivar survey_id: The survey ID of this survey.
    :ivar global_id: The global ID set for this survey. It is used during the "stamp" step.
    :ivar questionnaire: The py:class:`model.questionnaire.Questionnaire` instance representing the questionnaire.
    :ivar title: The title of the survey.
    :ivar info: Dictionary with general information about the survey.
    :ivar questionnaire_ids: A List of used questionnaire IDs.
    """

    _pickled_attrs = set(('defs', 'survey_id', 'questionnaire_ids', 'questionnaire', 'version'))

    def __init__(self):
        self.questionnaire = None

        self._internal_init()

        self.title = str()
        self.info = dict()
        self.survey_id = 0
        self.global_id = None
        self.questionnaire_ids = list()
        self.index = 0
        self.defs = Defs()
        self._db = None
        # Hardcoded for now.
        self._survey_rowid = 0

    def _internal_init(self):
        self._loaded_sheets = weakref.WeakValueDictionary()
        self._dirty_sheets = []
        self._current_sheet = None

    def add_questionnaire(self, questionnaire):
        self.questionnaire = questionnaire
        questionnaire.survey = self

    def add_sheet(self, sheet):
        """"
        WARNING: It is impossible to iterate newly added sheets before the
        survey has been saved!
        """
        sheet.survey = self
        sheet._rowid = -1

        self.goto_sheet(sheet)

    def delete_sheet(self, sheet):
        """"
        WARNING: The sheet will remain iteratable until the survey has been
        saved!
        """
        # This is a bit of a hack, but it will work great
        sheet._delete = True
        sheet._dirty = True

        self.goto_sheet(None)

    def calculate_survey_id(self):
        """Calculate the unique survey ID from the surveys settings and boxes.

        The ID only includes the boxes positions, which means that simple typo
        fixes will not change the ID most of the time."""
        import hashlib
        md5 = hashlib.new('md5')

        for qobject in self.questionnaire.qobjects:
            qobject.calculate_survey_id(md5)

        for defs_slot in self.defs.__slots__:
            # Backward compatibility
            if defs_slot == 'checkmode' and self.defs.checkmode == "checkcorrect":
                continue

            if defs_slot == 'engine':
                continue

            if isinstance(self.defs.__getattribute__(defs_slot), float):
                md5.update(str(round(self.defs.__getattribute__(defs_slot), 1)).encode('utf-8'))
            else:
                md5.update(str(self.defs.__getattribute__(defs_slot)).encode('utf-8'))

        # Use the first 32 bits as a little endian unsigned integer
        self.survey_id = struct.unpack('<I', md5.digest()[0:4])[0]

    @staticmethod
    def load(survey_dir):
        import configparser

        # Assume rowid is 0
        survey_rowid = 0

        dbfile = os.path.join(survey_dir, 'survey.sqlite')
        if not os.path.exists(dbfile):
            raise AssertionError('DB file does not exist!')
        _db = sqlite3.connect(dbfile)

        with _db as con:
            c = con.cursor()
            c.execute('SELECT json FROM surveys WHERE rowid=?', (survey_rowid,))
            _json, = c.fetchone()

            survey = db.fromJson(json.loads(_json), sys.modules[__name__])
            survey.survey_dir = survey_dir
            survey._survey_rowid = 0
            survey._db = _db

        ##########
        # Load the info file
        config = configparser.SafeConfigParser()
        config.optionxform = str
        config.read(os.path.join(survey_dir, 'info'))
        survey.title = config.get('sdaps', 'title')

        survey.global_id = config.get('sdaps', 'global_id')
        if survey.global_id == '' or survey.global_id == 'None':
            survey.global_id = None

        survey.info = dict()
        for key, value in config.items('info'):
            survey.info[key] = value

        return survey

    def _db_get_sheet(self, rowid):
        try:
            return self._loaded_sheets[rowid]
        except KeyError:
            pass

        c = self._db.cursor()
        c.execute('SELECT json FROM sheets WHERE survey_rowid=? AND rowid=?', (self._survey_rowid, rowid))

        data = json.loads(c.fetchone()[0])
        sheet = db.fromJson(data, Sheet)
        sheet._rowid = rowid
        sheet.survey = self
        sheet.reinit_state()

        self._loaded_sheets[rowid] = sheet
        return sheet

    def _db_save_sheet(self, cursor, sheet):
        if not sheet.dirty and sheet._rowid != -1:
            return

        if hasattr(sheet, '_delete') and sheet._delete:
            cursor.execute('DELETE FROM sheets WHERE survey_rowid=? and rowid=?', (self._survey_rowid, sheet._rowid))
            return

        tmp = json.dumps(sheet, default=db.toJson)
        if sheet._rowid == -1:
            cursor.execute('INSERT INTO sheets (survey_rowid, json) VALUES (?, ?)', (self._survey_rowid, tmp))
            sheet._rowid = cursor.lastrowid
            self._loaded_sheets[sheet._rowid] = sheet
        else:
            cursor.execute('UPDATE sheets SET json=? WHERE survey_rowid=? and rowid=?', (tmp, self._survey_rowid, sheet._rowid))

        sheet._clear_dirty()

    def __setstate__(self, state):
        self._internal_init()
        self.__dict__.update(state)
        self.questionnaire = db.fromJson(self.questionnaire, questionnaire.Questionnaire)
        self.questionnaire.survey = self
        self.defs = db.fromJson(self.defs, Defs)

        # Migrate old Defs object (from 1.9.5 or newer)
        if not hasattr(self.defs, 'engine'):
            self.defs.engine = defs.latex_engine

    @staticmethod
    def new(survey_dir):
        survey = Survey()
        survey.survey_dir = survey_dir
        try:
            os.makedirs(survey.path())
        except FileExistsError:
            pass

        dbfile = survey.path('survey.sqlite')
        if os.path.exists(dbfile):
            raise AssertionError('DB file already exists!')
        survey._db = sqlite3.connect(dbfile)
        survey._db.executescript(_db_schema)

        return survey

    def save(self):
        import configparser

        # Update the DB syncing out all changes
        with self._db as con:
            c = con.cursor()
            c.execute('INSERT OR REPLACE INTO surveys (rowid, json) VALUES (?, ?)', (self._survey_rowid, json.dumps(self, default=db.toJson)))

            for sheet in self._dirty_sheets:
                 self._db_save_sheet(c, sheet)
            if self._current_sheet:
                self._db_save_sheet(c, self._current_sheet)

            self._dirty_sheets = []

        # Sanity check that there is no sheet object alive that is dirty
        for sheet in self._loaded_sheets.values():
            assert sheet is None or (not sheet.dirty and sheet._rowid != -1)

        ###############
        # Write out the info file next

        # Hack to include comments. Set allow_no_value here, and add keys
        # with a '#' in the front and no value.
        config = configparser.SafeConfigParser(allow_no_value=True)

        config.optionxform = str
        config.add_section('sdaps')
        config.add_section('info')
        config.add_section('defs')
        config.add_section('questionnaire')
        config.set('sdaps', 'title', self.title)
        if self.global_id is not None:
            config.set('sdaps', 'global_id', self.global_id)
        else:
            config.set('sdaps', 'global_id', '')

        for key, value in sorted(self.info.items()):
            config.set('info', key, value)

        config.set('defs', '# These values are not read back, they exist for information only!')
        for attr in self.defs.__slots__:
            config.set('defs', attr, str(getattr(self.defs, attr)))

        config.set('questionnaire', '# These values are not read back, they exist for information only!')
        config.set('questionnaire', 'page_count', str(self.questionnaire.page_count))
        # Put the survey ID into "questionnaire". This seems sane even though
        # it is not stored there internally..
        config.set('questionnaire', 'survey_id', str(self.survey_id))

        # Atomically write info file
        info_fd = open(os.path.join(self.survey_dir, '.info.tmp'), 'w')
        config.write(info_fd)

        os.fsync(info_fd)
        info_fd.close()

        try:
            os.rename(os.path.join(self.survey_dir, 'info'), os.path.join(self.survey_dir, 'info~'))
        except OSError:
            pass

        os.rename(os.path.join(self.survey_dir, '.info.tmp'), os.path.join(self.survey_dir, 'info'))


    def path(self, *path):
        return os.path.join(self.survey_dir, *path)

    def new_path(self, path):
        content = os.listdir(self.path())
        i = 1
        while path % i in content:
            i += 1
        return os.path.join(self.survey_dir, path % i)

    def get_sheet(self):
        return self._current_sheet

    #: The currently selected sheet. Usually it will be changed by :py:meth:`iterate` or similar.
    sheet = property(get_sheet)

    def iterate(self, function, filter=lambda: True, *args, **kwargs):
        '''call function once for each sheet
        '''
        with self._db as con:
            c = con.cursor()
            c.execute('SELECT rowid FROM sheets WHERE survey_rowid=? ORDER BY sort,rowid', (self._survey_rowid,))
            for sheetid, in c.fetchall():
                self.goto_sheet(self._db_get_sheet(sheetid))
                if filter():
                    function(*args, **kwargs)

    @property
    def sheet_count(self):
        with self._db as con:
            c = con.cursor()
            c.execute('SELECT count(*) FROM sheets WHERE survey_rowid=?', (self._survey_rowid,))
            count = c.fetchone()[0]
            return count

    def iterate_progressbar(self, function, filter=lambda: True, *args, **kwargs):
        '''call function once for each sheet and display a progressbar
        '''
        with self._db as con:
            c = con.cursor()
            c.execute('SELECT count(*) FROM sheets WHERE survey_rowid=?', (self._survey_rowid,))
            count = c.fetchone()[0]

            # The old code used to first filter, and then run; but that is
            # a bit ineffective in a way
            print(ungettext('%i sheet', '%i sheets', count) % count)
            if count == 0:
                return

            log.progressbar.start(count)

            processed = 0
            c.execute('SELECT rowid FROM sheets WHERE survey_rowid=? ORDER BY sort,rowid', (self._survey_rowid,))
            for index, (sheetid,) in enumerate(c.fetchall()):
                self.goto_sheet(self._db_get_sheet(sheetid))
                if filter():
                    function(*args, **kwargs)
                    processed += 1

                log.progressbar.update(index + 1)

        print(_('Processed %i of %i sheets, took %f seconds') % (processed, count, log.progressbar.elapsed_time))

    def goto_sheet(self, sheet):
        '''goto the specified sheet object
        '''
        if self._current_sheet is not None and (self._current_sheet._rowid == -1 or self._current_sheet.dirty):
            if self._current_sheet not in self._dirty_sheets:
                self._dirty_sheets.append(self._current_sheet)

        self._current_sheet = sheet

    def goto_nth_sheet(self, index):
        with self._db as con:
            c = con.cursor()
            c.execute('SELECT rowid FROM sheets WHERE survey_rowid=? ORDER BY sort,rowid LIMIT 1 OFFSET ?', (self._survey_rowid, index))
            rowid = c.fetchone()[0]

        self.goto_sheet(self._db_get_sheet(rowid))

    def goto_questionnaire_id(self, questionnaire_id):
        '''goto the sheet object specified by its questionnaire_id
        '''

        qids = set()
        qids.add(questionnaire_id)
        # May also be an integer, so also add that if it can be decoded!
        try:
            qids.add(int(questionnaire_id))
        except ValueError:
            pass

        sheets = []
        def found():
            if self.sheet.questionnaire_id in qids:
                sheets.append(self.sheet)

        self.iterate(found)

        if len(sheets) == 1:
            self.goto_sheet(sheets[0])
        else:
            raise ValueError

    def check_settings(self):
        '''Do sanity checks on the different settings.'''

        if self.defs.duplex and self.questionnaire.page_count % 2 != 0:
            print(_("A questionnaire that is printed in duplex needs an even amount of pages!"))
            return False

        if self.defs.style == 'classic' and self.questionnaire.page_count > 6:
            print(_("The 'classic' style only supports a maximum of six pages! Use the 'code128' style if you require more pages."))
            return False

        return True

    def validate_questionnaire_id(self, qid):
        """Do style specific sanity checks on the questionnaire ID."""

        if self.defs.style == "classic":
            # The ID needs to be an integer
            try:
                return int(qid)
            except ValueError:
                log.error(_("IDs need to be integers in \"classic\" style!"))
                sys.exit(1)
        elif self.defs.style == "code128":
            # Check each character for validity
            for c in str(qid):
                if not c in defs.c128_chars:
                    log.error(_("Invalid character %s in questionnaire ID \"%s\" in \"code128\" style!") % (c, qid))
                    sys.exit(1)
            return qid
        elif self.defs.style == "custom":
            log.error(_("SDAPS cannot draw a questionnaire ID with the \"custom\" style. Do this yourself somehow!"))
            sys.exit(1)
        elif self.defs.style == "qr":
          return qid
        else:
            AssertionError()


