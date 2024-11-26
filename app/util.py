#!/usr/bin/python
# -*- coding: utf-8 -*-


#---------------------------------------------------------------------------
# Created for: usync project
# Dev line: PolarE 1.0
# Creation day: 11/03/2012
# Last change: 25/08/2023
#---------------------------------------------------------------------------

import app.config

import os
from datetime import datetime


dev_messages = ""
dev_messages += "\n"
dev_messages += "BUG: +1 en listado de riesgos\n"
dev_messages += "BUG: negativos en RA\n"
dev_messages += "BUG: descuadre en cabecera de titulo de fichero\n"
dev_messages += "FEATURE: indicar en informe los NE asociados a cada activo y otras tareas pendientes de la iteración\n"
dev_messages += "FEATURE: aplicabilidad en autocomentarios\n"
dev_messages += "FEATURE: Informe >> tablas de agrupación por activo en R2 y R3\n"
dev_messages += "FEATURE: Informe >> tablas interactuables\n"
dev_messages += "FEATURE: Informe >> ID de iteración en nombre y contenido\n"
dev_messages += "FEATURE: autocomentarios completos en r2 y r3\n"
dev_messages += "FEATURE: orden en tabla de conteo de amenazas\n"
dev_messages += "FEATURE: eliminar updates antiguos en db.py\n"
dev_messages += "FEATURE: letrero de proyecto/iteracción en curso\n"
dev_messages += "FEATURE: Salir\n"
dev_messages += "OPTIMIZATION: código muerto\n"
dev_messages += "OPTIMIZATION: suprimir update_risk3_values_by_dependences\n"


#---------------------------------------------------------------------------

def clearScreen():
	
	if os.name == "posix":
		os.system("clear")
		
	elif os.name == "nt":
		os.system("cls")


#---------------------------------------------------------------------------

def title(project="", iteration=""):
	
	clearScreen()
	
	output = ""
	spaces = ""
		
	title = "POLAR " + app.config.app_version
	fix = len(title)
		
	output += "+----------------------"
	for z in range(0,fix):
		output += "-"
	output += "+\n"
	limiter = output

	fix = len(output)-len(title)-2
	output += "|"
	for z in range(0,int(fix/2)):
		output += " "
	output += title
	for z in range(0,int(fix/2)):
		output += " "
	output += "|\n"

	output += limiter
	
	if not project=="":
		reference = "| " + project
		for z in range(len(reference),int(fix)):
			reference += " "
		output += reference + "|\n"

	output += "\n" + dev_messages


	return output
		
	
#-------------------------------------------------------------------


def today():

	t = datetime.today().strftime('%Y-%m-%d')
	
	return t
	
	
#---------------------------------------------------------------------------
