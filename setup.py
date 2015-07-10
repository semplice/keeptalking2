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

from distutils.core import setup

setup(name='keeptalking2',
	version='7.0.0',
	description='Library to interface with internationalization features',
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='http://github.com/semplice/keeptalking2',
	scripts=["service/keeptalking2-service.py"],
	data_files=[
		("/etc/dbus-1/system.d", ["service/org.semplicelinux.keeptalking2.conf"]),
		("/usr/share/dbus-1/system-services", ["service/org.semplicelinux.keeptalking2.service"]),
		("/usr/share/polkit-1/actions", ["service/org.semplicelinux.keeptalking2.policy"])
	],
	# package_dir={'bin':''},
	packages=["keeptalking2",],
	requires=['dbus', 'gi.repository.GLib', 'gi.repository.Polkit', 'gi.repository.Gio', 'time', 'fileinput', 'os', 'sys', 'shutil'],
)
