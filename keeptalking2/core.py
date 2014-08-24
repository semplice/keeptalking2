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

import subprocess

__version__ = "7.0.0"

# External program except:
class CmdError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# User except:
class UserError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class execute:
	""" The execute class is a convenient class implemented to easily launch and control an external process. """
	
	def __init__(self, command, shell=True, custom_log=open("/tmp/keeptalking.log", "w")):
		self.command = command
		self.shell = shell
		self.custom_log = custom_log
		
		self.pid = None # Err... process not started... so pid is none ;)
	
	def start(self):
		""" The core function. Will launch self.command. """

		# If shell is False, we should pass to Popen a list, instead of a normal string.
		if not self.shell:
			proc = self.command.split(" ")
		else:
			proc = self.command
		
		self.process = subprocess.Popen(proc, shell=self.shell, stdout=self.custom_log, stderr=self.custom_log)
		self.pid = self.process.pid
		
		# Now do whatever you want...
	
	def wait(self):
		""" Waits the end of the process """
		
		self.process.wait()
		return self.process.returncode # We let the thread starter handle this exit status

def sexec(command, shell=True):
	""" A simple function that will execute a command by invoking execute class. """
	
	# Declare class
	clss = execute(command, shell=shell)
	# Start thread
	clss.start()
	
	# Now we should wait the end...
	status = clss.wait()
	
	if status != 0:
		# An error occoured
		raise CmdError("An error occoured while executing %s" % command)
