# -*- coding: utf-8 -*-
#
# KeepTalking library -- live library
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

import os

class Live:
	@property
	def is_live(self):
		""" Checks if we are on the live environment. """
		
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
		# Overwrite /etc/semplice-live-mode
		with open("/etc/semplice-live-mode","w") as f:
			f.write(mode + "\n")
	
	@property
	def skip_live(self):
		""" If language AND keyboard layout are specified from command line, return True. Otherwise, return False. """
		
		keyb = False
		lang = False
		
		cmdline = open("/proc/cmdline")
		line = cmdline.readline()
		line = line.strip("\n")
		cmdline.close()
		
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
