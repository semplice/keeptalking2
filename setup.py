#!/usr/bin/env python
# keeptalking setup (using distutils)
# Copyright (C) 2012 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL license, version 3.

from distutils.core import setup

setup(name='keeptalking',
	version='3.10.0',
	description='Language/Keyboard/Timezone libraries',
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='http://launchpad.net/keeptalking',
	# package_dir={'bin':''},
	scripts=['keeptalking_gtk.py', 'keeptalking_cli.py'],
	packages=[
		"t9n",
		"keeptalking",
		"keeptalking.core",
		"keeptalking.Keyboard",
		"keeptalking.Live",
		"keeptalking.Locale",
		"keeptalking.TimeZone",
      ],
	data_files=[("/usr/share/keeptalking", ["keeptalking_gtk.glade", "restartgdm"]),("/usr/share/applications", ["keeptalking.desktop"]),("/usr/share/polkit-1/actions/", ["org.semplice-linux.pkexec.keeptalking.policy"])],
	requires=['gi.repository.Gtk', 'gi.repository.GObject', 'gi.repository.Gdk', 't9n', 'threading', 'gettext', 'time', 'locale', 'fileinput', 'os', 'sys', 'shutil'],
)
