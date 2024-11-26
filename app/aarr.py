import app.config
import app.util
import app.db
import app.report

import os
from datetime import datetime

class AARR:


#-------------------------------------------------------------------

	def __init__(self):
		
		self.today = app.util.today()


#-------------------------------------------------------------------

	def iteration_list(self, path):

		app.util.clearScreen()

		self.project_path = os.path.abspath(os.path.join(".", path))
		self.db = app.db.DB(self.project_path)

		self.project_path = os.path.abspath(os.path.join(".", path))
		self.db = app.db.DB(self.project_path)
		
		self.db.DBQUERY_table_set('Iteration')
		self.db.DBQUERY_order_set('ORDER BY Id ASC')
		export = self.db.DBQUERY_query()
		
		return export
			

#-------------------------------------------------------------------

	def new_iteration(self, options):

		keep = False
		if options["inactive"] == "Y" or options["inactive"] == "y":
			keep = True

		print ("Creando nueva iteración...")
		print ("  + Creando nuevos registros")
		
		self.db.DBQUERY_table_set('Iteration')
		self.db.DBQUERY_order_set('ORDER BY Id DESC')
		last_iter = self.db.DBQUERY_query()[0]

		data_model = self.db.TRANSLATION_data_model["Iteration"].copy()
		data_model["Name"] = options["name"]
		data_model["Start"] = self.today
		self.db.TABLE_insert("Iteration", data_model)

		self.db.DBQUERY_table_set('Iteration')
		self.db.DBQUERY_order_set('ORDER BY Id DESC')
		new_iter = self.db.DBQUERY_query()[0]

		if options["prev"] == "Y" or options["prev"] == "y":
			last_iter["End"] = self.today
			self.db.TABLE_update("Iteration", last_iter)
		
		self.db.DBQUERY_table_set('Assets')
		self.db.DBQUERY_filter_set('Iteration = ' + str(last_iter["Id"]))
		if not keep:
			self.db.DBQUERY_filter_set('Active = 1')
		assets = self.db.DBQUERY_query()
		for a in assets:
			a["Iteration"] = new_iter["Id"]
			self.db.TABLE_insert("Assets", a)

		self.db.DBQUERY_table_set('RiskCatalog')
		self.db.DBQUERY_filter_set('Iteration = ' + str(last_iter["Id"]))
		if not keep:
			self.db.DBQUERY_filter_set('Active = 1')
		risks = self.db.DBQUERY_query()
		for r in risks:
			r["Iteration"] = new_iter["Id"]	
			self.db.TABLE_insert("RiskCatalog", r)

		self.db.DBQUERY_table_set('SecurityControls')
		self.db.DBQUERY_filter_set('Iteration = ' + str(last_iter["Id"]))
		if not keep:
			self.db.DBQUERY_filter_set('Active = 1')
		security_controls = self.db.DBQUERY_query()
		for sc in security_controls:
			sc["Previous"] = sc["Id"]
			sc["Iteration"] = new_iter["Id"]
			self.db.TABLE_insert("SecurityControls", sc)
			
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(last_iter["Id"]))
		if not keep:
			self.db.DBQUERY_filter_set('Active = 1')
		applicability = self.db.DBQUERY_query()
		for ap in applicability:
			ap["Iteration"] = new_iter["Id"]		
			self.db.TABLE_insert("Applicability", ap)

		print ("  + Creando nuevos cálculos R1")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(last_iter["Id"]))
		self.db.DBQUERY_filter_set("(Applicability = 'Y' OR Applicability = 'AY')")
		if not keep:
			self.db.DBQUERY_filter_set('Active = 1')
		applicability = self.db.DBQUERY_query()
		for ap in applicability:
			
			last_ap = ap
			
			self.db.DBQUERY_table_set('Applicability')
			self.db.DBQUERY_filter_set('Iteration = ' + str(new_iter["Id"]))
			self.db.DBQUERY_filter_set('AssetId = ' + str(last_ap["AssetId"]))
			self.db.DBQUERY_filter_set('RiskId = ' + str(last_ap["RiskId"]))
			new_ap = self.db.DBQUERY_query()[0]

			self.db.DBQUERY_table_set('Risk1')
			self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(last_ap["Id"]))
			last_r1 = self.db.DBQUERY_query()[0]

			last_r1["ApplicabilityId"] = new_ap["Id"]
			last_r1["Iteration"] = new_iter["Id"]			
			self.db.TABLE_insert("Risk1", last_r1)		

		print ("  + Actualizando referencias de aplicabilidad")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(new_iter["Id"]))
		if not keep:
			self.db.DBQUERY_filter_set('Active = 1')
		applicability = self.db.DBQUERY_query()
		for ap in applicability:	
				
			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set('Id = ' + str(ap["AssetId"]))
			asset = self.db.DBQUERY_query()[0]		
			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set("InternalId = '" + str(asset["InternalId"]) + "'")	
			self.db.DBQUERY_filter_set("Iteration = " + str(new_iter["Id"]))
			asset = self.db.DBQUERY_query()[0]

			self.db.DBQUERY_table_set('RiskCatalog')
			self.db.DBQUERY_filter_set('Id = ' + str(ap["RiskId"]))	
			risk = self.db.DBQUERY_query()[0]		
			self.db.DBQUERY_table_set('RiskCatalog')
			self.db.DBQUERY_filter_set("InternalId = '" + str(risk["InternalId"]) + "'")
			self.db.DBQUERY_filter_set("Iteration = " + str(new_iter["Id"]))
			risk = self.db.DBQUERY_query()[0]
		
			ap["AssetId"] = asset["Id"]
			ap["RiskId"] = risk["Id"]
			self.db.TABLE_update("Applicability", ap)

		print ("  + Actualizando referencias de controles")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set("Iteration = " + str(new_iter["Id"]))
		controls = self.db.DBQUERY_query()
			
		for a in controls:
								
			if not (a["SecurityControlsId"] == None or a["SecurityControlsId"] == "None" or a["SecurityControlsId"] == "Null" or a["SecurityControlsId"] == ""):
				new_controls = ""
				control_ids = a["SecurityControlsId"].split(",")

				for x in control_ids:
					self.db.DBQUERY_table_set('SecurityControls')
					self.db.DBQUERY_filter_set('Previous = ' + str(x))	
					self.db.DBQUERY_filter_set('Iteration = ' + str(new_iter["Id"]))
					control = self.db.DBQUERY_query()[0]
					new_controls += str(control["Id"]) + ","
				
				new_controls = new_controls[:-1]
				a["SecurityControlsId"] = new_controls
				self.db.TABLE_update("Applicability", a)

		print ("  + Actualizando referencias de dependencias")
		self.db.DBQUERY_table_set('Assets')
		self.db.DBQUERY_filter_set("Iteration = " + str(new_iter["Id"]))
		assets = self.db.DBQUERY_query()		

		for a in assets:
			if not (a["Dependences"] == None or a["Dependences"] == "None" or a["Dependences"] == "Null" or a["Dependences"] == ""):
				new_dependences = ""
				dependences_ids = a["Dependences"].split(",")
				
				for x in dependences_ids:
					self.db.DBQUERY_table_set('Assets')
					self.db.DBQUERY_filter_set("Id = " + str(x))
					previous_asset = self.db.DBQUERY_query()[0]
					self.db.DBQUERY_table_set('Assets')
					self.db.DBQUERY_filter_set("InternalId = '" + str(previous_asset["InternalId"] + "'"))
					self.db.DBQUERY_filter_set("Iteration = " + str(new_iter["Id"]))
					new_asset = self.db.DBQUERY_query()[0]				
			
					new_dependences += str(new_asset["Id"]) + ","
				
				new_dependences = new_dependences[:-1]
				a["Dependences"] = new_dependences
				self.db.TABLE_update("Assets", a)
			
		self.db.DB_COMMIT()
		input(">")

