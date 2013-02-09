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

class Checkbox(Box):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Checkbox


class Textbox(Box):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Textbox



