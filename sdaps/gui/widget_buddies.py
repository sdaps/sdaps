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

from gi.repository import Gtk
from gi.repository import GLib
import cairo

from sdaps import model
from sdaps import defs

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def markup_escape_text(text):
    # Unfortunately the API returns a byte string, so we need to decode it
    # as the formatting would not work otherwise.
    return GLib.markup_escape_text(text)

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.Questionnaire

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)

        self.obj.connect_data_changed(self.data_changed)

        self._notify_ensure_visible = list()

    def data_changed(self, questionnaire, qobj, obj, name, old_value):
        # Simply sync everything on every change.
        self.sync_state()

    def create_widget(self):
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # First some global options
        widget = Gtk.Label()
        widget.set_markup(_('<b>Global Properties</b>'))
        widget.props.xalign = 0.0
        self.box.pack_start(widget, False, True, 0)

        self.valid_checkbox = Gtk.CheckButton.new_with_label(_('Sheet valid'))
        self.verified_checkbox = Gtk.CheckButton.new_with_label(_('Verified'))
        self.empty_checkbox = Gtk.CheckButton.new_with_label(_('Empty'))
        self.empty_checkbox.set_sensitive(False)

        self.valid_checkbox.connect('toggled', self.toggled_valid_cb)
        self.verified_checkbox.connect('toggled', self.toggled_verified_cb)

        indent = Gtk.Alignment()
        indent.set_padding(0, 0, 10, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.qid = Gtk.Label()
        self.qid.set_markup(_('<b>Questionnaire ID: </b>') + markup_escape_text(str(self.obj.survey.sheet.questionnaire_id)))
        self.qid.props.xalign = 0.0

        indent.add(vbox)

        vbox.add(self.qid)
        vbox.add(self.valid_checkbox)
        vbox.add(self.verified_checkbox)
        vbox.add(self.empty_checkbox)

        self.box.pack_start(indent, False, True, 0)

        # And all the questions
        for qobject in self.obj.qobjects:
            widget = qobject.widget.create_widget()
            if widget is not None:
                self.box.pack_start(widget, False, True, 0)

        return self.box

    def sync_state(self):
        for qobject in self.obj.qobjects:
            qobject.widget.sync_state()

        self.qid.set_markup(_('<b>Questionnaire ID: </b>') + markup_escape_text(str(self.obj.survey.sheet.questionnaire_id)))
        self.valid_checkbox.set_active(self.obj.survey.sheet.valid)
        self.verified_checkbox.set_active(self.obj.survey.sheet.verified)
        self.empty_checkbox.set_active(self.obj.survey.sheet.empty)

    def ensure_visible(self, widget):
        for func in self._notify_ensure_visible:
            func(widget)

    def connect_ensure_visible(self, func):
        self._notify_ensure_visible.append(func)

    def disconnect_ensure_visible(self, func):
        self._notify_ensure_visible.remove(func)

    def toggled_valid_cb(self, widget):
        self.obj.survey.sheet.valid = widget.get_active()

    def toggled_verified_cb(self, widget):
        self.obj.survey.sheet.verified = widget.get_active()

class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.QObject

    def create_widget(self):
        self.widget = None

        return self.widget

    def sync_state(self):
        for box in self.obj.boxes:
            box.widget.sync_state()

    def focus(self):
        self.obj.question.questionnaire.widget.ensure_visible(self.widget)

        if len(boxes) > 0:
            self.obj.boxes[0].widget.focus()


class Head(QObject, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.Head

    def create_widget(self):
        self.widget = Gtk.Label()
        self.widget.set_markup('<b>%s %s</b>' % (self.obj.id_str(), markup_escape_text(self.obj.title)))
        self.widget.props.xalign = 0.0

        return self.widget


class Question(QObject, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.Question

    def create_widget(self):
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.label = Gtk.Label()
        self.label.set_markup('<b>%s %s</b>' % (self.obj.id_str(), markup_escape_text(self.obj.question)))
        self.label.props.xalign = 0.0

        self.widget.pack_start(self.label, False, True, 0)

        indent = Gtk.Alignment()
        indent.set_padding(0, 0, 10, 0)
        self.widget.pack_end(indent, False, True, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        indent.add(vbox)

        for box in self.obj.boxes:
            widget = box.widget.create_widget()
            if widget is not None:
                vbox.pack_start(widget, False, True, 0)

        return self.widget

class Range(Question, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.Range

    def create_widget(self):
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.label = Gtk.Label()
        self.label.set_markup('<b>%s %s</b>' % (self.obj.id_str(), markup_escape_text(self.obj.question)))
        self.label.props.xalign = 0.0

        self.widget.pack_start(self.label, False, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lower_label = Gtk.Label()
        lower_label.set_text(self.obj.answers[0])
        lower_label.props.xalign = 1.0

        upper_label = Gtk.Label()
        upper_label.set_text(self.obj.answers[1])
        upper_label.props.xalign = 0.0

        sizegroup = Gtk.SizeGroup()
        sizegroup.set_mode(Gtk.SizeGroupMode.BOTH)
        sizegroup.add_widget(lower_label)
        sizegroup.add_widget(upper_label)

        hbox.pack_start(lower_label, True, True, 0)

        # Maybe use radiobuttons instead?
        for box in self.obj.boxes:
            widget = box.widget.create_widget()
            if widget is not None:
                hbox.pack_start(widget, False, True, 0)

        hbox.pack_start(upper_label, True, True, 0)

        self.widget.pack_start(hbox, False, True, 0)

        return self.widget


class Box(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.Checkbox

    def create_widget(self):
        if self.obj.text:
            self.widget = Gtk.CheckButton.new_with_label(self.obj.text)
        else:
            self.widget = Gtk.CheckButton.new_with_label('')
        self.widget.connect('toggled', self.toggled_cb)

        return self.widget

    def sync_state(self):
        self.widget.props.active = self.obj.data.state

    def toggled_cb(self, widget):
        self.obj.data.state = widget.props.active

    def focus(self):
        self.widget.grab_focus()

        self.obj.question.questionnaire.widget.ensure_visible(self.obj.question.widget.widget)
        self.obj.question.questionnaire.widget.ensure_visible(self.widget)

class Checkbox(Box, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.Checkbox


class Textbox(Box, metaclass=model.buddy.Register):

    name = 'widget'
    obj_class = model.questionnaire.Textbox

    def create_widget(self):
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.checkbox = Gtk.CheckButton.new_with_label(self.obj.text)
        self.checkbox.connect('toggled', self.toggled_cb)

        self.widget.add(self.checkbox)

        indent = Gtk.Alignment()
        indent.set_padding(0, 0, 10, 0)
        frame = Gtk.Frame()
        indent.add(frame)
        self.widget.pack_end(indent, False, True, 0)

        self.textbox = Gtk.TextView()
        self.textbox.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer = self.textbox.get_buffer()
        self.buffer.connect('changed', self.buffer_changed_cb)

        frame.add(self.textbox)

        return self.widget

    def buffer_changed_cb(self, buf):
        start = buf.get_start_iter()
        end = buf.get_end_iter()
        self.obj.data.text = buf.get_text(start, end, False)

    def sync_state(self):
        self.checkbox.props.active = self.obj.data.state

        self.textbox.props.sensitive = self.obj.data.state

        # Only update the text if it changed (or else recursion hits)
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        currtext = self.buffer.get_text(start, end, False)
        if self.obj.data.text != currtext:
            self.buffer.set_text(self.obj.data.text)

    def focus(self):
        if self.textbox.props.sensitive:
            self.textbox.grab_focus()
        else:
            self.checkbox.grab_focus()

        self.obj.question.questionnaire.widget.ensure_visible(self.obj.question.widget.widget)
        self.obj.question.questionnaire.widget.ensure_visible(self.widget)

