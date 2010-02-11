# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2007-2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2007-2008, Benjamin Berg <benjamin@sipsolutions.net>
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

import gobject
import gtk
import gtk.glade
import os
import time
import sys

from sdaps import model
from sdaps import surface
from sdaps import clifilter
from sdaps import defs
from sdaps import paths

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

from sheet_widget import SheetWidget
import buddies


zoom_steps = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
              1.25, 1.5, 2.0, 2.5, 3.0]


def gui (survey, *filter) :
	filter = clifilter.clifilter(survey, *filter)
	MainWindow(Provider(survey, filter)).run()


class Provider (object) :

	image = property(lambda self: self.images[self.index])

	def __init__ (self, survey, filter) :
		self.survey = survey
		self.images = list()
		self.survey.iterate(self, filter)
		self.index = 0
		self.image.surface.load()
		self.survey.goto_sheet(self.image.sheet)
		#self._surface = None

	def __call__ (self) :
		self.images.extend(list(self.survey.sheet.images))

	def next (self) : #, skip_valid = 1) :
		self.image.surface.clean()
		self.index += 1
		if self.index == len(self.images) :
			self.index = 0
		self.image.surface.load()
		self.survey.goto_sheet(self.image.sheet)

	def previous (self) : #, skip_valid = 1) :
		self.image.surface.clean()
		self.index -= 1
		if self.index < 0 :
			self.index = len(self.images) - 1
		self.image.surface.load()
		self.survey.goto_sheet(self.image.sheet)

	def goto (self, index) :
		if index >= 0 and index < len(self.images):
			self.image.surface.clean()
			self.index = index
			self.image.surface.load()
			self.survey.goto_sheet(self.image.sheet)


