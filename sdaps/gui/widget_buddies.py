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

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

# Mixin to provide lookup functionality for handles
class Switcher(object):

    def set_active_sheet(self, provider, handle):
        if provider is None:
            return

        provider.ensure_handle_active(handle)

    def iter_matching(self, keys):
        for provider, handle in keys:
            # Any None provider is simply always matched
            if provider is None:
                yield provider, handle
            elif provider.is_handle_active(handle):
                yield provider, handle

class Questionnaire(model.buddy.Buddy, Switcher):

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

    def create_widget(self, provider=None, handle=None):
        # XXX: Add "page" based options?
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # First some global options
        widget = Gtk.Label()
        widget.set_markup(_('<b>Global Properties</b>'))
        widget.props.xalign = 0.0
        self.box.pack_start(widget, False, True, 0)

        self.valid_checkbox = Gtk.CheckButton.new_with_label(_("Sheet valid"))
        self.verified_checkbox = Gtk.CheckButton.new_with_label(_("Verified"))
        self.empty_checkbox = Gtk.CheckButton.new_with_label(_("Empty"))
        self.empty_checkbox.set_sensitive(False)

        self.valid_checkbox.connect('toggled', self.toggled_valid_cb)
        self.verified_checkbox.connect('toggled', self.toggled_verified_cb)

        indent = Gtk.Alignment()
        indent.set_padding(0, 0, 10, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        indent.add(vbox)

        vbox.add(self.valid_checkbox)
        vbox.add(self.verified_checkbox)
        vbox.add(self.empty_checkbox)

        self.box.pack_start(indent, False, True, 0)

        # And all the questions
        for qobject in self.obj.qobjects:
            widget = qobject.widget.create_widget(provider, handle)
            if widget is not None:
                self.box.pack_start(widget, False, True, 0)

        return self.box

    def unref_widget(self, provider=None, handle=None):
        del self.box

        for qobject in self.obj.qobjects:
            qobject.widget.unref_widget(provider, handle)

    def sync_state(self):
        for qobject in self.obj.qobjects:
            qobject.widget.sync_state()

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

class QObject(model.buddy.Buddy, Switcher):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.QObject

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)

        self.widget = dict()

    def create_widget(self, provider=None, handle=None):
        self.widget[provider, handle] = None

        return self.widget[provider, handle]

    def unref_widget(self, provider=None, handle=None):
        del self.widget[provider, handle]

    def sync_state(self):
        for box in self.obj.boxes:
            box.widget.sync_state()

    def focus(self):
        for key in self.iter_matching(self.widget.iterkeys()):
            self.obj.question.questionnaire.widget.ensure_visible(self.widget[key])

        if len(boxes) > 0:
            self.obj.boxes[0].widget.focus()


class Head(QObject):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Head

    def create_widget(self, provider=None, handle=None):
        key = provider, handle

        self.widget[key] = Gtk.Label()
        self.widget[key].set_markup('<b>%s %s</b>' % (self.obj.id_str(), self.obj.title))
        self.widget[key].props.xalign = 0.0

        return self.widget[key]


