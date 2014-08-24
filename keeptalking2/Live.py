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
