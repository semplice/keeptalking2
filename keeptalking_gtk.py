#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# KeepTalking -- GTK+ frontend
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

from keeptalking import core, Locale, Keyboard, TimeZone, Live
import os, sys
import t9n.library as t9n

import threading

from gi.repository import Gtk, GObject, Gdk

GObject.threads_init()

_ = t9n.translation_init("keeptalking")

# Get keeptalking main dir (a bit hacky and ugly)
MAINDIR = os.path.join(os.path.dirname(core.__file__), "../..")
uipath = os.path.join(MAINDIR, "keeptalking_gtk.glade")
if not os.path.exists(uipath): uipath = "/usr/share/keeptalking/keeptalking_gtk.glade"

live = Live.Live()
locale = Locale.Locale()
keyboard = Keyboard.Keyboard()
timezone = TimeZone.TimeZone()
tzone_countries = timezone.associate_timezones_to_countries()

class Apply(threading.Thread):
	def __init__(self, parent, lay, loc, var, mod, tim, savespace, savespacepurge):
		self.parent = parent
		
		self.lay = lay
		self.loc = loc
		self.var = var
		self.mod = mod
		self.tim = tim
		self.savespace = savespace
		self.savespacepurge = savespacepurge
	
		threading.Thread.__init__(self)
	
	def run(self):
		""" Do things! """
				
		## Set locale:
		try:
			if self.loc:
				GObject.idle_add(self.parent.progress_text.set_text, _("Setting locale..."))
				locale.set(self.loc)
			
			GObject.idle_add(self.parent.progress_bar.set_fraction, 0.2)
			
			if self.savespace:
				if not self.loc:
					loc = locale.default
				else:
					loc = self.loc
				GObject.idle_add(self.parent.progress_text.set_text, _("Enabling 'Save space' feature..."))
				locale.savespace_enable(loc)
			else:
				GObject.idle_add(self.parent.progress_text.set_text, _("Disabling 'Save space' feature..."))
				locale.savespace_disable()
			
			GObject.idle_add(self.parent.progress_bar.set_fraction, 0.4)
			
			if self.savespace and self.savespacepurge:
				if not self.loc:
					loc = locale.default
				else:
					loc = self.loc
				GObject.idle_add(self.parent.progress_text.set_text, _("Removing older translations... This may take a while."))
				locale.savespace_purge(loc)
			
			GObject.idle_add(self.parent.progress_bar.set_fraction, 0.6)
			
			## Set keyboard
			GObject.idle_add(self.parent.progress_text.set_text, _("Setting keyboard..."))
			keyboard.set(layout=self.lay, model=self.mod, variant=self.var)
			
			GObject.idle_add(self.parent.progress_bar.set_fraction, 0.8)
			
			## Set timezone
			if self.tim:
				GObject.idle_add(self.parent.progress_text.set_text, _("Setting timezone..."))
				timezone.set(self.tim)
			
			GObject.idle_add(self.parent.progress_bar.set_fraction, 1.0)
			
			if live.is_live:
				# If is_live, set semplice-live-mode accordingly.
				live.set()
				# quit
				self.parent.quit()
			
			GObject.idle_add(self.parent.main_window.hide)
			GObject.idle_add(self.parent.ok_dialog.show_all)
		except:
			GObject.idle_add(self.parent.main_window.hide)
			GObject.idle_add(self.parent.error_dialog.show_all)
			