#-------------------------------------------------------------------

	def db_proxy(self, query):

		export = ""

		if query == "Project_name":
			self.db.DBQUERY_clean()
			self.db.DBQUERY_table_set('Common')
			self.db.DBQUERY_filter_set('Register = \'title\'')
			export = self.db.DBQUERY_query()[0]['Value']

		elif query == "Iteration_last_name":
			self.db.DBQUERY_clean()
			self.db.DBQUERY_table_set('Iteration')
			self.db.DBQUERY_order_set("ORDER BY Id DESC")
			export = self.db.DBQUERY_query()[0]['Name']
		
		elif query == "Iteration_last_id":
			self.db.DBQUERY_clean()
			self.db.DBQUERY_table_set('Iteration')
			self.db.DBQUERY_order_set("ORDER BY Id DESC")
			export = str(self.db.DBQUERY_query()[0]['Id'])
		
		return export

#-------------------------------------------------------------------

	def project_load(self, path, iteration):

		self.iteration = iteration
		self.dims = []
		self.project_config = {}

		app.util.clearScreen()
		self.project_path = os.path.abspath(os.path.join(".", path))
		self.db = app.db.DB(self.project_path)
		
		self.db_export = app.db.DB(self.project_path)
		
		self.db.DBQUERY_clean()
		self.db.DBQUERY_table_set('Common')
		self.db.DBQUERY_filter_set('Register = \'title\'')
		export = self.db.DBQUERY_query()
		self.title = export[0]['Value']

		self.db.DBQUERY_clean()
		self.db.DBQUERY_table_set('Common')
		self.db.DBQUERY_filter_set('Register = \'dims\'')
		export = self.db.DBQUERY_query()
		ldims = int(export[0]['Value'])
		for l in range(1,ldims+1):
			dim = {}
			self.db.DBQUERY_clean()
			self.db.DBQUERY_table_set('Common')
			self.db.DBQUERY_filter_set('Register = \'d' + str(l) + '_short\'')
			export = self.db.DBQUERY_query()
			dim['short'] = export[0]['Value']
			self.db.DBQUERY_clean()
			self.db.DBQUERY_table_set('Common')
			self.db.DBQUERY_filter_set('Register = \'d' + str(l) + '_name\'')
			export = self.db.DBQUERY_query()
			dim['name'] = export[0]['Value']
			self.dims.append(dim)
		
		self.db.DBQUERY_clean()
		self.db.DBQUERY_table_set('Common')
		export = self.db.DBQUERY_query()
		for e in export:
			self.project_config[e["Register"]] = e["Value"]
			
		self.ldims = len(self.dims)


#-------------------------------------------------------------------

	def set_autocomms(self):
		
		print("- Actualizar textos de apoyo")

		print("  + Aplicabilidad")	

		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		applicability = self.db.DBQUERY_query()

		for ap in applicability:

			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set('Id = ' + str(ap["AssetId"]))
			asset = self.db.DBQUERY_query()[0]
			
			self.db.DBQUERY_table_set('RiskCatalog')
			self.db.DBQUERY_filter_set('Id = ' + str(ap["RiskId"]))
			risk = self.db.DBQUERY_query()[0]
			
			comm = asset["InternalId"] + ". " + asset["Name"] + " x " + risk["InternalId"] + ". " + risk["Name"]
			
			ap["AutoComm"] = comm
			self.db.TABLE_update("Applicability", ap)

			if (ap["Applicability"] == "Y" or ap["Applicability"] == "AY"):
			
				self.db.DBQUERY_table_set('Risk1')
				self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap["Id"]))
				self.db.DBQUERY_filter_set('Active = 1')
				r1 = self.db.DBQUERY_query()
			
				if len(r1) > 0:
					
					r1 = r1[0]			
					r1["AutoComm"] = comm
					self.db.TABLE_update("Risk1", r1)
		
		self.db.DB_COMMIT()


