# -*- coding: utf-8 -*-
#
# KeepTalking library -- core
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

import subprocess

__version__ = 0.1

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