class MainWindow(object):

	def __init__(self, provider) :
		self.about_dialog = None
		self.close_dialog = None
		self.ask_open_dialog = None
		self.provider = provider

		self._load_image = 0
		if paths.local_run :
			self._glade = gtk.glade.XML(
			    os.path.join(os.path.dirname(__file__), 'main_window.glade'))
		else :
			self._glade = gtk.glade.XML(
			    os.path.join(
			        paths.prefix,
			        'share', 'sdaps', 'glade', 'main_window.glade'))

		self._window = self._glade.get_widget("main_window")
		self._glade.signal_autoconnect(self)
		self._window.maximize()

		scrolled_window = self._glade.get_widget("sheet_scrolled_window")
		self.sheet = SheetWidget(self.provider)
		scrolled_window.add(self.sheet)

		combo = self._glade.get_widget("page_number_combo")
		cell = gtk.CellRendererText()
		combo.pack_start(cell, True)
		combo.add_attribute(cell, 'text', 0)

		store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
		for i in range(self.provider.survey.questionnaire.page_count) :
			store.append(row = (
			    ungettext("Page %i", "Page %i", i + 1) % (i + 1), i + 1))

		combo.set_model(store)

		self.sheet.props.zoom = 0.2

		# So the buttons are insensitive
		self.update_ui()

	def on_zoom_in_toolbutton_clicked(self, *args):
		cur_zoom = self.sheet.props.zoom
		try:
			i = zoom_steps.index(cur_zoom)
			i += 1
			if i < len(zoom_steps):
				self.sheet.props.zoom = zoom_steps[i]
		except:
			self.sheet.props.zoom = 1.0

	def on_zoom_out_toolbutton_clicked(self, *args):
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
			self.about_dialog = gtk.AboutDialog()
			self.about_dialog.set_name("SDAPS")
			self.about_dialog.set_version("") #XXX: Version?
			self.about_dialog.set_authors([u"Benjamin Berg <benjamin@sipsolution.net>", u"Christoph Simon <christoph.simon@gmx.eu>"])
			self.about_dialog.set_copyright(_(u"Copyright © 2007-2008 Benjamin Berg, Christoph Simon"))
			self.about_dialog.set_license(_(u"GPL Version 3, 29 June 2007"))
			self.about_dialog.set_comments(_(u"Scripts for data acquisition with paper based surveys"))
			self.about_dialog.set_default_response(gtk.RESPONSE_CANCEL)

		self.about_dialog.run()
		self.about_dialog.hide()

		return True

	def update_page_status(self):
		combo = self._glade.get_widget("page_number_combo")
		turned_toggle = self._glade.get_widget("turned_toggle")

		# Update the combobox
		page_number = self.provider.image.page_number

		# Find the page_number in the model
		model = combo.get_model()
		iter = model.get_iter_first()

		while iter:
			i = combo.get_model().get(iter, 1)[0]
			if page_number == i :
				combo.set_active_iter(iter)
				iter = None
			else:
				iter = model.iter_next(iter)

		# Update the toggle
		turned_toggle.set_active(self.provider.image.rotated)

	def update_ui(self):
		# Update the next/prev button states
		#next_button = self._glade.get_widget("forward_toolbutton")
		#prev_button = self._glade.get_widget("backward_toolbutton")

		#next_button.set_sensitive(True)
		#prev_button.set_sensitive(True)

		position_label = self._glade.get_widget("position_label")
		page_spin = self._glade.get_widget("page_spin")
		position_label.set_text(_(u" of %i") % len(self.provider.images))
		#position_label.props.sensitive = True
		page_spin.set_range(1, len(self.provider.images))
		page_spin.set_value(self.provider.index + 1)

		self.update_page_status()
		self.sheet.update_state()

	def go_to_previous_page(self, *args):
		self.provider.previous()
		self.update_ui()
		return True

	def go_to_page(self, page):
		if page == self.provider.index :
			return True

		self.provider.goto(int(page))

		self.update_ui()
		return True

	def go_to_next_page(self, *args):
		self.provider.next()
		self.update_ui()
		return True

	def page_spin_value_changed_cb (self, *args):
		page_spin = self._glade.get_widget("page_spin")
		page = page_spin.get_value() - 1
		self.go_to_page(page)

	def page_number_combo_changed_cb (self, *args):
		combo = self._glade.get_widget("page_number_combo")
		active = combo.get_active_iter()
		page_number = combo.get_model().get(active, 1)[0]
		if self.provider.image.page_number != page_number:
			self.provider.image.page_number = page_number
			self.update_ui()
			return False

	def turned_toggle_toggled_cb (self, *args):
		toggle = self._glade.get_widget("turned_toggle")
		rotated = toggle.get_active()
		if self.provider.image.rotated != rotated :
			self.provider.image.rotated = rotated
			self.provider.image.surface.load()
			self.update_ui()
		return False

	def toggle_fullscreen(self, *args):
		flags = self._window.window.get_state()
		if flags & gtk.gdk.WINDOW_STATE_FULLSCREEN:
			self._window.unfullscreen()
		else:
			self._window.fullscreen()
		return True

	def save_project(self, *args):
		self.provider.survey.save()
		return True

	def window_key_press(self, window, event):
		# Go to the next when Enter or Tab is pressed
		# XXX: In openeva we supported a Verified flag, that would
		#      be set if Enter is pressed.
		if event.keyval == gtk.gdk.keyval_from_name("Return"):
			if event.state & gtk.gdk.SHIFT_MASK:
				self.go_to_previous_page()
			else:
				self.go_to_next_page()
			return True
		elif event.keyval == gtk.gdk.keyval_from_name("Tab"):
			if event.state & gtk.gdk.SHIFT_MASK:
				self.go_to_previous_page()
			else:
				self.go_to_next_page()
			return True

		return False

	def quit_application(self, *args):
		if not self.close_dialog:
			self.close_dialog = gtk.MessageDialog(parent=self._window, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_WARNING)
			self.close_dialog.add_buttons(_(u"Close with saving"), gtk.RESPONSE_CLOSE, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)
			self.close_dialog.set_markup(_(u"<b>Save the project before closing?</b>\n\nIf you do not save you may loose data."))
			self.close_dialog.set_default_response(gtk.RESPONSE_CANCEL)

		response = self.close_dialog.run()
		self.close_dialog.hide()

		if response == gtk.RESPONSE_CLOSE:
			gtk.main_quit()
			return False
		elif response == gtk.RESPONSE_OK:
			self.save_project()
			gtk.main_quit()
			return False
		else:
			return True

	def run(self):
		self._window.show_all()
		gtk.main()