#-------------------------------------------------------------------

	def operate(self):

		keep = True
		while keep:

			error = False

			print(app.util.title(self.title))

			print()
			print("1. Proceso completo")
			print("2. Actualizar aplicabilidad")
			print("3. Cálculo de R1")
			print("4. Cálculo de R2")
			print("5. Cálculo de R3")
			print("6. Actualizar textos de apoyo")
			print("7. Informe")
#			print("?9. Refrescar RR y RA")
			selection = input("> ")
			
			if selection == "1":
				self.calculate()

			elif selection == "2":
				self.expanse_applicability()

			elif selection == "3":
				self.calculate_R1()

			elif selection == "4":
				self.calculate_R2()

			elif selection == "5":
				self.calculate_R3()

			elif selection == "6":
				self.set_autocomms()


			elif selection == "7":
				self.report_general()

			elif selection == "999":
				self.clean_r2_r3()
			
			else:
				error = True
				
			if error:
				print("\nOpción incorrecta.")
			else:
				print("\nFinalizado")
			input("> ")
			

#-------------------------------------------------------------------

	def report_general(self):
		
		print("- Generando informes")
		r = app.report.Report()

		print("  + Informe general")
		r.report1(self.db, self.iteration, self.project_config)
		

#-------------------------------------------------------------------

	def calculate(self):

		print(app.util.title(self.title))

		self.clean_r2_r3()
		self.expanse_applicability()
		self.calculate_R1()
		self.calculate_R2()
		self.calculate_R3()
		self.set_autocomms()
		self.report_general()
		


#-------------------------------------------------------------------

	def calculate_R3(self):

		print("- Calculando R3")

		print("  + Trasladando valores de R2")
		self.db.DBQUERY_table_set('Risk2')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		r2 = self.db.DBQUERY_query()
		
		for r in r2:
			
			self.db.DBQUERY_table_set('Risk3')
			self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(r['ApplicabilityId']))
			r3 = self.db.DBQUERY_query()[0]
			
			r["Id"] = r3["Id"]
			
			self.db.TABLE_update("Risk3", r)
		
		self.db.DB_COMMIT()
		
		print("  + Creando el arbol de dependencias")

		dtree = []
		self.db.DBQUERY_table_set('Assets')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		assets = self.db.DBQUERY_query()

		for a in assets:
			entry = {"asset_id":None, "deps":[]}
			entry["asset_id"] = a["Id"]
			entry["deps"] = []
			dtree.append(entry)
		
		
		assets = self.db.DBQUERY_query()
		for a in assets:
			for s in str(a["Dependences"]).split(","):
				if not (s == None or s == "None" or s == 0):
					for dt in dtree:

						if int(dt["asset_id"]) == int(s):
							dt["deps"].append(int(a["Id"]))

		print("  + Repercutiendo valores")
		
		dep_index = ["P"]
		for x in range(1, self.ldims+1):
			dep_index.append("D"+str(x))
				
		self.db.DBQUERY_table_set('Assets')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		sending_assets = self.db.DBQUERY_query()
			
		sas_to_check = []
		for sa in sending_assets:
			sas_to_check.append(sa)

		dcount = 0
		while len(sas_to_check) > 0:
			dcount += 1
			
			sa = sas_to_check.pop(0)
			dep = None
			print("    +", str(dcount)+".", sa["Id"], "-", sa["InternalId"])
			
			for d in dtree:
				if d["asset_id"] == sa["Id"]:
					dep = d["deps"]
		
			self.db.DBQUERY_table_set('Applicability')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('AssetId = ' + str(sa["Id"]))
			self.db.DBQUERY_filter_set('Active = 1')
			sa_r3 = self.db.DBQUERY_query()
			
			for d in dep:

				self.db.DBQUERY_table_set('Assets')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + str(d))
				original_asset = self.db.DBQUERY_query()[0]
				
				asset_changed = False
				
				for sar3 in sa_r3:
					cross_changed = False
					
					self.db.DBQUERY_table_set('Applicability')
					self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
					self.db.DBQUERY_filter_set('AssetId = ' + str(original_asset["Id"]))
					self.db.DBQUERY_filter_set('RiskId = ' + str(sar3["RiskId"]))
					cross_r3 = self.db.DBQUERY_query()[0]
					
					self.db.DBQUERY_table_set('Risk3')
					self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(sar3["Id"]))
					r3sa = self.db.DBQUERY_query()[0]					

					self.db.DBQUERY_table_set('Risk3')
					self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(cross_r3["Id"]))
					r3oa = self.db.DBQUERY_query()
						
					if len(r3oa)==0:
						
						r3oa = r3sa
						r3oa["ApplicabilityId"] = cross_r3["Id"]
						r3oa["AutoComm"] = ""
						r3oa["Updated"] = self.today
						self.db.TABLE_insert("Risk3", r3oa)
						cross_changed = True
						asset_changed = True						
					
					else:
					
						r3oa = r3oa[0]
												
						for i in dep_index:
							if r3sa[i] > r3oa[i] and r3sa[i] > 0:
								r3oa[i] = r3sa[i]
								cross_changed = True
								asset_changed = True
						
						if cross_changed:
							r3oa["Active"] = 1
							self.db.TABLE_update("Risk3", r3oa)

							#print(r3sa)
							#print(r3oa)
							#print(dep_index)
							#print()
							#input(">")
					
				if asset_changed:
					to_review = False
					for x in sas_to_check:
						if x["Id"] == original_asset["Id"]:
							to_review = True
					if not to_review:
						sas_to_check.append(original_asset)
					
					
								
		#	for oa in original_assets:
		#		oa_count += 1
		#		print("        @ OA" + str(oa_count) + ":", str(oa["Id"]), str(oa["Name"]), end="")
		#		print()
		#		dependences = self.get_dependences_by_assetid(oa)
		#		asset_change = self.update_risk3_values_by_dependences(oa, dependences, nchanges, changed_list)
		#		if asset_change:
		#			changes = True
		#			print("          ==> Cambios")
		#			new_changed_list.append(oa["Id"])
							
		#	nchanges += 1
		
		self.db.DB_COMMIT()

		print("  + Cálculo de R3")

		self.db.DBQUERY_table_set('Risk3')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		r3_registers = self.db.DBQUERY_query()
			
		for r3 in r3_registers:
				
			self.db.DBQUERY_table_set('Applicability')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(r3['ApplicabilityId']))
			ap = self.db.DBQUERY_query()[0]

			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(ap['AssetId']))
			ass = self.db.DBQUERY_query()[0]
			asset_value = ass['Value']
				
			for x in range(1,11):
					
				r_index = "R" + str(x)
				d_index = "D" + str(x)
				
				if r3['P'] > 0 and r3[d_index] > 0:
					r3[r_index] = str(float(asset_value) * float(r3['P']) * float(r3[d_index]))
				else:
					r3[r_index] = -9
					
			r3['Updated'] = app.util.today()

			self.db.risk3_update(r3)
			self.db.TABLE_update("Risk3", r3)

		self.db.DB_COMMIT()


