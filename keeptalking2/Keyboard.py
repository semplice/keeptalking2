# -*- coding: utf-8 -*-
#
# KeepTalking library -- Keyboard mdoule
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

from gi.repository import Gio

import fileinput, os, sys
import keeptalking2.core as core

BUS_NAME = "org.freedesktop.locale1"

class Keyboard:
	"""
	The Keyboard class is an interface to the current and supported Keyboard
	layouts, models and variants.
	"""
	
	def __init__(self, target="/"):
		"""
		Initialization.
		"""
		
		self.target = target
		
		if os.path.exists(os.path.join(self.target, "etc/default/keyboard")):
			# Debian
			self.KEYBFILE = os.path.join(self.target, "etc/default/keyboard")
		else:
			# Older Debian; Ubuntu
			self.KEYBFILE = os.path.join(self.target, "etc/default/console-setup")
		
		# Enter in the bus
		self.bus_cancellable = Gio.Cancellable()
		self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, self.bus_cancellable)
		self.Keyboard = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/locale1",
			BUS_NAME,
			self.bus_cancellable
		)
		self.KeyboardProperties = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/locale1",
			"org.freedesktop.DBus.Properties",
			self.bus_cancellable
		) # Really we should create a new proxy to get the properties?!

	@property
	def default_layout(self):
		"""
		Returns the current keyboard layout.
		"""
		
		return self.KeyboardProperties.Get('(ss)', BUS_NAME, 'X11Layout')

	@property
	def default_layout_offline(self):
		"""
		Returns the current keyboard layout.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		catched = None
		
		# Catch XKBLAYOUT into the KEYBFILE
		with open(self.KEYBFILE) as f:
			for line in f.readlines():
				if line[0] != "#":
					line = line.split("=")
					if line[0] == "XKBLAYOUT":
						catched = line[1].replace('"','').replace('\n','')
						break
		
		return catched

	@property
	def default_model(self):
		"""
		Returns the current keyboard model.
		"""
		
		return self.KeyboardProperties.Get('(ss)', BUS_NAME, 'X11Model')

	@property
	def default_model_offline(self):
		"""
		Returns the current keyboard model.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		catched = None
		
		# Catch XKBMODEL into the KEYBFILE
		with open(self.KEYBFILE) as f:
			for line in f.readlines():
				if line[0] != "#":
					line = line.split("=")
					if line[0] == "XKBMODEL":
						catched = line[1].replace('"','').replace('\n','')
						break
		
		return catched
	
	@property
	def default_variant(self):
		"""
		Returns the current keyboard variant.
		"""
		
		return self.KeyboardProperties.Get('(ss)', BUS_NAME, 'X11Variant')
	
	@property
	def default_variant_offline(self):
		"""
		Returns the current keyboard variant.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		catched = None
		
		# Catch XKBVARIANT into the KEYBFILE
		with open(self.KEYBFILE) as f:
			for line in f.readlines():
				if line[0] != "#":
					line = line.split("=")
					if line[0] == "XKBVARIANT":
						catched = line[1].replace('"','').replace('\n','')
						break
		
		return catched	
	
	@property
	def default(self):
		"""
		Layout, model, variant, options: all together.
		"""
		
		return "%(layout)s:%(model)s%(variant)s" % {
				"layout": self.default_layout,
				"model": self.default_model,
				"variant": ":%s" % self.default_variant if self.default_variant else ""
			}
	
	@property
	def default_offline(self):
		"""
		Layout, model, variant, options: all together.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		return "%(layout)s:%(model)s%(variant)s" % {
				"layout": self.default_layout_offline,
				"model": self.default_model_offline,
				"variant": ":%s" % self.default_variant_offline if self.default_variant_offline else ""
			}

	@property
	def supported_walking(self):
		"""
		Returns a dictionary with supported keymaps.
		"""
		
		supported = {}
		
		# Walk in /usr/share/keymaps
		for root, dirs, files in os.walk("/usr/share/keymaps/i386"):
			n = os.path.basename(root)
			if n == "i386": continue
			
			_sup = []
			
			for fil in files:
				_sup.append(fil.split(".")[0])
			
			# Add to supported
			supported[n] = tuple(_sup)
		
		return supported
	
	def supported(self):
		"""
		Returns a dictionary with supported models, layout (with variants).
		"""
		
		models = {}
		layouts = {}
		
		current = None
		
		with open("/usr/share/X11/xkb/rules/base.lst", "r") as f:
			for line in f.readlines():
				line = line.replace("\n","")
				if not line: continue
				if line == "! model":
					# Beginning with model!
					current = "model"
					continue
				elif line == "! layout":
					# Continuing with layout!
					current = "layout"
					continue
				elif line == "! variant":
					# Finishing with variant!
					current = "variant"
					continue
				elif line == "! option":
					current = "option"
					continue
				else:
					
					# Stript the first 2 spaces and split.
					line = line[2:].split(" ")
					
					# First item is ALWAYS the layout/model code. The non-empty rest is the description.
					item = line[0]
					desc = []
					for word in line[1:]:
						if word: desc.append(word)
					desc = " ".join(desc)
					
					if current == "model":
						# Add to models!
						models[item] = desc
					elif current == "layout":
						# Add to layouts!
						layouts[item] = {"description": desc, "variants": []}
					elif current == "variant":
						# Add to variants of the layout!
						# Obtain the layout
						desc = desc.split(":")
						if len(desc) == 1: continue
						lay = desc[0]
						desc_ = []
						for boh in desc[1].split(" "):
							if boh: desc_.append(boh)
						desc = " ".join(desc_)
						
						layouts[lay]["variants"].append({item:desc})
		
		return models, layouts
	
	def supported_variants(self, layout):
		"""
		Returns a tuple of available variants for layout.
		"""
		
		available = []
		
		fil = "/usr/share/X11/xkb/symbols/%s" % layout
		
		if not os.path.exists(fil): return ()
		
		with open(fil, "r") as f:
			for line in f.readlines():
				if "xkb_symbols" in line:
					line = line.split(" ")
					available.append(line[1].replace('"', ''))
		
		return tuple(available)
	
	def is_supported(self, layout):
		"""
		Returns True if the layout is supported, False if not.
		"""
		
		for typ, lst in self.supported.items():
			if layout in lst:
				return True
		
		return False
	
	def set(self, layout=None, model=None, variant=None):
		"""
		Sets the desired layout and model.
		"""
		
		self.Keyboard.SetX11Keyboard(
			'(ssssbb)',
			layout if layout else self.default_layout,
			model if model else self.default_model,
			variant if variant else self.default_variant,
			"", # options (not supported yet)
			True, # convert
			True # User interaction
		)

	def set_offline(self, layout=None, model=None, variant=None):
		"""
		Sets the desired layout and model.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		for line in fileinput.input(self.KEYBFILE,inplace=1):
			# WARNING: Ugly-ness excess in this for
			if line[0] != "#":
				splitted = line.split("=")
				if splitted[0] == "XKBLAYOUT":
					if layout != None and layout != []:
						if type(layout) == list: layout = ",".join(layout)
						sys.stdout.write(line.replace("XKBLAYOUT=%s" % (splitted[1]),"XKBLAYOUT=\"%s\"" % (layout)) + "\n")
					else:
						sys.stdout.write(line)
				elif splitted[0] == "XKBMODEL":
					if model != None:
						sys.stdout.write(line.replace("XKBMODEL=%s" % (splitted[1]),"XKBMODEL=\"%s\"" % (model)) + "\n")
					else:
						sys.stdout.write(line)
				elif splitted[0] == "XKBVARIANT":
					if variant != None:
						sys.stdout.write(line.replace("XKBVARIANT=%s" % (splitted[1]),"XKBVARIANT=\"%s\"" % (variant)) + "\n")
					else:
						sys.stdout.write(line)
				else:
					sys.stdout.write(line)
			else:
				sys.stdout.write(line)

		if layout:
			if os.path.exists(os.path.join(self.target, "usr/sbin/install-keymap")):
				if self.target is not "/":
					core.sexec("chroot %s install-keymap %s" % (self.target,layout))
				else:
					core.sexec("install-keymap %s" % (layout))