class GUI:
	def __init__(self):
		""" Initialize the UI. """
		
		self.is_building = False
		
		self.savespace_activated = False
		self.purge_older_translations = None
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file(uipath)
		
		# Get window
		self.main_window = self.builder.get_object("keeptalking_window")
		self.main_window.connect("destroy", self.quit)
		
		# Get live box
		self.live_box = self.builder.get_object("live_box")
		
		# Get the other windows and relative buttons...
		self.error_dialog = self.builder.get_object("holyshit_dialog")
		self.error_dialog.connect("destroy", self.quit, 1)
		self.error_button = self.builder.get_object("holyshit_close")
		self.error_button.connect("clicked", self.quit, 1)
		self.ok_dialog = self.builder.get_object("daje_dialog")
		self.ok_dialog.connect("destroy", self.quit)
		self.daje_button = self.builder.get_object("daje_close")
		self.daje_button.connect("clicked", self.quit)
		
		self.savespace_dialog = self.builder.get_object("savespace_dialog")
		self.savespace_yes = self.builder.get_object("savespace_yes")
		self.savespace_yes.connect("clicked", self.on_savespace_yes)
		self.savespace_no = self.builder.get_object("savespace_no")
		self.savespace_no.connect("clicked", self.on_savespace_no)
		
		self.savespace_disabled_dialog = self.builder.get_object("savespace_disabled_dialog")
		self.savespace_disabled_close = self.builder.get_object("savespace_disabled_close")
		self.savespace_disabled_close.connect("clicked", self.on_savespace_disabled_close)
		
		# Get notebook
		self.notebook = self.builder.get_object("notebook")
		
		# Get buttons, and connect them
		self.ok_button = self.builder.get_object("ok_button")
		self.cancel_button = self.builder.get_object("cancel_button")
		self.ok_button.connect("clicked", self.on_ok_button_clicked)
		self.cancel_button.connect("clicked", self.quit)
		
		# Get progressbar
		self.progress_box = self.builder.get_object("progress_box")
		self.progress_text = self.builder.get_object("progress_text")
		self.progress_bar = self.builder.get_object("progress_bar")
				
		## LOCALE PAGE
		self.locale_frame = self.builder.get_object("locale_frame")
		
		## Create a treeview to attach to locale_frame
		self.locale_treeview = self.builder.get_object("locale_treeview")
		self.locale_treeview.connect("cursor-changed", self.on_locale_changed)
		self.locale_model = Gtk.ListStore(str, str, str)
		
		self.locale_treeview.set_model(self.locale_model)
		# Create cell
		self.locale_treeview.append_column(Gtk.TreeViewColumn("Locale", Gtk.CellRendererText(), text=1))
		self.locale_treeview.append_column(Gtk.TreeViewColumn("Codepage", Gtk.CellRendererText(), text=2))
		#self.locale_frame.add(self.locale_treeview)
		
		## Get the checkbox.
		self.locale_checkbox = self.builder.get_object("all_locales_checkbutton")
		
		## Tweaks
		self.tweaks_frame = self.builder.get_object("tweaks_frame")
		self.savespace_checkbox = self.builder.get_object("savespace_checkbox")
		
		# Populate
		if self.is_utf8(locale.default):
			self.populate_locale_model(all=False)
			self.locale_checkbox.set_active(False)
		else:
			self.populate_locale_model(all=True)
			self.locale_checkbox.set_active(True)

		self.locale_checkbox.connect("toggled", self.on_locale_checkbox_toggled)
		
		if locale.is_savingspace:
			self.savespace_activated = True
			self.savespace_checkbox.set_active(True)
		self.savespace_checkbox.connect("toggled", self.on_savespace_checkbox_toggled)

		## KEYBOARD PAGE
		self.keyboard_label = self.builder.get_object("keyblabel")
		## Create a treeview to attach to locale_frame
		self.layout_treeview = self.builder.get_object("layout_treeview")
		self.layout_model = Gtk.ListStore(str, str)
		
		self.layout_treeview.set_model(self.layout_model)
		# Create cell
		self.layout_treeview.append_column(Gtk.TreeViewColumn("Layout", Gtk.CellRendererText(), text=1))
		#self.layout_treeview.append_column(Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=1))
				
		# Populate
		self.populate_layout_model()
		
		## Create the variants treeview
		self.variant_treeview = self.builder.get_object("variant_treeview")
		self.layout_treeview.connect("cursor-changed", self.populate_variant_model)
		self.variant_model = Gtk.ListStore(str, str)
		
		self.variant_treeview.set_model(self.variant_model)
		# Create cell
		self.variant_treeview.append_column(Gtk.TreeViewColumn("Variant", Gtk.CellRendererText(), text=1))
		#self.layout_treeview.append_column(Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=1))
				
		# Populate
		self.populate_variant_model()
		
		## Create the model combobox
		self.model_combo = self.builder.get_object("model_combo")
		self.model_model = Gtk.ListStore(str, str)
		
		self.model_combo.set_model(self.model_model)
		# Create cell
		renderer_text = Gtk.CellRendererText()
		self.model_combo.pack_start(renderer_text, True)
		self.model_combo.add_attribute(renderer_text, "text", 1)
        #renderer_text = Gtk.CellRendererText()
        #country_combo.pack_start(renderer_text, True)
        #country_combo.add_attribute(renderer_text, "text", 0)
		
		self.populate_model_combo()

		## TIMEZONE PAGE
		self.timezone_label = self.builder.get_object("tzonelabel")
		## Create a treeview
		self.timezone_treeview = self.builder.get_object("timezone_treeview")
		self.timezone_treeview.connect("cursor-changed", self.on_timezone_changed)
		self.timezone_model = Gtk.ListStore(str, str)
		
		self.timezone_treeview.set_model(self.timezone_model)
		# Create cell
		self.timezone_treeview.append_column(Gtk.TreeViewColumn("Timezone", Gtk.CellRendererText(), text=0))
		# Populate
		self.populate_timezone_model()

		self.main_window.show_all()
		self.progress_box.hide()

		# Properly set things if live...
		if live.is_live:
			self.cancel_button.hide()
			self.tweaks_frame.hide()
		else:
			self.live_box.hide()

		# See if we are root...
		if os.environ["USER"] != "root":
			self.main_window.set_sensitive(False)
			self.error_dialog.set_title(_("You must be root!"))
			self.error_dialog.set_markup(_("<big><b>You must be root to use this application.</b></big>"))
			self.error_dialog.format_secondary_text(_("Ensure you have the proper rights to start this application."))
			self.error_dialog.show_all()
	
	def on_timezone_changed(self, obj):
		""" Fired when the timezone is changed. """

		# Make the tab label normal.
		self.timezone_label.set_markup(self.timezone_label.get_text().strip("<b>").strip("</b>"))
	
	def on_locale_changed(self, obj):
		""" Fired when the locale is changed on the first view. """
		
		if self.is_building: return
		
		loc = self.get_selected_locale()
		if not loc: return
		
		# Display warning if self.savespace_activated
		if self.savespace_activated:
			GObject.idle_add(self.main_window.set_sensitive, False)
			GObject.idle_add(self.savespace_disabled_dialog.show)
		
		# We need to set the keyboard layout!
		lay = loc.split(".")[0].split("@")[0].split("_")[1].lower()
		# We will use idle_add otherwise GUI will freeze for a few seconds (it should rebuild all layouts).
		GObject.idle_add(self.populate_layout_model, lay)
		
		# Set the variant too, if any
		var = loc.split(".")[0].split("@")[0].split("_")[0].lower()
		# We will use idle_add otherwise GUI will freeze for a few seconds (it should rebuild all layouts).
		GObject.idle_add(self.populate_variant_model, None, var)

		# We need to set the timezone!
		tzone = loc.split(".")[0].split("@")[0].split("_")[1].upper()
		if tzone in tzone_countries:
			# We will use idle_add otherwise GUI will freeze for a few seconds (it should rebuild all timezones).
			GObject.idle_add(self.populate_timezone_model, tzone_countries[tzone])
	
	def on_locale_checkbox_toggled(self, obj):
		""" Triggered when the locale checkbox has been toggled. """
		
		if obj.get_active():
			# Rebuild locale_model with all=True
			GObject.idle_add(self.populate_locale_model, True)
		else:
			# Rebuild locale_model with all=False
			GObject.idle_add(self.populate_locale_model, False)
	
	def is_utf8(self, _locale):
		""" Checks if the default locale is utf8. """
		
		if _locale in locale.codepages and locale.codepages[_locale] == "UTF-8":
			return True
		else:
			return False
	
	def get_selected_layouts(self):
		""" Gets the selected keyboard layouts. """
		
		# get selection
		selection = self.layout_treeview.get_selection()
		if not selection: return []
		model, paths = selection.get_selected_rows()
		
		values = []
		
		for path in paths:
			values.append(self.layout_model.get_value(self.layout_model.get_iter(path), 0))
		
		return values
	
	def get_selected_locale(self):
		""" Gets the selected locale. """
		
		# get selection
		selection = self.locale_treeview.get_selection()
		if not selection: return None
		model, itr = selection.get_selected()
		if not itr: return None
		
		
		return self.locale_model.get_value(itr, 0)

	def get_selected_variant(self):
		""" Gets the selected variant. """
		
		# get selection
		selection = self.variant_treeview.get_selection()
		if not selection: return None
		model, itr = selection.get_selected()
		
		return self.variant_model.get_value(itr, 0)

	def get_selected_model(self):
		""" Gets the selected model. """
		
		# get selection
		itr = self.model_combo.get_active_iter()
		
		return self.model_model.get_value(itr, 0)

	def get_selected_timezone(self):
		""" Gets the selected timezone. """
		
		# get selection
		selection = self.timezone_treeview.get_selection()
		if not selection: return None
		model, itr = selection.get_selected()
		
		return self.timezone_model.get_value(itr, 0)

	def on_savespace_checkbox_toggled(self, obj):
		""" Triggered when the savespace checkbox has been toggled. """
		
		if obj.get_active():
			# Enabled. Display savespace_dialog
			
			self.savespace_activated = True
			
			GObject.idle_add(self.main_window.set_sensitive, False)
			GObject.idle_add(self.savespace_dialog.show)
		else:
			# Disabled. Display warning dialog.
			
			self.savespace_activated = False
			
			GObject.idle_add(self.main_window.set_sensitive, False)
			GObject.idle_add(self.savespace_disabled_dialog.show)
	
	def on_savespace_yes(self, obj):
		""" Triggered when the Yes button has been pressed on the savespace dialog. """
		
		self.purge_older_translations = True

		GObject.idle_add(self.main_window.set_sensitive, True)
		GObject.idle_add(self.savespace_dialog.hide)

	def on_savespace_no(self, obj):
		""" Triggered when the No button has been pressed on the savespace dialog. """
		
		self.purge_older_translations = False

		GObject.idle_add(self.main_window.set_sensitive, True)
		GObject.idle_add(self.savespace_dialog.hide)

	def on_savespace_disabled_close(self, obj):
		""" Triggered when the Close button has been pressed on the savespace_disabled dialog. """
		
		GObject.idle_add(self.main_window.set_sensitive, True)
		GObject.idle_add(self.savespace_disabled_dialog.hide)

	def on_ok_button_clicked(self, obj):
		""" Triggered when the OK button has been clicked. """
		
		_lay = self.get_selected_layouts()
		_loc = self.get_selected_locale()
		_var = self.get_selected_variant()
		_mod = self.get_selected_model()
		_tim = self.get_selected_timezone()
		
		# Set to None unchanged things
		if locale.default == _loc: _loc = None
		if keyboard.default_layout == _lay: _lay = None
		if keyboard.default_variant == _var: _var = None
		if keyboard.default_model == _mod: _mod = None
		if timezone.default == _tim: _tim = None
		
		# Show box and make the notebook unsensitive
		self.progress_box.show()
		self.notebook.set_sensitive(False)
		
		self.cancel_button.set_sensitive(False)
		self.ok_button.set_sensitive(False)
		
		# Load Apply class, then run it
		clss = Apply(self, lay=_lay, loc=_loc, var=_var, mod=_mod, tim=_tim, savespace=self.savespace_activated, savespacepurge=self.purge_older_translations)
		clss.start()
	
	def populate_variant_model(self, caller=None, var=None):
		""" Populates self.variants_model. """

		if self.is_building: return
		self.is_building = True
		
		if caller:
			# If we have a caller, this is called when the user has selected another layout (or changed to the keyboard tab). So:
			# Make the tab label normal.
			self.keyboard_label.set_markup(self.keyboard_label.get_text().strip("<b>").strip("</b>"))

		print "REBUILDING VARIANT MODEL"
		
		default = None
		variantitr = None
		
		self.variant_model.clear()
		
		selected = self.get_selected_layouts()
		if len(selected) != 1:
			self.variant_treeview.set_sensitive(False)
			return
		else:
			self.variant_treeview.set_sensitive(True)
		
		models, layouts = keyboard.supported()
		variants = layouts[selected[0]]["variants"]
		
		for variant in variants:
			for item, key in variant.items():
				itr = self.variant_model.append([item, key])
				if item == keyboard.default_variant:
					# save the iter! ;)
					default = itr
				elif item == var:
					# save the iter! ;)
					variantitr = itr
		self.variant_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		reciter = self.variant_model.prepend([None, _("%s") % layouts[selected[0]]["description"]])
		
		# Set default		
		sel = self.variant_treeview.get_selection()
		if variantitr:
			sel.select_iter(variantitr)
		elif default:
			sel.select_iter(default)
		else:
			sel.select_iter(reciter)
		
		self.variant_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
		
		self.is_building = False
	
	def populate_layout_model(self, lay=None):
		""" Populates self.layout_model. """

		if self.is_building: return
		self.is_building = True

		# Make the tab label normal.
		self.keyboard_label.set_markup(self.keyboard_label.get_text().strip("<b>").strip("</b>"))

		print "REBUILDING LAYOUT MODEL"
		
		default = None
		layout = None
		
		self.layout_model.clear()
		
		models, layouts = keyboard.supported()
		
		for item, key in layouts.items():
			itr = self.layout_model.append([item, key["description"]])
			if item == keyboard.default_layout:
				# save the iter! ;)
				default = itr
			elif item == lay:
				# save the iter! ;)
				layout = itr
		self.layout_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
				
		# Set default
		sel = self.layout_treeview.get_selection()
		if layout:
			sel.select_iter(layout)
			self.layout_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			
			# Make the tab label bold.
			self.keyboard_label.set_markup("<b>%s</b>" % self.keyboard_label.get_text())
		elif default:
			sel.select_iter(default)
			self.layout_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			#self.locale_treeview.scroll_to_cell(default)
		
		sel.set_mode(Gtk.SelectionMode.MULTIPLE)
		
		self.is_building = False
	
	def populate_locale_model(self, all=False):
		""" Populates self.locale_model. """
		
		if self.is_building: return
		self.is_building = True
		
		self.main_window.set_sensitive(False)
		
		print "REBUILDING LOCALE MODEL"
		
		default = None
		
		self.locale_model.clear()
		
		for item, key in locale.human_form(all=all).items():
			if all:
				codepage = locale.codepages[item]
			else:
				codepage = ""
			itr = self.locale_model.append([item, key.split("-")[0], codepage])
			if item == locale.default:
				# save the iter! ;)
				default = itr
			self.locale_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		
		# Set default
		if default:
			sel = self.locale_treeview.get_selection()
			sel.select_iter(default)
			self.locale_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			#self.locale_treeview.scroll_to_cell(default)
		
		self.is_building = False
		
		self.main_window.set_sensitive(True)

	def populate_timezone_model(self, tzone=None):
		""" Populates self.timezone_model. """

		if self.is_building: return
		self.is_building = True

		# Make the tab label normal.
		self.timezone_label.set_markup(self.timezone_label.get_text().strip("<b>").strip("</b>"))

		print "REBUILDING TIMEZONE MODEL"
		
		default = None
		tzoneitr = None
		
		self.timezone_model.clear()
		
		for item, key in timezone.supported.items():
			for zone in key:
				zone1 = "%s/%s" % (item, zone)
				itr = self.timezone_model.append([zone1, zone])
				if zone1 == timezone.default:
					# save the iter! ;)
					default = itr
				elif zone1 == tzone:
					# save the iter! ;)
					tzoneitr = itr
		self.timezone_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
		
		# Set default
		if tzoneitr:
			sel = self.timezone_treeview.get_selection()
			sel.select_iter(tzoneitr)
			self.timezone_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])

			# Make the tab label bold.
			self.timezone_label.set_markup("<b>%s</b>" % self.timezone_label.get_text())
		elif default:
			sel = self.timezone_treeview.get_selection()
			sel.select_iter(default)
			self.timezone_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			#self.locale_treeview.scroll_to_cell(default)
		
		self.is_building = False

	def populate_model_combo(self):
		""" Populates self.model_combo """
		
		default = None
		pc105 = None
		
		self.model_model.clear()
		
		models, layouts = keyboard.supported()
		
		for item, key in models.items():
			itr = self.model_model.append([item, key])
			if item == keyboard.default_model:
				# save the iter ;)
				default = itr
			elif item == "pc105":
				# Save, fallback if no default
				pc105 = itr
		self.model_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		
		if default:
			self.model_combo.set_active_iter(default)
		else:
			self.model_combo.set_active_iter(pc105) # Do not check, pc105 MUST be there.
	
	def quit(self, obj=None, status=0):
		""" EXIT!!! """
		
		Gtk.main_quit()
		sys.exit(status)
		

if live.is_live:
	# Check!
	if live.skip_live: sys.exit(0)

g = GUI()

Gtk.main()