#-------------------------------------------------------------------

	def calculate_R1(self):

		print("- Calculando R1")

		print("  + Identificando registros listos para procesar")
		self.db.DBQUERY_table_set('Risk1')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('P > 0')
		self.db.DBQUERY_filter_set('Active = 1')
		r1 = self.db.DBQUERY_query()

		print("  + Cálculo de R1")
		for r in r1:
			
			changes = False
			
			for index in range(1,11):
				r["R"+str(index)] = -9
			
			self.db.DBQUERY_table_set('Applicability')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(r['ApplicabilityId']))
			ap = self.db.DBQUERY_query()[0]
			probability = r['P']

			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(ap['AssetId']))
			ass = self.db.DBQUERY_query()[0]			
			asset_value = float(ass['Value'])

			for x in range(1,len(self.dims)+1):
				index = "D" + str(x)
				impact = float(r[index])
				
				if impact > 0:
					changes = True
					risk_value = asset_value * probability * impact
					index = "R" + str(x)
					r[index] = risk_value
					
			if changes:
				r['Updated'] = app.util.today()
				self.db.risk1_update(r)
		
		self.db.DB_COMMIT()

		#%%%%				
		#print("- Calculo del riesgo inherente")
		#self.db.DBQUERY_table_set('Risk1')
		#self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		#self.db.DBQUERY_filter_set('P > 0')
		#r1 = self.db.DBQUERY_query()
		
		#for r in r1:
		#	changes = False
			
		#	self.db.DBQUERY_table_set('Applicability')
		#	self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		#	self.db.DBQUERY_filter_set('Id = ' + str(r['ApplicabilityId']))
		#	ap = self.db.DBQUERY_query()[0]
		#	probability = r['P']

		#	self.db.DBQUERY_table_set('Assets')
		#	self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		#	self.db.DBQUERY_filter_set('Id = ' + str(ap['AssetId']))
#			ass = self.db.DBQUERY_query()[0]			
#			asset_value = float(ass['Value'])

#			for x in range(1,11):
#				index = "D" + str(x)
#				impact = float(r[index])
				
#				if impact > 0:
#					changes = True
#					risk_value = asset_value * probability * impact
#					index = "R" + str(x)
#					r[index] = risk_value
					
#			if changes:
#				r['Updated'] = datetime.today().strftime('%Y-%m-%d')
#				self.db.risk1_update(r)

#-------------------------------------------------------------------

	def calculate_R2(self):

		print("- Calculando R2")
		self.db.DBQUERY_table_set('Risk2')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		r2_registers = self.db.DBQUERY_query()
		
		master_sc_factors = []
		for x in range(0,len(self.dims)+1):
			master_sc_factors.append(1.0)

		for r2 in r2_registers:
				
			sc_factors = master_sc_factors.copy()
			self.db.DBQUERY_table_set('Risk1')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(r2['ApplicabilityId']))					
			r1 = self.db.DBQUERY_query()[0]
			
			self.db.DBQUERY_table_set('Applicability')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(r2['ApplicabilityId']))					
			ap = self.db.DBQUERY_query()[0]

			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(ap['AssetId']))					
			asset = self.db.DBQUERY_query()[0]		
		
			scid = []
			try:
				if len(ap["SecurityControlsId"]) > 0 and not ap["SecurityControlsId"] == None and not ap["SecurityControlsId"] == "None":
					scid = ap["SecurityControlsId"].split(',')
			except:
				scid = []		
		
			for sc in scid:
				self.db.DBQUERY_table_set('SecurityControls')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + str(sc))					
				c = self.db.DBQUERY_query()[0]
				
				cfactors = [c["P"]]
				for x in range(1,len(self.dims)+1):
					cfactors.append(c["D"+str(x)])
					
					
				for x in range(0, self.ldims+1):
					if cfactors[x] == None:
						cfactors[x] = 0
					cfactors[x] = 1 - (cfactors[x]/100)
					sc_factors[x] = sc_factors[x] * cfactors[x]

			for x in range(0, self.ldims+1):
				if x == 0:
					index = "P"
				else:
					index = "D" + str(x)
				
				if r1[index] < 0:
					r2[index] = r1[index]
				else:
					r2[index] = round(float(r1[index]) * float(sc_factors[x]), 2)

			for x in range(1, self.ldims+1):
				index = "D" + str(x)
				inder = "R" + str(x)

				if r2["P"] < 0 or r2[index] < 0:
					r2[inder] = -9.0
				else:
					r2[inder] = round(float(asset["Value"]) * r2["P"] * r2[index], 2)
			
			r2['Updated'] = self.today
			r2['AutoComm'] = ap['AutoComm']
			self.db.TABLE_update("Risk2", r2)

		self.db.DB_COMMIT()
	
		
