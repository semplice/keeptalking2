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

BUS_NAME = "org.freedesktop.timedate1"

class TimeZone:
	"""
	The TimeZone class is an interface to the current and supported
	Timezones.
	"""
	
	def __init__(self):
		"""
		Initialization.
		"""
		
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
		"""
		Returns the default timezone.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		with open("/etc/timezone") as f:
			tzone = f.readline().replace("\n","")
		
		return tzone

	@property		
	def supported(self):
		"""
		This will list all available timezones, directly via /usr/share/zoneinfo.
		"""

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
		"""
		Associates know timezones in supported to their country.
		Returns the associated dictionary.
		"""
		
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
		"""
		Permanently set the selected timezone.
		
		This is an 'offline' method, so the target will be respected
		and DBus will not be used.
		"""
		
		if tzone.startswith("Other/"):
			tzone.replace("Other/","")
		
		with open("/etc/timezone", "w") as f:
			f.write(tzone + "\n")
				
		if os.path.exists("/etc/localtime"):
			os.remove("/etc/localtime")
		shutil.copy2("/usr/share/zoneinfo/%s" % (tzone),"/etc/localtime")
		
