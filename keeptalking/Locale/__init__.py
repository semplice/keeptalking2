# -*- coding: utf-8 -*-
#
# KeepTalking library -- Locale mdoule
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

import os
import keeptalking.core as core

class Locale:
	def __init__(self, target="/"):
		
		self.target = target

	@property
	def default(self):
		""" Returns the default locale on the system. """
		
		target = None
		
		with open(os.path.join(self.target, "etc/default/locale")) as f:
			for line in f.readlines():
				if "LANG=" in line:
					target = line.strip('LANG="').strip('"\n')
					break
		
		return target

	@property
	def supported(self):
		""" Returns a tuple which contains supported locales. """
		
		final = []
		
		with open(os.path.join(self.target, "usr/share/i18n/SUPPORTED")) as f:
			for line in f.readlines():
				line = line.split(" ")[0] # Get only the first column
				final.append(line)
					
		return tuple(final)
	
	@property
	def codepages(self):
		""" Returns a dictionary which contains, for every supported locale, its own codepage. """
		
		codepages = {}
		
		with open(os.path.join(self.target, "usr/share/i18n/SUPPORTED")) as f:
			for line in f.readlines():
				line = line.split(" ")
				# First column is locale, the second is codepage.
				codepages[line[0]] = line[1].replace("\n","")

		return codepages

	def human_form(self, all=True):
		""" Returns a dictionary which contains, for every supported locale, its "human" form. """
		
		working = {}
		working_reverse = {}
		final = {}
		
		## PASS 1: loop through /usr/share/i18n/locales/ and get description for every locale
		for _file in os.listdir("/usr/share/i18n/locales/"):
			if "translit" in _file or "iso14651_t1" in _file or "POSIX" in _file: continue
						
			with open(os.path.join("/usr/share/i18n/locales/", _file)) as f:
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
		""" Returns the best locale (the first one) in supported, which should match (in part or fully) 'locale'. """
		
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
	
	def set(self, locale):
		""" Sets specified locale in the system's configuration. """
		
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