#		self.db.DBQUERY_table_set('Risk2')
#		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
#		r2_registers = self.db.DBQUERY_query()
		
#		for r2 in r2_registers:
			
#			sc_factors = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
			
#			self.db.DBQUERY_table_set('Risk1')
#			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
	#		self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(r2['ApplicabilityId']))					
#			r1 = self.db.DBQUERY_query()[0]

#			self.db.DBQUERY_table_set('Applicability')
#			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
#			self.db.DBQUERY_filter_set('Id = ' + str(r2['ApplicabilityId']))					
#			ap = self.db.DBQUERY_query()[0]

#			self.db.DBQUERY_table_set('Assets')
#			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
#			self.db.DBQUERY_filter_set('Id = ' + str(ap['AssetId']))					
#			asset = self.db.DBQUERY_query()[0]
			
#			scid = []
#			try:
#				if len(ap["SecurityControlsId"]) > 0 and not ap["SecurityControlsId"] == None and not ap["SecurityControlsId"] == "None":
#					scid = ap["SecurityControlsId"].split(',')
#			except:
#				scid = []
			
#			for sc in scid:
#				self.db.DBQUERY_table_set('SecurityControls')
##				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
#				self.db.DBQUERY_filter_set('Id = ' + str(sc))					
#				c = self.db.DBQUERY_query()[0]
				
#				cfactors = [c["P"], c["D1"], c["D2"], c["D3"], c["D4"], c["D5"]]
				
#				for x in range(0, 6):
#					if cfactors[x] == None:
#						cfactors[x] = 0
#					cfactors[x] = 1 - (cfactors[x]/100)
#					sc_factors[x] = sc_factors[x] * cfactors[x]

#			for x in range(0, 6):
#				if x == 0:
#					index = "P"
#				else:
#					index = "D" + str(x)
				
#				if r1[index] < 0:
#					r2[index] = r1[index]
#				else:
#					r2[index] = round(float(r1[index]) * float(sc_factors[x]), 2)
					
#			for x in range(1, 6):
#				index = "D" + str(x)
#				inder = "R" + str(x)
#
#				if r2["P"] < 0 or r2[index] < 0:
#					r2[inder] = -9.0
#				else:
#					r2[inder] = round(float(asset["Value"]) * r2["P"] * r2[index], 2)
			
#			r2['Updated'] = app.util.today()
#			r2['AutoComm'] = ap['AutoComm']
#			self.db.risk2_update(r2)			
			
			
#-------------------------------------------------------------------

	def calculate_OLD(self):
		
		#%%%%				
		print("- Actualizando textos de apoyo")
		print("  + Aplicabilidad")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		applicability_registers = self.db.DBQUERY_query()
		for ar in applicability_registers:
			
			scid = []
			laid = []
			autoc = ""
			
			try:
				if len(ar["SecurityControlsId"]) > 0 and not ar["SecurityControlsId"] == None and not ar["SecurityControlsId"] == "None":
					scid = ar["SecurityControlsId"].split(',')
			except:
				scid = []

			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(ar['AssetId']))
			ass = self.db.DBQUERY_query()[0]
			autoc = ass['InternalId'] + " x "			

			try:
				if len(ass["Dependences"]) > 0 and not ass["Dependences"] == None and not ass["Dependences"] == "None":
					laid = ass["Dependences"].split(',')
			except:
				laid = []
			
			self.db.DBQUERY_table_set('RiskCatalog')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(ar['RiskId']))
			rc = self.db.DBQUERY_query()[0]
			autoc += rc['InternalId'] + " " + rc['Name'] + "\n"
			
			autoc += "Security Controls:\n"
			for s in scid:
				self.db.DBQUERY_table_set('SecurityControls')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + s)
				rc = self.db.DBQUERY_query()[0]
				autoc += " - [" + str(rc['Id']) + "] " + rc['Name'] + "\n"				
			
			autoc += "Linked assets:\n"
			for l in laid:
				self.db.DBQUERY_table_set('Assets')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + l)
				rc = self.db.DBQUERY_query()[0]
				autoc += " - [" + str(rc['Id']) + "][" + rc['InternalId'] +"] " + rc['Name'] + "\n"				

			autoc = autoc[:-1]
			
			if not autoc == ar["AutoComm"]:
				ar["AutoComm"] = autoc
				ar["Updated"] = app.util.today()
				self.db.applicability_update(ar)
				
		print("  + Riesgo inherente")
		dbri = app.db.DB(self.project_path)
		self.db.DBQUERY_table_set('Risk1')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		risk1_registers = self.db.DBQUERY_query()	
		
		for r1 in risk1_registers:
			
			risk_ref = r1['AutoComm'].split(' x ')[1].split("\n")[0]
			if len(risk_ref) <= 6:
				self.db.DBQUERY_table_set('RiskCatalog')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('InternalId = "' + risk_ref + '"')
				riski_reg =  self.db.DBQUERY_query()[0]
				risk_name = " x " + risk_ref + " " + riski_reg["Name"] + "\n"
				
				dbri.DBQUERY_table_set('Applicability')
				dbri.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				dbri.DBQUERY_filter_set('Id = "' + riski_reg["ApplicabilityId"] + '"')
				appli_reg = self.db.DBQUERY_query()[0]
				
				#risk_ref = " x " + risk_ref + " [" + appli_reg["Applicability"] + "]\n"
				risk_ref = " x " + risk_ref + " [SSSSSSSSSSSSSSSSSSSSSSSSSSS]\n"

				r1['AutoComm'] = r1['AutoComm'].replace(risk_ref, risk_name)
				
				self.db.risk1_update(r1)

		#%%%%
		print("- Guardando el riesgo inherente no registrado")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('(Applicability = "AY" OR Applicability = "Y")')
		ap = self.db.DBQUERY_query()

		for a in ap:
			self.db.DBQUERY_table_set('Risk1')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(a['Id']))
			r = self.db.DBQUERY_query(True)
			
			if r ==0:
				
				self.db.DBQUERY_table_set('RiskCatalog')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + str(a['RiskId']))
				risk = self.db.DBQUERY_query()
				dims = risk[0]["Dims"]
				
				self.db.DBQUERY_table_set('Assets')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + str(a['AssetId']))
				asset = self.db.DBQUERY_query()[0]
				
				data_model = self.db.risk1_data_model.copy()
				data_model["ApplicabilityId"] = a['Id']
				data_model["Iteration"] = a['Iteration']
				data_model["Scope"] = a['Scope']
				data_model["Updated"] = datetime.today().strftime('%Y-%m-%d')
				data_model["Reviewed"] = datetime.today().strftime('%Y-%m-%d')
				data_model["AutoComm"] = a['AutoComm']
				data_model["P"] = -1
				data_model["D1"] = -9
				data_model["D2"] = -9
				data_model["D3"] = -9
				data_model["D4"] = -9
				data_model["D5"] = -9
				data_model["D6"] = -9
				data_model["D7"] = -9
				data_model["D8"] = -9
				data_model["D9"] = -9
				data_model["D10"] = -9
				data_model["R1"] = -9
				data_model["R2"] = -9
				data_model["R3"] = -9
				data_model["R4"] = -9
				data_model["R5"] = -9
				data_model["R6"] = -9
				data_model["R7"] = -9
				data_model["R8"] = -9
				data_model["R9"] = -9
				data_model["R10"] = -9

				counter = 1
				for dim in self.dims:
					applies_dim = risk[0]['Dims'].find(dim['short'])
					if applies_dim > -1:
						index = "D" + str(counter)
						data_model[index] = -1
						index = "R" + str(counter)
						data_model[index] = -1
					counter += 1
				
				self.db.risk1_insert(data_model)




		#%%%%
		print("- Guardando el riesgo residual no registrado")
		self.db.DBQUERY_table_set('Risk1')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('P > 0')
		r1 = self.db.DBQUERY_query()

		for r in r1:
			self.db.DBQUERY_table_set('Risk2')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(r['ApplicabilityId']))
			registered = self.db.DBQUERY_query(True)
			
			if registered ==0:
				
				r["Updated"] = app.util.today()
				self.db.risk2_insert(r)

		#%%%%				



		#%%%%				


		#!!!!
		print("- Finalizado")
		input('>')

