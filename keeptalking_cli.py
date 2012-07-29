#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# KeepTalking -- Command-Line frontend
# Copyright (C) 2012 Semplice Team. All rights reserved.
#
# This file is part of the keeptalking package.
#

from keeptalking import core, Locale, Keyboard, TimeZone
import os, sys
import t9n.library as t9n

_ = t9n.translation_init("keeptalking")

class GUI:
	def header(self, section):
		os.system("clear")
		print "\n" + section
		num = 0
		while num != len(section):
			sys.stdout.write("-")
			num += 1
		print "\n"
	
	def yesno(self):
		
		yn = raw_input(_("Are you sure to continue? [y/n]: ")).lower()
		
		if yn == "y":
			return True
		elif yn == "n":
			return False
		else:
			return self.yesno()
			
	def prompt(self, message, noblank=False, password=False, onlyint=False):
		choice = raw_input(message + ": ")

		if onlyint:
			# We should check if it is an integer
			try:
				choice = int(choice)
			except:
				print "E: %s" % (_("You need to insert a number!"))

		if choice == "" and noblank == False:
			print "E: %s" % (_("You must insert something!"))
			choice = self.prompt(message, password=password)
			return choice
		else:
			return choice

def help():
	""" Displays an help message. """
	
	print(_("keeptalking_cli -- a command-line frontend for keeptalking."))
	print
	print(_("SYNTAX: keeptalking_cli <options> <scene>"))
	print
	print(_("Available scenes:"))
	print(_("   locale                    - Locale scene"))
	print(_("   keyboard                  - Keyboard scene"))
	print(_("   timezone                  - Timezone scene"))
	print(_("   all                       - All scenes"))
	print
	print(_("Available options:"))
	print(_("   --version|-v              - Prints version, then exits."))
	print(_("   --help|-h                 - Prints this message, then exits."))
	print(_("   --default|-d              - Returns the default item for the scene."))
	print(_("   --set|-s (= item)         - Sets the default item for the scene."))
	print(_("   --supported|-u            - Returns the supported items for the scene."))
	print
	print(_("Extra options for locale scene:"))
	print(_("   --codepages|-c            - Returns the codepages supported for every locale."))
	print(_("   --human|-m                - Returns the locales in an human form."))
	print
	print(_("Extra options for keyboard scene:"))
	print(_("   --variants|-a (= layout)  - Returns the supported variants for the layout."))
	print

def locale():
	""" Displays the locale scene. """
	
	cls = Locale.Locale()
	
	if print_default:
		print cls.default
		return
	elif print_supported:
		print cls.supported
		return
	elif print_codepages:
		print cls.codepages
		return
	elif print_human:
		for locale, key in cls.human_form().items(): print "%s\t%s" % (key, locale)
		return
	
	gui.header(_("Select locale"))

	print _("""You should now select your locale.
You can insert your full locale (for example it_IT.UTF-8) or let
this application guess it for you by entering only your locale
code (ex: it).

To get a list of supported locales, you can open this application
with the -u switch.

Current locale is %s.""" % (cls.default)) + "\n"

	if set_default:
		# Specified language to set via commandline...
		choice = set_default
	else:
		# We need to ask for language.
		choice = gui.prompt(_("Please insert the locale you want"))
	
	choice = cls.get_best_locale(choice) # Get best locale
	if not choice:
		# No best locale found :( Exit
		raise core.UserError(_("No locale discovered using the selected pattern. See supported locales using the -u switch."))
	
	print
	if not set_default:
		result = gui.yesno()
	else:
		result = True
	if result:
		# Let's do things for real
		cls.set(choice)

def keyboard():
	""" Displays the keyboard scene. """
	
	cls = Keyboard.Keyboard()
	
	if print_default:
		print cls.default
		return
	elif print_supported:
		print cls.supported()
		return
	elif print_variants:
		print cls.supported_variants(print_variants)
		return
	
	gui.header(_("Select keyboard layout"))

	print "\n" + _("""Here you can select the keyboard layout.

It is possible to specify layout, model and variant,
in that order.
Colons are used to separate the sections. Then:

  it:pc105:

will set it as layout, pc105 as model and nothing as variant.
If something is not specified, it will be leaved as-is currently
in /etc/default/keyboard.

NOTE: If you are attempting to change the variant, you need to
specify the layout.

To get a list of supported layouts, you can open this application
with the -u switch.

Current keyboard layout is %s.""" % cls.default) + "\n"

	if set_default:
		# Specified language to set via commandline...
		choice = set_default
	else:
		# We need to ask for language.
		choice = gui.prompt(_("Please insert the keyboard layout you want"))
	
	choice = choice.split(":")
	
	if len(choice) == 1:
		# No model and variant
		lay = choice[0]
		model = None
		variant = None
	elif len(choice) == 2:
		# only model
		lay = choice[0]
		model = choice[1]
		variant = None
		
		if model == "": model = None
	else:
		# model and variant
		lay = choice[0]
		model = choice[1]
		variant = choice[2]
		
		if model == "": model = None
		if variant == "": variant = None
	
	if variant == "basic": variant = ""
	
	# See if layout is supported
	if lay:
		supp = cls.is_supported(lay)
		if not supp:
			# Is not supported :( Exit
			raise core.UserError(_("The selected layout is not supported. See supported layouts using the -u switch."))
	
	# See if variant (if any) is supported
	if variant:
		if variant not in cls.supported_variants(lay):
			# Is not supported :( Exit
			raise core.UserError(_("The selected variant is not supported. See supported variants for the given layout with the -a=layout switch."))
	
	print
	if not set_default:
		result = gui.yesno()
	else:
		result = True
	if result:
		# Let's do things for real
		cls.set(layout=lay, model=model, variant=variant)

