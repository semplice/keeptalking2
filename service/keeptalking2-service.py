#!/usr/bin/python3
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

from keeptalking2.Locale import Locale

import sys

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from gi.repository import GLib, Polkit

TIMEOUT_LENGTH = 5 * 60

class Service(dbus.service.Object):
	"""
	A DBus service needed to fix the nonsense of logind.
	"""
	
	def on_timeout_elapsed(self):
		"""
		Fired when the timeout elapsed.
		"""
		
		self.mainloop.quit()
		
		return False
	
	def remove_timeout(self):
		"""
		Removes the timeout.
		"""

		if self.timeout > 0:
			# Timeout already present, cancel it
			GLib.source_remove(self.timeout)
	
	def add_timeout(self):
		"""
		Timeout.
		"""
		
		self.timeout = GLib.timeout_add_seconds(TIMEOUT_LENGTH, self.on_timeout_elapsed)
	
	def __init__(self):
		"""
		Initialization.
		"""
		
		self.timeout = 0
		
		self.mainloop = None
		self.Locale = Locale(no_dbus=True)
		
		self.bus_name = dbus.service.BusName("org.semplicelinux.keeptalking2", bus=dbus.SystemBus())
		
		self.add_timeout()
		
		# Get polkit authority
		self.authority = Polkit.Authority.get_sync()
		
		super().__init__(self.bus_name, "/org/semplicelinux/keeptalking2")
	
	def start_mainloop(self):
		"""
		Creates and starts the main loop.
		"""
		
		self.mainloop = GLib.MainLoop()
		self.mainloop.run()
	
	def is_authorized(self, sender, connection, privilege, user_interaction=True):
		"""
		Checks if the sender has the given privilege.
		
		Returns True if yes, False if not.
		"""
		
		if not user_interaction:
			flags = Polkit.CheckAuthorizationFlags.NONE
		else:
			flags = Polkit.CheckAuthorizationFlags.ALLOW_USER_INTERACTION
		
		# Get PID
		pid = dbus.Interface(
			dbus.SystemBus().get_object(
				"org.freedesktop.DBus",
				"/org/freedesktop/DBus"
			),
			"org.freedesktop.DBus"
		).GetConnectionUnixProcessID(sender)
		
		try:
			result = self.authority.check_authorization_sync(
				Polkit.UnixProcess.new(pid),
				privilege,
				None,
				flags,
				None
			)
		except:
			return False
		
		return result.get_is_authorized()
	
	@dbus.service.method(
		"org.semplicelinux.keeptalking2",
		in_signature="sb",
		sender_keyword="sender",
		connection_keyword="connection"
	)
	def GenerateLocales(self, locale, user_interaction, sender, connection):
		"""
		This method generates the specified locale.
		
		This really doesn't belong here, but directly in logind.
		I don't know why the SetLocale() call does not update /etc/locale.gen
		and generates (if needed) the new locale, maybe they expect every
		linux box to have all possible locales already generated?
		
		NONSENSE.
		"""
		
		if not self.is_authorized(sender, connection, "org.semplicelinux.keeptalking2.generate-locales", user_interaction):
			raise Exception("E: Not authorized")
				
		self.remove_timeout()
		self.Locale.set_offline(locale, generateonly=True)
		self.add_timeout()

	@dbus.service.method(
		"org.semplicelinux.keeptalking2",
		in_signature="asb",
		sender_keyword="sender",
		connection_keyword="connection"
	)
	def CreateStamp(self, change_stamp, user_interaction, sender, connection):
		"""
		This method creates the specified locale-change stamps on every homedir.
		"""
		
		if not self.is_authorized(sender, connection, "org.semplicelinux.keeptalking2.create-stamp", user_interaction):
			raise Exception("E: Not authorized")
		
		self.remove_timeout()
		self.Locale.create_stamp_offline(change_stamp)
		self.add_timeout()

	@dbus.service.method(
		"org.semplicelinux.keeptalking2",
		in_signature="sb",
		sender_keyword="sender",
		connection_keyword="connection"
	)
	def EnableSavespace(self, locale, user_interaction, sender, connection):
		"""
		This method enables the savespace feature.
		"""
		
		if not self.is_authorized(sender, connection, "org.semplicelinux.keeptalking2.change-savespace", user_interaction):
			raise Exception("E: Not authorized")
				
		self.remove_timeout()
		self.Locale.savespace_enable_offline(locale)
		self.add_timeout()

	@dbus.service.method(
		"org.semplicelinux.keeptalking2",
		in_signature="b",
		sender_keyword="sender",
		connection_keyword="connection"
	)
	def DisableSavespace(self, user_interaction, sender, connection):
		"""
		This method disables the savespace feature.
		"""
		
		if not self.is_authorized(sender, connection, "org.semplicelinux.keeptalking2.change-savespace", user_interaction):
			raise Exception("E: Not authorized")
				
		self.remove_timeout()
		self.Locale.savespace_disable_offline()
		self.add_timeout()

	@dbus.service.method(
		"org.semplicelinux.keeptalking2",
		in_signature="sb",
		sender_keyword="sender",
		connection_keyword="connection"
	)
	def PurgeSavespace(self, locale, user_interaction, sender, connection):
		"""
		This method purges locale files not needed anymore.
		"""
		
		if not self.is_authorized(sender, connection, "org.semplicelinux.keeptalking2.change-savespace", user_interaction):
			raise Exception("E: Not authorized")
				
		self.remove_timeout()
		self.Locale.savespace_purge_offline(locale)
		self.add_timeout()

if __name__ == "__main__":	
	DBusGMainLoop(set_as_default=True)
	service = Service()
	
	# Ladies and gentlemen...
	service.start_mainloop()
