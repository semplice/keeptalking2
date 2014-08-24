# -*- coding: utf-8 -*-
#
# keeptalking2 - library to interface with internationalization features
# Copyright (C) 2012-2014  Eugenio "g7" Paolantonio
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Authors:
#    Eugenio "g7" Paolantonio <me@medesimo.eu>
#

from gi.repository import Gio

import os, shutil
import keeptalking2.core as core

BUS_NAME = "org.freedesktop.locale1"

class Locale:
	"""
	The Locale class is an interface to the current set locale and the
	other supported ones.
	"""
	
	def __init__(self, target="/"):
		"""
		Initialization.
		"""
		
		self.target = target

		# Enter in the bus
		self.bus_cancellable = Gio.Cancellable()
		self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, self.bus_cancellable)
		self.Locale = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/locale1",
			BUS_NAME,
			self.bus_cancellable
		)
		self.LocaleProperties = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/locale1",
			"org.freedesktop.DBus.Properties",
			self.bus_cancellable
		) # Really we should create a new proxy to get the properties?!

	@property
	def default(self):
		"""
		Returns the default locale on the system.
		"""
		
		for item in self.LocaleProperties.Get('(ss)', BUS_NAME, 'Locale'):
			if item.startswith("LANG="):
				return item.split("=")[-1]
		
		return None

	@property
	def default_offline(self):
		"""
		Returns the default locale on the system.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		target = None
		
		with open(os.path.join(self.target, "etc/default/locale")) as f:
			for line in f.readlines():
				if "LANG=" in line:
					target = line.strip('LANG="').strip('"\n')
					break
		
		return target

	@property
	def supported(self):
		"""
		Returns a tuple which contains supported locales.
		"""
		
		final = []
		
		with open(os.path.join(self.target, "usr/share/i18n/SUPPORTED")) as f:
			for line in f.readlines():
				line = line.split(" ")[0] # Get only the first column
				final.append(line)
					
		return tuple(final)
	
	@property
	def codepages(self):
		"""
		Returns a dictionary which contains, for every supported locale, its own codepage.
		"""
		
		codepages = {}
		
		with open(os.path.join(self.target, "usr/share/i18n/SUPPORTED")) as f:
			for line in f.readlines():
				line = line.split(" ")
				# First column is locale, the second is codepage.
				codepages[line[0]] = line[1].replace("\n","")

		return codepages
	
	@property
	def is_savingspace(self):
		"""
		Returns True if the 'Save space' function is enabled, False if not.
		"""
		
		if os.path.exists(os.path.join(self.target, "etc/dpkg/dpkg.cfg.d/keeptalking")):
			return True
		else:
			return False

	def human_form(self, all=True):
		"""
		Returns a dictionary which contains, for every supported locale, its "human" form.
		"""
		
		working = {}
		working_reverse = {}
		final = {}
		
		## PASS 1: loop through /usr/share/i18n/locales/ and get description for every locale
		for _file in os.listdir("/usr/share/i18n/locales/"):
			if "translit" in _file or "iso14651_t1" in _file or "POSIX" in _file: continue
						
			with open(os.path.join("/usr/share/i18n/locales/", _file), encoding="latin-1") as f:
				language = False
				territory = False
				while language == False or territory == False:
					line = f.readline().replace("\n","").replace("\t","")
					#print line[:9], language, territory
					if line[:8] == "language":
						# We discovered language!
						language = line.split('"')[1] # a bit ugly but, hey.
					elif line[:9] == "territory":
						territory = line.split('"')[1] # same as above.
				
			# Add to working
			if territory:
				
				desc = "%s (%s)" % (language, territory)
				if desc in working_reverse:
					desc = "%s/%s (%s)" % (language, _file, territory)
				
				working[_file] = desc
				working_reverse[desc] = _file
			else:
				
				desc = language
				if desc in working_reverse:
					desc = "%s/%s" % (language, _file)
				
				working[_file] = desc
				working_reverse[desc] = _file
					
		## PASS 2: associate every supported locale with the the human form defined in working
		codepages = self.codepages
		for locale in self.supported:
			splt = locale.split(".")
			base = splt[0]

			
			# Add to final!
			if base in working:
				# Get codepage
				codepage = codepages[locale]
				if codepage != "UTF-8" and all:
					final[locale] = working[base] + " - %s" % codepage
				elif codepage == "UTF-8":
					final[locale] = working[base]
			else:
				final[locale] = locale
		
		return final
	
	def get_best_locale(self, locale):
		"""
		Returns the best locale (the first one) in supported, which should match (in part or fully) 'locale'.
		"""
		
		if len(locale) == 2:
			# If we have only the two-letters code, we should make something like ll_LL.
			# Ex: it -> it_IT.
			locale = locale.lower() + "_" + locale.upper()
		
		best = False
		for line in self.supported:
			if locale in line:
				best = line
				break # Break here.
		
		if not best: return None
		
		return best
	
	def set(self, locale, generateonly=False):
		"""
		Sets the specified locale in the system's configuration.
		
		Please note that generateonly is ignored and it's only there
		for compatibility purposes.
		"""
		
		self.Locale.SetLocale(
			'(asb)',
			["LANG=%s" % locale],
			True # User interaction
		)
	
	def set_offline(self, locale, generateonly=False):
		"""
		Sets specified locale in the system's configuration.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		if not generateonly:
			with open(os.path.join(self.target, "etc/default/locale"),"w") as f:
				f.write("LANG=\"%s\"\n" % (locale))
		
		for _file in (os.path.join(self.target, "etc/locale.gen"), os.path.join(self.target, "etc/locale-gen.conf")):
			append = True
			with open(_file,"a+") as f:
				for line in f.readlines():
					line = line.split(" ")[0]
					if locale in line:
						# We found the locale: locale-gen knows of it. Then we do not need to append it.
						append = False
						break
				
				if append:
					f.write("%s %s\n" % (locale, self.codepages[locale]))
		
		# Generating locales
		if self.target is not "/":
			core.sexec("chroot %s /usr/sbin/locale-gen" % (self.target))
		else:
			core.sexec("/usr/sbin/locale-gen")
	
	def savespace_detect(self, locale):
		"""
		Internal.
		"""

		manlang = locale.split(".")[0].split("@")[0].split("_")[0].lower()
		
		basedir = os.path.join(self.target, "usr/share/locale/")
		
		# Get appropriate language.
		for lang in (locale.split(".")[0], locale.split(".")[0].split("@")[0], locale.split(".")[0].split("@")[0].split("_")[0]):
			lang = lang.lower()
			finaldir = os.path.join(basedir, lang)
			if os.path.exists(finaldir): break
		
		return manlang, lang, finaldir

	def savespace_enable(self, locale):
		"""
		Enables savespace for the language of the given locale.
		"""
				
		manlang, lang, finaldir = self.savespace_detect(locale)
				
		with open(os.path.join(self.target, "etc/dpkg/dpkg.cfg.d/keeptalking"), "w") as f:
			f.write("""## DPKG RULES FOR %(lang)s WRITTEN BY KEEPTALKING

# Drop every locale except %(lang)s
path-exclude=/usr/share/locale/*
path-include=%(finaldir)s/*
path-include=/usr/share/locale/locale.alias

# Drop man pages except english and %(manlang)s
path-exclude=/usr/share/man/*
path-include=/usr/share/man/man[1-9]/*
path-include=/usr/share/man/%(manlang)s*/*
""" % {"lang":lang, "manlang":manlang, "finaldir": finaldir})

	def savespace_disable(self):
		"""
		Disables savespace (if enabled)
		"""
		
		rules = os.path.join(self.target, "etc/dpkg/dpkg.cfg.d/keeptalking")
		if not os.path.exists(rules): return
		
		os.remove(rules)
	
	def savespace_purge(self, locale):
		"""
		Purges foreign locales.
		"""

		manlang, lang, finaldir = self.savespace_detect(locale)
		
		# Purge things on /usr/share/locale and /usr/share/man
		# Doing something like "dpkg-purge" which scans the dpkg config and removes everything from the
		# path-exclude and path-include variables would be way cooler, but hey.
		
		toremove = []
		
		for item in os.listdir(os.path.join(self.target, "usr/share/locale")):
			if item not in (lang, "locale.alias"): # skip the language directory and locale.alias
				toremove.append(os.path.join(self.target, "usr/share/locale/%s" % item))

		for item in os.listdir(os.path.join(self.target, "usr/share/man")):
			if item != manlang and not item.startswith("man"): # skip man* and language directory
				toremove.append(os.path.join(self.target, "usr/share/man/%s" % item))
		
		for item in toremove:	
			if os.path.isdir(item):
				shutil.rmtree(item)
			else:
				os.remove(item)
				