#-------------------------------------------------------------------

	def export_data(self):
		
		for t in app.config.export_data_set:
			table = t
			
			data_model = self.db.TRANSLATION_data_model[table]
			
			path = 'export_' + self.title + "_" + str(self.iteration) + "_" + table + ".cvs"
			e = open(os.path.abspath(os.path.join(".", path)), 'w+')
			
			lines = ""
			for dm in data_model:
				lines += "\""+ dm + "\";"
			lines=lines[:-1] + "\n"
			
			self.db.DBQUERY_clean()
			self.db.DBQUERY_table_set(table)
			export = self.db.DBQUERY_query()

			for l in export:
				for dm in data_model:
					lines+= "\""+ str(l[dm]) + "\";"
				lines=lines[:-1] + "\n"
			lines=lines[:-1]
			
			e.write(lines)
			e.close()


#-------------------------------------------------------------------

	def get_dependences_by_assetid(self, asset):
	
		dependences = []
		
		if not (asset["Dependences"] == None or asset["Dependences"] == "None" or asset["Dependences"] == ""):
			for dep in asset["Dependences"].split(","):
				
				self.db.DBQUERY_table_set('Assets')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + str(dep))
				dependences.append(self.db.DBQUERY_query()[0])

		return dependences
	
	
#-------------------------------------------------------------------

	def update_risk3_values_by_dependences(self, oa, dependences, nchanges, changed_list):
	#	print(nchanges, changed_list)
	#	asset_changed = False
	#	rindex = ["P", "D1", "D2", "D3", "D4", "D5"]
		
		# First, we create the list of risk that are going to affect the asset
	#	risk_list = []
	#	for d in (dependences+[oa]):
			
	#		self.db.DBQUERY_table_set('Applicability')
	#		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
	#		self.db.DBQUERY_filter_set('AssetId = ' + str(d["Id"]))
	#		self.db.DBQUERY_filter_set("(Applicability = 'Y' OR Applicability = 'AY')")
	#		for r in self.db.DBQUERY_query():
	#			if nchanges == 0:
	#				if not r["RiskId"] in risk_list:
	#					risk_list.append(r["RiskId"])
	#			else:
	#				if r["AssetId"] in changed_list:
	#					if not r["RiskId"] in risk_list:
	#						risk_list.append(r["RiskId"])
		
	#	print 
		
		#We extract from the db the r3 value for the asset x risk, compare with all the dependences
	#		for rl in risk_list:

	#			r_original = self.get_r_by_asset_risk(oa["Id"], rl, 3)
	#			risk_changed = False
				
	#			for dep in dependences:

	#				if dep["Id"] in changed_list:

	#					r_new = self.get_r_by_asset_risk(dep["Id"], rl, 3)
						
	#					for i in rindex:

	#						if r_new[i] > r_original[i]:
	#							r_original[i] = r_new[i]
	#							asset_changed = True
	#							risk_changed = True
				
	#			if risk_changed:
	#				for x in range(1,6):
	#					r_original["R"+str(x)] = oa["Value"] * r_original["P"] * r_original["D"+str(x)]
	#				self.db.risk3_update(r_original, comm=False)

		return asset_changed


