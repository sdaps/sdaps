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
import cairo

from sdaps import model
from sdaps import defs

class Questionnaire(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
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
        # XXX: Add "page" based options?
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        for qobject in self.obj.qobjects:
            widget = qobject.widget.create_widget()
            if widget is not None:
                self.box.pack_start(widget, False, True, 0)

        return self.box

        return None

    def sync_state(self):
        for qobject in self.obj.qobjects:
            qobject.widget.sync_state()

    def ensure_visible(self, widget):
        for func in self._notify_ensure_visible:
            func(widget)

    def connect_ensure_visible(self, func):
        self._notify_ensure_visible.append(func)

    def disconnect_ensure_visible(self, func):
        self._notify_ensure_visible.remove(func)


class QObject(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
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


class Head(QObject):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Head

    def create_widget(self):
        self.widget = Gtk.Label()
        self.widget.set_markup('<b>%s %s</b>' % (self.obj.id_str(), self.obj.title))
        self.widget.props.xalign = 0.0

        return self.widget


class Question(QObject):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Question

    def create_widget(self):
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.label = Gtk.Label()
        self.label.set_markup('<b>%s %s</b>' % (self.obj.id_str(), self.obj.question))
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

class Mark(Question):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Mark

    def create_widget(self):
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.label = Gtk.Label()
        self.label.set_markup('<b>%s %s</b>' % (self.obj.id_str(), self.obj.question))
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


class Box(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Checkbox

    def create_widget(self):
        self.widget = Gtk.CheckButton.new_with_label(self.obj.text)
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

class Checkbox(Box):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Checkbox


class Textbox(Box):

    __metaclass__ = model.buddy.Register
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
        self.obj.data.text = buf.get_text(start, end, False).decode('UTF-8')

    def sync_state(self):
        self.checkbox.props.active = self.obj.data.state

        self.textbox.props.sensitive = self.obj.data.state

        # Only update the text if it changed (or else recursion hits)
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        currtext = self.buffer.get_text(start, end, False).decode('UTF-8')
        if self.obj.data.text != currtext:
            self.buffer.set_text(self.obj.data.text)

    def focus(self):
        if self.textbox.props.sensitive:
            self.textbox.grab_focus()
        else:
            self.checkbox.grab_focus()

        self.obj.question.questionnaire.widget.ensure_visible(self.obj.question.widget.widget)
        self.obj.question.questionnaire.widget.ensure_visible(self.widget)

