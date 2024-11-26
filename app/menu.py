import app.config
import app.util
import app.aarr

import os

class Menu:
	
#-------------------------------------------------------------------
	
	def go(self):
		
		keep_going = True

		while keep_going:
			app.util.clearScreen()
			print(app.util.title())
				
			print("Selecciona un proyecto:")
			self.project_list()
			print ("  N. Nuevo proyecto")
			print ("  0. Salir")
			selection = input("> ")

			if selection == "N" or selection == "n":
				print("NEW")

			elif selection == "0" or selection == 0 or selection == "":
				keep_going = False
				
			elif selection.isnumeric():
				selection = int(selection)
				
				if selection > 0 and selection <= len(self.project_files):
					project = app.aarr.AARR()
					ilist = project.iteration_list(self.project_files[selection-1])
					
					iteration = self.select_iteration(ilist)
					
					if iteration == 0:
						keep_going = False
					if iteration == -1:
						config = self.new_iteration(project)
						project.new_iteration(config)
					else:
						project.project_load(self.project_files[selection-1], iteration)
						project.operate()

				else:
					print("\nOpción incorrecta.")
					input("> ")
				
				
			else:
				print("\nOpción incorrecta.")
				input("> ")

#-------------------------------------------------------------------

	def new_iteration(self, project):

		app.util.clearScreen()
		print(app.util.title())

		print("Se va a crear una nueva iteración para el proyecto.")
		print("Proyecto: " + project.db_proxy("Project_name")) 
		print("Iteración base: " + project.db_proxy("Iteration_last_name") + " (" + project.db_proxy("Iteration_last_id") + ")")
		print()
		
		print("Nuevo nombre:")
		name = input("")
		print("¿Cerrar iteración anterior (Y/N)?")
		prev = input("")
		print("¿Arrastrar elementos inactivos (Y/N)?")
		inactive = input("")

		return {"name":name, "prev":prev, "inactive":inactive}


#-------------------------------------------------------------------

	def select_iteration(self, ilist):
		app.util.clearScreen()
		print(app.util.title())
			
		keep_going = True
		selection = 0

		while keep_going:
			count = 0
			print("Selecciona una iteración del análisis:")

			for i in ilist:
				count+=1
				print("  " + str(count) + ".", i["Name"])
			print ("  N. Nueva iteracion")
			print ("  0. Salir")
			selection = input("> ")
			
			if selection == "N" or selection == "n":
				selection = -1
				keep_going = False

			elif selection == "0" or selection == 0 or selection == "":
				keep_going = False

			elif selection.isnumeric():
				selection = int(selection)
				if selection > 0 and selection <= len(self.project_files):
					keep_going = False
					
		return selection
				

#-------------------------------------------------------------------

	def project_list(self):
		self.project_files_list()
		count = 0

		for x in self.project_files:
			count+=1
			print("  " + str(count) + ". " + x)
		
		
#-------------------------------------------------------------------

	def project_files_list(self):
		
		self.project_files = []
		
		for x in os.listdir('.'):
			if x[-4:] == ".pra":
				self.project_files.append(x)		
		
		
#-------------------------------------------------------------------

		
