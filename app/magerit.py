#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------
# Created for: PolarE
# Dev line: PolarE
# Creation day: 24/03/2025
# Last change: 24/03/2025
#---------------------------------------------------------------------------


import app.util


class Magerit:


#-------------------------------------------------------------------

	def __init__(self, app_lang):
		
		self.app_lang = app_lang
		
		self.setLangOnInit()
		self.lang = self.lang[self.app_lang]
		
		self.ra_steps = []
		self.ra_steps.append({'name': "", 'description':"", 'requieres':"", 'optional_requieres':"", 'produces':"", 'optional_produces':""})


#-------------------------------------------------------------------

	def creator(self):

		keep_going = True
			
		while keep_going:
			app.util.clearScreen()
			print(app.util.title())
			print()
			print(self.lang['new_project'] + ":")

		input("> ")

#-------------------------------------------------------------------

	def setLangOnInit(self):
		
		self.lang = {}
		
		self.lang['es'] = {}

		self.lang['es']['new_project'] = "Nuevo proyecto MAGERIT"
		self.lang['es']['set_assets'] = "Establecer activos"
		self.lang['es']['set_risk_catalog'] = "Establecer catálogo de amenazas"
		self.lang['es']['set_asset_links'] = "Establecer relación de activos"
		self.lang['es']['set_asset_x_risk'] = "Establecer cruce de activos y amenazas"
		self.lang['es']['set_controls'] = "Establecer controles"
		self.lang['es']['set_cross_x_control'] = "Vinculas controles a riesgos"
		self.lang['es']['calc_risk'] = "Calcular riesgo"
		self.lang['es']['calc_risk_x_controls'] = "Calcula riesgos en base a controles"


#-------------------------------------------------------------------