def timezone_loop():
	""" Displays an interactive list to select the proper timezone. """
	
	cls = TimeZone.TimeZone()
	
	lst = {}
	num = 0
	for zone in cls.supported:
		num += 1
		print " %s) %s" % (num, zone)
		
		# Add to lst
		lst[num] = zone
	
	# Add specify and exit
	num += 1
	print " %s) %s" % (num, _("Specify"))
	lst[num] = "_specify"
	
	num += 1
	print " %s) %s" % (num, _("Exit"))
	lst[num] = "_exit"
	
	print
	
	# Prompt
	choice = gui.prompt(_("Please insert your choice"), onlyint=True)
	if not choice in lst:
		# Wrong!
		print "E: %s" % _("Wrong choice!")
		return timezone_loop()
	
	### Build cities list
	zone = lst[choice]
	
	if zone == "_exit":
		return "_exit"
	elif zone == "_specify":
		choice = gui.prompt(_("Please specify the timezone")).split("/")
		if len(choice) == 1:
			# We assume is only the zone.
			if choice[0] in cls.supported:
				zone = choice[0]
			else:
				print "E: %s" % _("Invalid zone!")
				return timezone_loop()
		else:
			# Both zone and city
			if choice[0] in cls.supported and choice[1] in cls.supported[choice[0]]:				
				# ok!
				return "%s/%s" % (choice[0], choice[1])
			else:
				# :/
				print "E: %s" % _("Invalid zone or city!")
				return timezone_loop()
				
	
	lst = {}
	num = 0
	for city in cls.supported[zone]:
		num += 1
		print " %s) %s" % (num, city)
		
		# Add to lst
		lst[num] = city

	# Add specify and exit
	num += 1
	print " %s) %s" % (num, _("Specify"))
	lst[num] = "_specify"
	
	num += 1
	print " %s) %s" % (num, _("Exit"))
	lst[num] = "_exit"
	
	print

	# Prompt
	choice = gui.prompt(_("Please insert your choice"), onlyint=True)
	if not choice in lst:
		# Wrong!
		print "E: %s" % _("Wrong choice!")
		return timezone_loop()
	
	### Get city
	city = lst[choice]
	
	if city == "_exit":
		return "_exit"
	elif city == "_specify":
		choice = gui.prompt(_("Please specify the city"))
		if choice in cls.supported[zone]:
			city = choice
		else:
			print "E: %s" % _("Invalid city!")
			return timezone_loop()
	
	return "%s/%s" % (zone, city)
	

def timezone():
	""" Displays the timezone scene. """
	
	cls = TimeZone.TimeZone()
	
	if print_default:
		print cls.default
		return
	elif print_supported:
		print cls.supported
		return

	gui.header(_("Select Timezone"))
	
	print "\n" + _("""Here you can select your Timezone.

Current is %s.

Select one from the list:
""") % cls.default
	
	if set_default:
		choice = set_default
	else:
		# We should loop through all supported timezones
		choice = timezone_loop()
		if choice == "_exit":
			return

	print
	if not set_default:
		result = gui.yesno()
	else:
		result = True
	if result:
		# Let's do things for real
		cls.set(choice)

		
def tutte_insieme():
	""" Runs all scenes. """
	
	locale()
	keyboard()
	timezone()
	

gui = GUI() # Initialize interface

scene = "all"
print_default = False
set_default = None
print_supported = False

print_variants = False
print_codepages = False
print_human = False

# Parse arguments
for arg in sys.argv[1:]:
	if arg in ("locale", "keyboard", "timezone", "all"):
		scene = arg
	elif arg in ("--version", "-v"):
		print core.__version__
		sys.exit(0)
	elif arg in ("--help", "-h"):
		help()
		sys.exit(0)
	elif arg in ("--default", "-d"):
		print_default = True
	elif arg.split("=")[0] in ("--set", "-s"):
		set_default = arg.split("=")[1]
	elif arg in ("--supported", "-u"):
		print_supported = True
	elif arg.split("=")[0] in ("--variants", "-a"):
		print_variants = arg.split("=")[1]
	elif arg in ("--codepages", "-c"):
		print_codepages = True
	elif arg in ("--human","-m"):
		print_human = True
	else:
		print(_("Invalid argument: %s") % arg)
		help()
		sys.exit(1)
	

scenes = {"locale":locale, "keyboard":keyboard, "timezone":timezone, "all":tutte_insieme}

sys.exit(scenes[scene]())