#-------------------------------------------------------------------

	def clean_r2_r3(self):

		print("- Purgando riesgos previos")
		self.db.risk2_truncate()
		self.db.risk3_truncate()
		self.db.DB_COMMIT()
		

#-------------------------------------------------------------------

	def get_r_by_asset_risk(self, assetid, riskid, rindex):
		
		rindex = str(rindex)
		
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('AssetId = ' + str(assetid))
		self.db.DBQUERY_filter_set('RiskId = ' + str(riskid))	
		ap = self.db.DBQUERY_query()[0]
		
		self.db.DBQUERY_table_set('Risk' + rindex)
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap["Id"]))
		rcheck = self.db.DBQUERY_query(True)
		#If the register does not exist, we create it now
		if rcheck == 0:
			data_model = self.db.TRANSLATION_data_model["Risk"+rindex].copy()
			data_model["ApplicabilityId"] = str(ap["Id"])
			data_model["Updated"] = app.util.today()
			data_model["Reviewed"] = app.util.today()
			data_model["Iteration"] = self.iteration			
			data_model["P"] = -9
			for x in range(1,11):
				data_model["D"+str(x)] = -9
				data_model["R"+str(x)] = -9
			self.db.risk3_insert(data_model)
		
		
		self.db.DBQUERY_table_set('Risk' + rindex)
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap["Id"]))
		risk_register = self.db.DBQUERY_query()[0]
		
		return risk_register



