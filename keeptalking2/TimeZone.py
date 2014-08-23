# -*- coding: utf-8 -*-
#
# KeepTalking library -- TimeZone mdoule
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

from gi.repository import Gio

import os, shutil
import keeptalking2.core as core

BUS_NAME = "org.freedesktop.timedate1"

class TimeZone:
	
	def __init__(self):
		
		# Enter in the bus
		self.bus_cancellable = Gio.Cancellable()
		self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, self.bus_cancellable)
		self.TimeZone = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/timedate1",
			BUS_NAME,
			self.bus_cancellable
		)
		self.TimeZoneProperties = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/timedate1",
			"org.freedesktop.DBus.Properties",
			self.bus_cancellable
		) # Really we should create a new proxy to get the properties?!
	
	@property
	def default(self):
		"""
		Returns the default timezone.
		"""
		
		return self.TimeZoneProperties.Get('(ss)', BUS_NAME, 'Timezone')
	
	@property
	def default_offline(self):
		""" Returns the default timezone. """
		
		with open("/etc/timezone") as f:
			tzone = f.readline().replace("\n","")
		
		return tzone

	@property		
	def supported(self):
		""" This will list all available timezones, directly via /usr/share/zoneinfo. """

		supported = {}
		
		for root, dirs, files in os.walk("/usr/share/zoneinfo/"):
			
			n = root.replace("/usr/share/zoneinfo/","").split("/")
			if n[0] == "": # zoneinfo
				n = "Other"
			else:
				n = "/".join(n)
			
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
		"""
		Permanently set the selected timezone.
		"""
		
		self.TimeZone.SetTimezone(
			'(sb)',
			tzone,
			True # User interaction
		)
	
	def set_offline(self, tzone):
		""" Permanently set the selected timezone. """
		
		if tzone.startswith("Other/"):
			tzone.replace("Other/","")
		
		with open("/etc/timezone", "w") as f:
			f.write(tzone + "\n")
				
		if os.path.exists("/etc/localtime"):
			os.remove("/etc/localtime")
		shutil.copy2("/usr/share/zoneinfo/%s" % (tzone),"/etc/localtime")
		
