# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2007-2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2007-2008, Benjamin Berg <benjamin@sipsolutions.net>
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

"""
This modules contains a GTK+ user interface. With the help of this GUI it is
possible to manually correct the automatic recognition and do basic debugging.
"""

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
import os
import time
import sys
import signal

from sdaps import model
from sdaps import surface
from sdaps import recognize
from sdaps import clifilter
from sdaps import defs
from sdaps import paths
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

from .sheet_widget import SheetWidget
from . import buddies
from . import widget_buddies


zoom_steps = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
              1.25, 1.5, 2.0, 2.5, 3.0]


def gui(survey, cmdline):
    filter = clifilter.clifilter(survey, cmdline['filter'])
    provider = Provider(survey, filter)
    if not provider.images:
        log.error(_("The survey does not have any images! Please add images (and run recognize) before using the GUI."))
        return 1

    try:
        # Exit the mainloop if Ctrl+C is pressed in the terminal.
        GLib.unix_signal_add_full(GLib.PRIORITY_HIGH, signal.SIGINT, lambda *args : Gtk.main_quit(), None)
    except AttributeError:
        # Whatever, it is only to enable Ctrl+C anyways
        pass

    MainWindow(provider).run()


class Provider(object):

    def __init__(self, survey, filter, by_quality=False):
        self._by_quality = by_quality

        self.survey = survey
        self.images = list()
        self.qualities = list()
        self.survey.iterate(self, filter)
        self.qualities.sort(reverse=False)
        self.index = 0

        # There may be no images. This error is
        # caught and printed in the "gui" function.
        if not self.images:
            return

        self.image.surface.load_rgb()
        self.survey.goto_sheet(self.image.sheet)
        #self._surface = None

    def __call__(self):
        # Add all images that are "valid" ie. everything except back side of
        # a simplex printout.
        new_images = [img for img in self.survey.sheet.images if not img.ignored]

        # Try to sort the images, which may fail if the page numbers have not been
        # recognised
        try:
            new_images.sort(key=lambda Image: Image.page_number)
        except TypeError:
            pass

        self.images.extend(new_images)
        # Insert each image of the sheet into the qualities array
        for i in range(len(new_images)):
            self.qualities.append((self.survey.sheet.quality, len(self.qualities)))

    def next(self, cycle=True):
        if self.index >= len(self.images) - 1:
            if cycle:
                new_index = 0
            else:
                return False
        else:
            new_index = self.index + 1

        self.image.surface.clean()

        self.index = new_index

        self.image.surface.load_rgb()
        self.survey.goto_sheet(self.image.sheet)

        return True

    def previous(self, cycle=True):
        if self.index <= 0:
            if cycle:
                new_index = len(self.images) - 1
            else:
                return False
        else:
            new_index = self.index - 1

        self.image.surface.clean()

        self.index = new_index

        self.image.surface.load_rgb()
        self.survey.goto_sheet(self.image.sheet)

        return True

    def goto(self, index):
        if index >= 0 and index < len(self.images):
            self.image.surface.clean()
            self.index = index
            self.image.surface.load_rgb()
            self.survey.goto_sheet(self.image.sheet)

    def set_sort_by_quality(self, value):
        self.image.surface.clean()
        self._by_quality = value
        self.image.surface.load_rgb()
        self.survey.goto_sheet(self.image.sheet)

    def get_image(self):
        if self._by_quality:
            return self.images[self.qualities[self.index][1]]
        else:
            return self.images[self.index]

    image = property(get_image)