#-------------------------------------------------------------------

	def expanse_applicability(self):

		print("- Resolviendo incoherencias de aplicabilidad")

		print("  + Creando nuevos registros de cruce")
		self.db.DBQUERY_table_set('Assets')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		asset_list = self.db.DBQUERY_query()

		self.db.DBQUERY_table_set('RiskCatalog')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		risk_list = self.db.DBQUERY_query()

		for al in asset_list:
			for rl in risk_list:

				self.db.DBQUERY_table_set('Applicability')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('AssetId = ' + str(al["Id"]))
				self.db.DBQUERY_filter_set('RiskId = ' + str(rl["Id"]))
				cross = self.db.DBQUERY_query()
				
				if len(cross) == 0:
					data_model = self.db.TRANSLATION_data_model["Applicability"].copy()
					data_model["AssetId"]=al["Id"]
					data_model["RiskId"]=rl["Id"]
					if al["Active"] == 0 or rl["Active"] == 0:
						data_model["Active"]=0
					else:
						data_model["Active"]=1
					data_model["Applicability"]="NE"
					data_model["Updated"]=self.today
					data_model["Reviewed"]=self.today
					data_model["Iteration"]=self.iteration
					data_model["Scope"]=al["Scope"]
					self.db.TABLE_insert("Applicability", data_model)
					
		self.db.DB_COMMIT()

		print("  + Determinando autoaplicabilidad de los nuevos registros")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		self.db.DBQUERY_filter_set("Applicability = 'NE'")
		ane = self.db.DBQUERY_query()
		
		for ae in ane:
			
			self.db.DBQUERY_table_set('Assets')
			self.db.DBQUERY_filter_set('Id = ' + str(ae['AssetId']))
			self.db.DBQUERY_filter_set('Active = 1')
			asset = self.db.DBQUERY_query()[0]
		
			self.db.DBQUERY_table_set('RiskCatalog')
			self.db.DBQUERY_filter_set('Id = ' + str(ae['RiskId']))
			self.db.DBQUERY_filter_set('Active = 1')
			risk = self.db.DBQUERY_query()[0]
			
			applies = False
			for criteria in risk['Applicability'].split(','):
				if asset['InternalId'].find(criteria) > -1:
					applies = True
			if applies:
				ae['Applicability'] = 'AY'
			else:
				ae['Applicability'] = 'AN'
			ae['Updated'] = self.today
			self.db.TABLE_update("Applicability", ae)
		self.db.DB_COMMIT()



		print("- Extendiendo aplicabilidad a cálculos de riesgo")
		r_index = ["Risk1", "Risk2", "Risk3"]

		print("  + Creando nuevos registros de R1")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		self.db.DBQUERY_filter_set("(Applicability = 'Y' OR Applicability = 'AY')")
		applicability_list = self.db.DBQUERY_query()

		for ap in applicability_list:
			self.db.DBQUERY_table_set("Risk1")
			self.db.DBQUERY_filter_set("ApplicabilityId = '" + str(ap["Id"]) + "'")

			if self.db.DBQUERY_query(True) == 0:

				self.db.DBQUERY_table_set("RiskCatalog")
				self.db.DBQUERY_filter_set("Id = " + str(ap["RiskId"]))
				risk_reference = self.db.DBQUERY_query()[0]
				
				self.db.DBQUERY_table_set("Assets")
				self.db.DBQUERY_filter_set("Id = " + str(ap["AssetId"]))
				asset_reference = self.db.DBQUERY_query()[0]

				data_model = self.db.risk1_data_model.copy()
				data_model["ApplicabilityId"]=ap["Id"]
				data_model["P"]=-1
				data_model["D1"]=-9
				data_model["D2"]=-9
				data_model["D3"]=-9
				data_model["D4"]=-9
				data_model["D5"]=-9
				data_model["D6"]=-9
				data_model["D7"]=-9
				data_model["D8"]=-9
				data_model["D9"]=-9
				data_model["D10"]=-9
				data_model["R1"]=-9
				data_model["R2"]=-9
				data_model["R3"]=-9
				data_model["R4"]=-9
				data_model["R5"]=-9
				data_model["R6"]=-9
				data_model["R7"]=-9
				data_model["R8"]=-9
				data_model["R9"]=-9
				data_model["R10"]=-9
				dim_index = 0
				for d in self.dims:
					dim_index += 1					
					if d["short"] in risk_reference["Dims"]:
						data_model["D"+str(dim_index)] = -1
						data_model["R"+str(dim_index)] = -1
				data_model["Active"]=1
				data_model["Updated"]=self.today
				data_model["Reviewed"]=self.today
				data_model["Iteration"]=self.iteration
				data_model["Scope"]=asset_reference["Scope"]
				self.db.TABLE_insert("Risk1", data_model)
		self.db.DB_COMMIT()	
				
		print("  + Creando nuevos registros de R2")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		self.db.DBQUERY_filter_set("(Applicability = 'Y' OR Applicability = 'AY')")
		applicability_list = self.db.DBQUERY_query()

		for ap in applicability_list:
			self.db.DBQUERY_table_set("Risk2")
			self.db.DBQUERY_filter_set("ApplicabilityId = '" + str(ap["Id"]) + "'")

			if self.db.DBQUERY_query(True) == 0:

				self.db.DBQUERY_table_set("RiskCatalog")
				self.db.DBQUERY_filter_set("Id = " + str(ap["RiskId"]))
				risk_reference = self.db.DBQUERY_query()[0]
				
				self.db.DBQUERY_table_set("Assets")
				self.db.DBQUERY_filter_set("Id = " + str(ap["AssetId"]))
				asset_reference = self.db.DBQUERY_query()[0]

				data_model = self.db.risk1_data_model.copy()
				data_model["ApplicabilityId"]=ap["Id"]
				data_model["P"]=-1
				data_model["D1"]=-9
				data_model["D2"]=-9
				data_model["D3"]=-9
				data_model["D4"]=-9
				data_model["D5"]=-9
				data_model["D6"]=-9
				data_model["D7"]=-9
				data_model["D8"]=-9
				data_model["D9"]=-9
				data_model["D10"]=-9
				data_model["R1"]=-9
				data_model["R2"]=-9
				data_model["R3"]=-9
				data_model["R4"]=-9
				data_model["R5"]=-9
				data_model["R6"]=-9
				data_model["R7"]=-9
				data_model["R8"]=-9
				data_model["R9"]=-9
				data_model["R10"]=-9
				dim_index = 0
				for d in self.dims:
					dim_index += 1					
					if d["short"] in risk_reference["Dims"]:
						data_model["D"+str(dim_index)] = -1
						data_model["R"+str(dim_index)] = -1
				data_model["Active"]=1
				data_model["Updated"]=self.today
				data_model["Reviewed"]=self.today
				data_model["Iteration"]=self.iteration
				data_model["Scope"]=asset_reference["Scope"]
				self.db.TABLE_insert("Risk2", data_model)
		self.db.DB_COMMIT()	

		print("  + Creando nuevos registros de R3")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		applicability_list = self.db.DBQUERY_query()

		for ap in applicability_list:
			self.db.DBQUERY_table_set("Risk3")
			self.db.DBQUERY_filter_set("ApplicabilityId = '" + str(ap["Id"]) + "'")

			if self.db.DBQUERY_query(True) == 0:

				self.db.DBQUERY_table_set("RiskCatalog")
				self.db.DBQUERY_filter_set("Id = " + str(ap["RiskId"]))
				risk_reference = self.db.DBQUERY_query()[0]
				
				self.db.DBQUERY_table_set("Assets")
				self.db.DBQUERY_filter_set("Id = " + str(ap["AssetId"]))
				asset_reference = self.db.DBQUERY_query()[0]

				data_model = self.db.risk1_data_model.copy()
				data_model["ApplicabilityId"]=ap["Id"]
				data_model["P"]=-1
				data_model["D1"]=-9
				data_model["D2"]=-9
				data_model["D3"]=-9
				data_model["D4"]=-9
				data_model["D5"]=-9
				data_model["D6"]=-9
				data_model["D7"]=-9
				data_model["D8"]=-9
				data_model["D9"]=-9
				data_model["D10"]=-9
				data_model["R1"]=-9
				data_model["R2"]=-9
				data_model["R3"]=-9
				data_model["R4"]=-9
				data_model["R5"]=-9
				data_model["R6"]=-9
				data_model["R7"]=-9
				data_model["R8"]=-9
				data_model["R9"]=-9
				data_model["R10"]=-9
				dim_index = 0
				for d in self.dims:
					dim_index += 1					
					if d["short"] in risk_reference["Dims"]:
						data_model["D"+str(dim_index)] = -1
						data_model["R"+str(dim_index)] = -1
				data_model["Active"]=1
				data_model["Updated"]=self.today
				data_model["Reviewed"]=self.today
				data_model["Iteration"]=self.iteration
				data_model["Scope"]=asset_reference["Scope"]
				self.db.TABLE_insert("Risk3", data_model)
		self.db.DB_COMMIT()	
				
		print("  + Actualizando registros aplicables")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		self.db.DBQUERY_filter_set("(Applicability = 'Y' OR Applicability = 'AY')")
		applicability_list = self.db.DBQUERY_query()
		for ap in applicability_list:
			for x in r_index:
				self.db.DBQUERY_table_set(x)
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap["Id"]))
				risk_list = self.db.DBQUERY_query()
				for risk in risk_list:
					if not risk["Active"] == 1:
						risk["Active"] = 1
						risk["Updated"] = self.today
						self.db.TABLE_update(x, risk)
						

		print("  + Actualizando registros no aplicables")
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Active = 1')
		self.db.DBQUERY_filter_set("(Applicability = 'N' OR Applicability = 'AN')")
		applicability_list = self.db.DBQUERY_query()
		for ap in applicability_list:
			for x in r_index:
				self.db.DBQUERY_table_set(x)
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap["Id"]))
				risk_list = self.db.DBQUERY_query()
				for risk in risk_list:
					if not risk["Active"] == 0:
						risk["Active"] = 0
						risk["Updated"] = self.today
						self.db.TABLE_update(x, risk)
		
		self.db.DB_COMMIT()


				
#-------------------------------------------------------------------
	
