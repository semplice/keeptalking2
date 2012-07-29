# -*- coding: utf-8 -*-
#
# KeepTalking library -- TimeZone mdoule
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

import os, shutil
import keeptalking.core as core

class TimeZone:
	@property
	def default(self):
		""" Returns the default timezone. """
		
		with open("/etc/timezone") as f:
			tzone = f.readline().replace("\n","")
		
		return tzone

	@property		
	def supported(self):
		""" This will list all available timezones, directly via /usr/share/zoneinfo. """

		supported = {}
		
		for root, dirs, files in os.walk("/usr/share/zoneinfo"):
			n = os.path.basename(root)
			if n == "zoneinfo": n = "Other"
			
			_sup = []
			
			for fil in files:
				_sup.append(fil)
			
			# Add to supported
			supported[n] = tuple(_sup)
		
		return supported
	
	def associate_timezones_to_countries(self):
		""" Associates know timezones in supported to their country.
		Returns the associated dictionary. """
		
		result = {}
		with open("/usr/share/zoneinfo/zone.tab", "r") as f:
			for line in f.readlines():
				if line[0] == "#": continue
				
				line = line.replace("\n","").split("\t")
				if not line[0] in result: result[line[0]] = line[2]
		
		return result
		
	
	def set(self, tzone):
		""" Permanently set the selected timezone. """
		
		with open("/etc/timezone", "w") as f:
			f.write(tzone + "\n")
				
		if os.path.exists("/etc/localtime"):
			os.remove("/etc/localtime")
		shutil.copy2("/usr/share/zoneinfo/%s" % (tzone),"/etc/localtime")
		
