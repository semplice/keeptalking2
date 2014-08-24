# -*- coding: utf-8 -*-
#
# KeepTalking library -- live library
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

import os

class Live:
	"""
	The Live class is an interface to Semplice Live's states, and can
	be used to set-up the live-mode after language selection.
	"""
	
	@property
	def is_live(self):
		"""
		Returns True if the system is in live mode, False if not.
		
		Note that Live mode is only with /etc/semplice-live-mode == 'yeahh',
		other states like 'nolock' will make this method return False.
		
		If you need to check for all live-mode states, simply test for
		/etc/semplice-live-mode.
		"""
		
		#return True
		
		if os.path.exists("/etc/semplice-live-mode"):
			with open("/etc/semplice-live-mode", "r") as f:
				line = f.readline().strip("\n")
				if line == "yeahh":
					LIVE = True
				else:
					LIVE = False
		else:
			LIVE = False
		
		return LIVE
	
	def set(self, mode="nolock"):
		"""
		Sets the specified live-mode.
		"""
		
		# Overwrite /etc/semplice-live-mode
		with open("/etc/semplice-live-mode","w") as f:
			f.write(mode + "\n")
	
	@property
	def skip_live(self):
		"""
		Returns True if the language selection can be skipped (i.e when
		the locale and keyboard layout have been specified in the cmdline),
		False if not.
		"""
		
		keyb = False
		lang = False
		
		with open("/proc/cmdline") as cmdline:
			line = cmdline.readline().strip("\n")
		
		# Split line
		line = line.split(" ")
		for arg in line:
			if "locales=" in arg:
				# lang is already selected!
				lang = True
			elif "keyboard-layouts=" in arg:
				# keyb is selected!
				keyb = True
		
		if keyb and lang:
			# If keyb and lang are selected, we can skip the laiv-setup prompt.
			return True
		else:
			return False