class Question(QObject):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Question

    def create_widget(self, provider=None, handle=None):
        self.widget[provider, handle] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        label = Gtk.Label()
        label.set_markup('<b>%s %s</b>' % (self.obj.id_str(), self.obj.question))
        label.props.xalign = 0.0

        self.widget[provider, handle].pack_start(label, False, True, 0)

        indent = Gtk.Alignment()
        indent.set_padding(0, 0, 10, 0)
        self.widget[provider, handle].pack_end(indent, False, True, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        indent.add(vbox)

        for box in self.obj.boxes:
            widget = box.widget.create_widget(provider, handle)
            if widget is not None:
                vbox.pack_start(widget, False, True, 0)

        return self.widget[provider, handle]

class Mark(Question):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Mark

    def create_widget(self, provider=None, handle=None):
        self.widget[provider, handle] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        label = Gtk.Label()
        label.set_markup('<b>%s %s</b>' % (self.obj.id_str(), self.obj.question))
        label.props.xalign = 0.0

        self.widget[provider, handle].pack_start(label, False, True, 0)

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
            widget = box.widget.create_widget(provider, handle)
            if widget is not None:
                hbox.pack_start(widget, False, True, 0)

        hbox.pack_start(upper_label, True, True, 0)

        self.widget[provider, handle].pack_start(hbox, False, True, 0)

        return self.widget[provider, handle]


class Box(model.buddy.Buddy, Switcher):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Checkbox

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)

        self.widget = dict()

    def create_widget(self, provider=None, handle=None):
        self.widget[provider, handle] = Gtk.CheckButton.new_with_label(self.obj.text)
        self.widget[provider, handle].connect('toggled', self.toggled_cb, provider, handle)

        return self.widget[provider, handle]

    def free_widget(self, provider=None, handle=None):
        del self.widget[provider, handle]

    def sync_state(self):
        for key in self.iter_matching(self.widget.iterkeys()):
            self.widget[key].props.active = self.obj.data.state

    def toggled_cb(self, widget, provider, handle):
        self.set_active_sheet(provider, handle)

        self.obj.data.state = widget.props.active

    def focus(self):
        for key in self.iter_matching(self.widget.iterkeys()):
            self.widget[key].grab_focus()

            if key in self.obj.question.widget.widget:
                self.obj.question.questionnaire.widget.ensure_visible(self.obj.question.widget.widget[key])
            self.obj.question.questionnaire.widget.ensure_visible(self.widget[key])

class Checkbox(Box):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Checkbox


class Textbox(Box):

    __metaclass__ = model.buddy.Register
    name = 'widget'
    obj_class = model.questionnaire.Textbox

    def __init__(self, *args):
        model.buddy.Buddy.__init__(self, *args)

        self.widget = dict()
        self.checkbox = dict()
        self.textbox = dict()
        self.buffer = dict()

    def create_widget(self, provider=None, handle=None):
        key = provider, handle
        self.widget[key] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.checkbox[key] = Gtk.CheckButton.new_with_label(self.obj.text)
        self.checkbox[key].connect('toggled', self.toggled_cb, provider, handle)

        self.widget[key].add(self.checkbox[key])

        indent = Gtk.Alignment()
        indent.set_padding(0, 0, 10, 0)
        frame = Gtk.Frame()
        indent.add(frame)
        self.widget[key].pack_end(indent, False, True, 0)

        self.textbox[key] = Gtk.TextView()
        self.textbox[key].set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer[key] = self.textbox[key].get_buffer()
        self.buffer[key].connect('changed', self.buffer_changed_cb, provider, handle)

        frame.add(self.textbox[key])

        return self.widget[key]

    def free_widget(self, provider=None, handle=None):
        key = provider, handle

        del self.widget[key]
        del self.checkbox[key]
        del self.textbox[key]
        del self.buffer[key]

    def buffer_changed_cb(self, buf, provider, handle):
        self.set_active_sheet(provider, handle)

        start = buf.get_start_iter()
        end = buf.get_end_iter()
        self.obj.data.text = buf.get_text(start, end, False).decode('UTF-8')

    def sync_state(self):
        for key in self.iter_matching(self.widget.iterkeys()):
            self.checkbox[key].props.active = self.obj.data.state

            self.textbox[key].props.sensitive = self.obj.data.state

            # Only update the text if it changed (or else recursion hits)
            start = self.buffer[key].get_start_iter()
            end = self.buffer[key].get_end_iter()
            currtext = self.buffer[key].get_text(start, end, False).decode('UTF-8')
            if self.obj.data.text != currtext:
                self.buffer[key].set_text(self.obj.data.text)

    def focus(self):
        for key in self.iter_matching(self.widget.iterkeys()):
            if self.textbox[key].props.sensitive:
                self.textbox[key].grab_focus()
            else:
                self.checkbox[key].grab_focus()

            if key in self.obj.question.widget.widget:
                self.obj.question.questionnaire.widget.ensure_visible(self.obj.question.widget.widget[key])
            self.obj.question.questionnaire.widget.ensure_visible(self.widget[key])

