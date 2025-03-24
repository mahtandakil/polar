#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------
# Created for: PolarE
# Dev line: PolarE
# Creation day: 03/03/2025
# Last change: 24/03/2025
#---------------------------------------------------------------------------

import app.config
import app.util

from app.lang import lang
lang = lang[app.config.app_lang]

import os


class UIConsole:

#-------------------------------------------------------------------

	def go(self):
		
		keep_going = True
		
		while keep_going:
			app.util.clearScreen()
			print(app.util.title())
			
			print("DEV notes:")
			print("  @ Magerit.creator")
			print("  @ Magerit.__init__")
			print()
				
			print(lang['select_project'] + ":")
#			self.project_list()
			print ("  N. " + lang['new_project'])
			print ("  X. " + lang['exit'])
			selection = input("> ")

			if selection == "N" or selection == "n":
				self.createProject()

			elif selection == "X" or selection == "x":
				keep_going = False
				
#			elif selection.isnumeric():
#				selection = int(selection)
				
#				if selection > 0 and selection <= len(self.project_files):
#					project = app.aarr.AARR()
#					ilist = project.iteration_list(self.project_files[selection-1])
					
#					iteration = self.select_iteration(ilist)
					
#					if iteration == 0:
#						keep_going = False
#					if iteration == -1:
#						config = self.new_iteration(project)
#						project.new_iteration(config)
#					else:
#						project.project_load(self.project_files[selection-1], iteration)
#						project.operate()

#				else:
#					print("\nOpción incorrecta.")
#					input("> ")
				
				
			else:
				print("\n" + lang['wrong_option'])
				input("> ")


#-------------------------------------------------------------------

	def createProject(self):

		keep_going = True
		
		while keep_going:
			app.util.clearScreen()
			print(app.util.title())
			
			count = 0	
			
			print(lang['new_project'] + ":")
			for x in app.config.modules:
				print("  " + str(count+1) + ". " + x['name'])
			print ("  X. " + lang['exit'])
			
			selection = input(">")

			if selection.isnumeric():
				if int(selection) > 0 and int(selection) <= len(app.config.modules):
					module_creation = app.config.modules[int(selection)-1]['module']
					module_creation.creator()
					
				else:
					print("\n" + lang['wrong_option'])
					input("> ")
				
			elif selection == "X" or selection == "x":
				keep_going = False

			else:
				print("\n" + lang['wrong_option'])
				input("> ")	


#-------------------------------------------------------------------