class MainWindow(object):

    def __init__(self, provider):
        self.about_dialog = None
        self.close_dialog = None
        self.ask_open_dialog = None
        self.provider = provider

        self._load_image = 0
        self._builder = Gtk.Builder()
        if paths.local_run:
            self._builder.add_from_file(
                os.path.join(os.path.dirname(__file__), 'main_window.ui'))
        else:
            self._builder.add_from_file(
                os.path.join(
                    paths.prefix,
                    'share', 'sdaps', 'ui', 'main_window.ui'))

        self._window = self._builder.get_object("main_window")
        self._builder.connect_signals(self)
        self._window.maximize()

        scrolled_window = self._builder.get_object("sheet_scrolled_window")
        self.sheet = SheetWidget(self.provider)
        self.sheet.show()
        scrolled_window.add(self.sheet)

        self.data_viewport = self._builder.get_object("data_view")
        widgets = provider.survey.questionnaire.widget.create_widget()
        widgets.show_all()
        self.data_viewport.add(widgets)

        provider.survey.questionnaire.widget.connect_ensure_visible(self.data_view_ensure_visible)

        self.sheet.connect('key-press-event', self.sheet_view_key_press)

        combo = self._builder.get_object("page_number_combo")
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)

        store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        store.append(row=(_("Page|Invalid"), -1))
        for i in range(self.provider.survey.questionnaire.page_count):
            store.append(row=(
                ungettext("Page %i", "Page %i", i + 1) % (i + 1), i + 1))

        combo.set_model(store)

        self.sheet.props.zoom = 0.2

        # So the buttons are insensitive
        self.update_ui()

    def zoom_in(self, *args):
        cur_zoom = self.sheet.props.zoom
        try:
            i = zoom_steps.index(cur_zoom)
            i += 1
            if i < len(zoom_steps):
                self.sheet.props.zoom = zoom_steps[i]
        except:
            self.sheet.props.zoom = 1.0

    def zoom_out(self, *args):
        cur_zoom = self.sheet.props.zoom
        try:
            i = zoom_steps.index(cur_zoom)
            i -= 1
            if i >= 0:
                self.sheet.props.zoom = zoom_steps[i]
        except:
            self.sheet.props.zoom = 1.0

    def null_event_handler(self, *args):
        return True

    def show_about_dialog(self, *args):
        if not self.about_dialog:
            self.about_dialog = Gtk.AboutDialog()
            self.about_dialog.set_program_name("SDAPS")
            #self.about_dialog.set_version("")
            self.about_dialog.set_authors(
                ["Benjamin Berg <benjamin@sipsolution.net>",
                 "Ferdinand Schwenk <ferdisdot@gmail.com>",
                 "Christoph Simon <post@christoph-simon.eu>",
                 "Tobias Simon <tobsimon@googlemail.com>"])
            self.about_dialog.set_copyright(_("Copyright © 2007-2014 The SDAPS Authors"))
            self.about_dialog.set_license_type(Gtk.License.GPL_3_0)
            self.about_dialog.set_comments(_("Scripts for data acquisition with paper based surveys"))
            self.about_dialog.set_website(_("http://sdaps.org"))
            self.about_dialog.set_translator_credits(_("translator-credits"))
            self.about_dialog.set_default_response(Gtk.ResponseType.CANCEL)

        self.about_dialog.set_transient_for(self._window)
        self.about_dialog.run()
        self.about_dialog.hide()

        return True

    def update_page_status(self):
        combo = self._builder.get_object("page_number_combo")
        turned_toggle = self._builder.get_object("turned_toggle")

        # Update the combobox
        if self.provider.image.survey_id == self.provider.survey.survey_id:
            page_number = self.provider.image.page_number
        else:
            page_number = -1

        # Find the page_number in the model
        model = combo.get_model()
        iter = model.get_iter_first()

        while iter:
            i = combo.get_model().get(iter, 1)[0]
            if page_number == i:
                combo.set_active_iter(iter)
                iter = None
            else:
                iter = model.iter_next(iter)

        # Update the toggle
        turned_toggle.set_active(self.provider.image.rotated or False)

    def update_ui(self):
        # Update the next/prev button states
        #next_button = self._builder.get_object("forward_toolbutton")
        #prev_button = self._builder.get_object("backward_toolbutton")

        #next_button.set_sensitive(True)
        #prev_button.set_sensitive(True)

        position_label = self._builder.get_object("position_label")
        quality_label = self._builder.get_object("quality_label")
        page_spin = self._builder.get_object("page_spin")
        position_label.set_text(_(" of %i") % len(self.provider.images))
        quality_label.set_text(_("Recognition Quality: %.2f") % self.provider.image.sheet.quality)
        #position_label.props.sensitive = True
        page_spin.set_range(1, len(self.provider.images))
        page_spin.set_value(self.provider.index + 1)

        self.update_page_status()
        self.sheet.update_state()

        self.provider.survey.questionnaire.widget.sync_state(self.provider.image)

    def go_to_previous_page(self, *args):
        if not self.provider.previous(cycle=False):
            dialog = Gtk.MessageDialog(
                flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.CANCEL,
                message_format=_("You have reached the first page of the survey. Would you like to go to the last page?"))
            dialog.set_transient_for(self._window)
            dialog.add_button(_("Go to last page"), Gtk.ResponseType.OK)
            if dialog.run() == Gtk.ResponseType.OK:
                self.provider.previous(cycle=True)
            dialog.destroy()
        self.update_ui()
        return True

    def go_to_page(self, page):
        if page == self.provider.index:
            return True

        self.provider.goto(int(page))

        self.update_ui()
        return True

    def go_to_next_page(self, *args):
        if not self.provider.next(cycle=False):
            dialog = Gtk.MessageDialog(
                flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.CANCEL,
                message_format=_("You have reached the last page of the survey. Would you like to go to the first page?"))
            dialog.set_transient_for(self._window)
            dialog.add_button(_("Go to first page"), Gtk.ResponseType.OK)
            if dialog.run() == Gtk.ResponseType.OK:
                self.provider.next(cycle=True)
            dialog.destroy()

        self.update_ui()
        return True

    def page_spin_value_changed_cb(self, *args):
        page_spin = self._builder.get_object("page_spin")
        page = page_spin.get_value() - 1
        self.go_to_page(page)

    def page_number_combo_changed_cb(self, *args):
        combo = self._builder.get_object("page_number_combo")
        active = combo.get_active_iter()
        page_number = combo.get_model().get(active, 1)[0]
        if self.provider.image.page_number != page_number:
            if page_number != -1:
                self.provider.image.page_number = page_number
                self.provider.image.survey_id = self.provider.survey.survey_id
            elif self.provider.image.survey_id == self.provider.survey.survey_id:
                # Keep the values as is if it belongs to another survey
                self.provider.image.page_number = None
                self.provider.image.survey_id = None
            self.update_ui()
            return False

    def turned_toggle_toggled_cb(self, *args):
        toggle = self._builder.get_object("turned_toggle")
        rotated = toggle.get_active()
        if self.provider.image.rotated != rotated:
            self.provider.image.rotated = rotated
            self.provider.image.surface.load_rgb()
            self.update_ui()
        return False

    def quality_sort_toggle_toggled_cb(self, *args):
        toggle = self._builder.get_object("quality_sort_toggle")
        self.provider.set_sort_by_quality(toggle.get_active())
        self.update_ui()
        return False

    def toggle_fullscreen(self, *args):
        flags = self._window.get_window().get_state()
        if flags & Gdk.WindowState.FULLSCREEN:
            self._window.unfullscreen()
        else:
            self._window.fullscreen()
        return True

    def run_recognition(self, *args):
        self.provider.survey.questionnaire.recognize.recognize(skip_identify=True,
                                                               image=self.provider.image)
        # We need to re-load the page as it gets cleared
        self.provider.image.surface.load_rgb()
        return True

    def save_project(self, *args):
        self.provider.survey.save()
        return True

    def data_view_ensure_visible(self, widget):
        allocation = widget.get_allocation()

        vadj = self.data_viewport.props.vadjustment
        lower = vadj.props.lower
        upper = vadj.props.upper
        value = vadj.props.value
        page_size = vadj.props.page_size

        value = max(value, allocation.y + allocation.height - page_size)
        value = min(value, allocation.y)
        value = max(value, lower)
        value = min(value, upper)

        vadj.props.value = value

    def sheet_view_key_press(self, window, event):
        # Go to the next when Enter or Tab is pressed
        enter_keyvals = [Gdk.keyval_from_name(k) for k in ["Return", "KP_Enter", "ISO_Enter"]]
        if event.keyval in enter_keyvals:
            # If "Return" is pressed, then the examiner figured that the data
            # is good.

            # Mark as verified
            self.provider.image.verified = True

            # Mark the sheet as valid if it is verified
            if self.provider.image.sheet.verified:
                self.provider.image.sheet.valid = True

            if event.state & Gdk.ModifierType.SHIFT_MASK:
                self.go_to_previous_page()
            else:
                self.go_to_next_page()
            return True
        elif event.keyval == Gdk.KEY_Tab or event.keyval == Gdk.KEY_KP_Tab or event.keyval == Gdk.KEY_ISO_Left_Tab:
            # Allow tabbing out with Ctrl
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                return False

            if event.state & Gdk.ModifierType.SHIFT_MASK:
                self.go_to_previous_page()
            else:
                self.go_to_next_page()
            return True

        return False

    def quit_application(self, *args):
        if not self.close_dialog:
            self.close_dialog = Gtk.MessageDialog(
                parent=self._window,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING)
            self.close_dialog.add_buttons(
                _("Close without saving"), Gtk.ResponseType.CLOSE,
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
            self.close_dialog.set_markup(
                _("<b>Save the project before closing?</b>\n\nIf you do not save you may lose data."))
            self.close_dialog.set_default_response(Gtk.ResponseType.CANCEL)

        response = self.close_dialog.run()
        self.close_dialog.hide()

        if response == Gtk.ResponseType.CLOSE:
            Gtk.main_quit()
            return False
        elif response == Gtk.ResponseType.OK:
            self.save_project()
            Gtk.main_quit()
            return False
        else:
            return True

    def run(self):
        self._window.show()
        Gtk.main()


