#!/usr/bin/python3
# keeptalking setup (using distutils)
# Copyright (C) 2012 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL license, version 3.

from distutils.core import setup

setup(name='keeptalking2',
	version='6.20.0',
	description='Language/Keyboard/Timezone libraries',
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='http://github.com/semplice/keeptalking2',
	# package_dir={'bin':''},
	packages=[
		"keeptalking",
		"keeptalking.core",
		"keeptalking.Keyboard",
		"keeptalking.Live",
		"keeptalking.Locale",
		"keeptalking.TimeZone",
      ],
	requires=['gi.repository.Gtk', 'gi.repository.GObject', 'gi.repository.Gdk', 't9n', 'threading', 'gettext', 'time', 'locale', 'fileinput', 'os', 'sys', 'shutil'],
)
