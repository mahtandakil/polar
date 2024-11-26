import app.db
import app.config


import os


class Report:
	
#-------------------------------------------------------------------

	def report1(self, db, iteration, project_config):

		self.iteration = iteration
		self.db = db
		self.project_config = project_config

		fp = "Report - "

		f = open(os.path.join('.', 'app', 'report1.html'))
		repo = f.read()
		f.close()

		repo = repo.replace('<APP_VERSION>', app.config.app_version)
		
		db.DBQUERY_table_set('Common')
		db.DBQUERY_filter_set("Register = 'organization'")
		dbv = db.DBQUERY_query()[0]
		repo = repo.replace('<COMPANY>', dbv['Value'])
		fp += dbv['Value'] + " - "

		db.DBQUERY_table_set('Iteration')
		db.DBQUERY_filter_set('Id = ' + str(iteration))
		dbv = db.DBQUERY_query()[0]
		repo = repo.replace('<ITERATION>', dbv['Name'])
		fp += dbv['Name'] + ".html"
		
		db.DBQUERY_table_set('Assets')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set('Active = 1')
		dbv = db.DBQUERY_query(True)
		repo = repo.replace('<#_ASSETS>', str(dbv))
		
		db.DBQUERY_table_set('RiskCatalog')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set('Active = 1')
		dbv = db.DBQUERY_query(True)
		repo = repo.replace('<#_CATALOG>', str(dbv))		

		db.DBQUERY_table_set('Applicability')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set("Applicability = 'Y'")
		db.DBQUERY_filter_set('Active = 1')
		dbv_1 = db.DBQUERY_query(True)
		db.DBQUERY_table_set('Applicability')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set("Applicability = 'AY'")
		db.DBQUERY_filter_set('Active = 1')
		dbv_2 = db.DBQUERY_query(True)
		repo = repo.replace('<#_APPLICABILITY>', str(dbv_1+dbv_2))		

		db.DBQUERY_table_set('Common')
		db.DBQUERY_filter_set("Register = 'dims'")
		dbv = db.DBQUERY_query()[0]
		repo = repo.replace('<#_DIMS>', dbv['Value'])

		#-----------------------------------------------------------------------------
		# MENU & GENERAL 
		#-----------------------------------------------------------------------------

		db.DBQUERY_table_set('Common')
		db.DBQUERY_filter_set("Register = 'organization'")
		dbv = db.DBQUERY_query()[0]
		value = dbv['Value']
		db.DBQUERY_table_set('Common')
		db.DBQUERY_filter_set("Register = 'title'")
		value += " - " + db.DBQUERY_query()[0]['Value']	
		repo = repo.replace('<PROJECT_NAME>', value)

		db.DBQUERY_table_set('Common')
		db.DBQUERY_filter_set("Register = 'org_logo'")
		dbv = db.DBQUERY_query()[0]
		repo = repo.replace('<PROJECT_LOGO>', dbv['Value'])
		
		db.DBQUERY_table_set('Iteration')
		db.DBQUERY_filter_set('Id = ' + str(iteration))
		dbv = db.DBQUERY_query()[0]
		repo = repo.replace('<ITERATION_COMMENT>', dbv['Comments'])

		db.DBQUERY_table_set('Iteration')
		db.DBQUERY_filter_set('Id = ' + str(iteration))
		dbv = db.DBQUERY_query()[0]
		repo = repo.replace('<ITERATION_NAME>', dbv['Name'])

		repo = repo.replace('<ITERATION_ID>', str(self.iteration))

		#-----------------------------------------------------------------------------
		# ASSETS SECTION 
		#-----------------------------------------------------------------------------
		composed = ""
		ite = repo.split("<[!ITERABLE_ASSET]>")[1]
		ite_pre = repo.split("<[!ITERABLE_ASSET]>")[0]
		ite_post = ite.split("<[ITERABLE_ASSET!]>")[1]
		ite = ite.split("<[ITERABLE_ASSET!]>")[0]
		db.DBQUERY_table_set('Assets')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set('Active = 1')
		db.DBQUERY_order_set("ORDER BY Name ASC")
		dbv = db.DBQUERY_query()

		for asset in dbv:
			pivot = ite
			pivot = pivot.replace("<IT_ASSET_ICONS>", self.common_get_asset_icons(asset))
			pivot = pivot.replace("<IT_ASSET_ID>", str(asset["Id"]))
			pivot = pivot.replace("<IT_ASSET_INTERNAL_ID>", str(asset["InternalId"]))
			pivot = pivot.replace("<IT_ASSET_NAME>", asset["Name"])
			pivot = pivot.replace("<IT_ASSET_VALUE>", str(asset["Value"]))
			pivot = pivot.replace("<IT_ASSET_SCOPE>", asset["Scope"])
			composed += pivot
		repo = ite_pre + composed + ite_post

		#-----------------------------------------------------------------------------
		# RISK CATALOG SECTION 
		#-----------------------------------------------------------------------------		
		composed = ""
		ite = repo.split("<[!ITERABLE_RISKCATALOG]>")[1]
		ite_pre = repo.split("<[!ITERABLE_RISKCATALOG]>")[0]
		ite_post = ite.split("<[ITERABLE_RISKCATALOG!]>")[1]
		ite = ite.split("<[ITERABLE_RISKCATALOG!]>")[0]
		db.DBQUERY_table_set('RiskCatalog')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set('Active = 1')
		db.DBQUERY_order_set("ORDER BY InternalId ASC")
		dbv = db.DBQUERY_query()
		for risk in dbv:
			pivot = ite
			pivot = pivot.replace("<IT_RISK_ID>", str(risk["Id"]))
			pivot = pivot.replace("<IT_RISK_CODE>", risk["InternalId"])
			pivot = pivot.replace("<IT_RISK_NAME>", risk["Name"])
			description = "Aplica a: " + str(risk["Applicability"]) + "\n\n" + str(risk["Description"])
			pivot = pivot.replace("<IT_RISK_DESCRIPTION>", description)
			pivot = pivot.replace("<IT_RISK_DIMS>", risk["Dims"])
			composed += pivot
		repo = ite_pre + composed + ite_post

		#-----------------------------------------------------------------------------
		# CONTROLS SECTION 
		#-----------------------------------------------------------------------------
		composed = ""
		index = ["P", "D1", "D2", "D3", "D4", "D5"]
		ite = repo.split("<[!ITERABLE_CONTROL_ANALISYS]>")[1]
		ite_pre = repo.split("<[!ITERABLE_CONTROL_ANALISYS]>")[0]
		ite_post = ite.split("<[ITERABLE_CONTROL_ANALISYS!]>")[1]
		ite = ite.split("<[ITERABLE_CONTROL_ANALISYS!]>")[0]
		db.DBQUERY_table_set('SecurityControls')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set('Active = 1')
		db.DBQUERY_order_set("ORDER BY Name ASC")
		dbv = db.DBQUERY_query()
		for control in dbv:
			
			pivot = ite
			pivot = pivot.replace("<IT_CONTROL_ID>", str(control["Id"]))
			pivot = pivot.replace("<IT_CONTROL_NAME>", str(control["Name"]))
			pivot = pivot.replace("<IT_CONTROL_ANALISIS>", str(control["Comments"]))
			for i in index:
				ref = "<IT_CONTROL_"+i+">"
				
				if control[i] <= 0 or control[i] == None or control[i] == "":
					pivot = pivot.replace(ref, "_")
				else:
					pivot = pivot.replace(ref, str(control[i]))		
			composed += pivot
		repo = ite_pre + composed + ite_post

		#-----------------------------------------------------------------------------
		# ASSET ANALYSIS SECTION 
		#-----------------------------------------------------------------------------
		composed = ""
		ite = repo.split("<[!ITERABLE_ASSET_ANALISYS]>")[1]
		ite_pre = repo.split("<[!ITERABLE_ASSET_ANALISYS]>")[0]
		ite_post = ite.split("<[ITERABLE_ASSET_ANALISYS!]>")[1]
		ite = ite.split("<[ITERABLE_ASSET_ANALISYS!]>")[0]
		
		#Asset iteration
		db.DBQUERY_table_set('Assets')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		db.DBQUERY_filter_set('Active = 1')
		db.DBQUERY_order_set("ORDER BY Name ASC")
		dbv = db.DBQUERY_query()
		for asset in dbv:
			#Essential values
			pivot = ite
			pivot = pivot.replace("<IT_ASSET_ID>", str(asset["Id"]))
			pivot = pivot.replace("<IT_ASSET_ICONS>", self.common_get_asset_icons(asset))
			pivot = pivot.replace("<IT_ASSET_NAME>", asset["Name"])
			pivot = pivot.replace("<IT_ASSET_VALUE>", str(asset["Value"]))
			
			#Dependences tree 1
			impactados = ""
			for ass2 in dbv:
				if str(asset["Id"]) in str(ass2["Dependences"]).split(","):
					impactados += "<a href='#asset_analysis_" + str(ass2["Id"]) + "'>" + ass2["Name"] + "</a>, "
			if len(impactados)>2:
				impactados = impactados[:-2]
			pivot = pivot.replace("<ASSET_SENDIG_RISK>", impactados)
			
			#Dependences tree 2
			emisores = ""
			for ass2 in str(asset["Dependences"]).split(","):
				if not(ass2 == None or ass2 == "None" or ass2 == ""):
					db.DBQUERY_table_set('Assets')
					db.DBQUERY_filter_set('Iteration = ' + str(iteration))
					db.DBQUERY_filter_set('Id = ' + str(ass2))
					dbass2 = db.DBQUERY_query()[0]
					emisores +="<a href='#asset_analysis_" + str(dbass2["Id"]) + "'>" + dbass2["Name"] + "</a>, "
			if len(emisores)>2:
				emisores = emisores[:-2]
			pivot = pivot.replace("<ASSET_GETTING_RISK>", emisores)

			#Applicable control list 
			security_controls = ""
			sc_list = []
			db.DBQUERY_table_set('Applicability')
			db.DBQUERY_filter_set('Iteration = ' + str(iteration))
			db.DBQUERY_filter_set('AssetId = ' + str(asset["Id"]))
			db.DBQUERY_filter_set("(Applicability = 'Y' OR Applicability = 'AY')")
			for ap in db.DBQUERY_query():
				
				for scap in ap["SecurityControlsId"].split(","):
					if (not scap in sc_list) and not (scap == None or scap == "None" or scap=="" or scap==0):
						sc_list.append(scap)
						db.DBQUERY_table_set('SecurityControls')
						db.DBQUERY_filter_set('Iteration = ' + str(iteration))
						db.DBQUERY_filter_set('Id = ' + str(scap))
						dbsc2 = db.DBQUERY_query()[0]
						security_controls += "<a href='#control_analysis_" + str(scap) + "'>" + str(dbsc2["Name"]) + "</a>, " 
			if len(security_controls)>2:
				security_controls = security_controls[:-2]
			pivot = pivot.replace("<ASSET_SECURITY_CONTROL_LIST>", security_controls)
			
			
			ite_l2 = pivot.split("<[!ITERABLE_ASSETxRISK_ANALISYS]>")[1]
			ite_pre_l2 = pivot.split("<[!ITERABLE_ASSETxRISK_ANALISYS]>")[0]
			ite_post_l2 = ite_l2.split("<[ITERABLE_ASSETxRISK_ANALISYS!]>")[1]
			ite_l2 = ite_l2.split("<[ITERABLE_ASSETxRISK_ANALISYS!]>")[0]
			
			pivot = ite_pre_l2 + self.common_asset_x_risk(ite_l2, asset["Id"], asset["Name"]) + ite_post_l2
			
			composed += pivot
		repo = ite_pre + composed + ite_post

		repo = repo.replace('<MAX_RA_COUNT>', str(self.project_config["report_max_ra"]))
		db.DBQUERY_table_set('Risk3')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		dbv = db.DBQUERY_query()
		
		composed = ""
		rlist = []
		r3list = []
		for r3 in dbv:
			for x in range (1, 6):
				risk = round(r3["R"+str(x)], 2)
				if risk>0:
					if not risk in rlist:
						rlist.append(risk)
		rlist.sort(reverse=True)
		rdims = ["Disponibilidad", "Integridad", "Confidencialidad", "Autenticidad", "Trazabilidad"]
		db.DBQUERY_table_set('Risk3')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		dbv = db.DBQUERY_query()
		while len(r3list) < int(self.project_config["report_max_ra"]):
			rreference = rlist.pop(0)
			for r3 in dbv:
				for x in range (1, 6):
					risk = round(r3["R"+str(x)], 2)
					if risk == rreference and len(r3list) < int(self.project_config["report_max_ra"]) + 1:
						r3list.append({"ApplicabilityId": r3["ApplicabilityId"], "dim":rdims[x-1], "R":r3["R"+str(x)]})
		for x in r3list:
			db.DBQUERY_table_set('Applicability')
			db.DBQUERY_filter_set('Iteration = ' + str(iteration))
			db.DBQUERY_filter_set('Id = ' + str(x["ApplicabilityId"]))
			dbv = db.DBQUERY_query()[0]
			dbv_asset = dbv["AssetId"]
			dbv_risk = dbv["RiskId"]
			db.DBQUERY_table_set('Assets')
			db.DBQUERY_filter_set('Iteration = ' + str(iteration))
			db.DBQUERY_filter_set('Id = ' + str(dbv_asset))
			dbv = db.DBQUERY_query()[0]
			x["Asset"] = dbv["Name"]
			x["AssetId"] = dbv["Id"]
			db.DBQUERY_table_set('RiskCatalog')
			db.DBQUERY_filter_set('Iteration = ' + str(iteration))
			db.DBQUERY_filter_set('Id = ' + str(dbv_risk))
			dbv = db.DBQUERY_query()[0]
			x["Risk"] = dbv["InternalId"] + ". " + dbv["Name"]
		ite = repo.split("<[!ITERABLE_MAX_RA]>")[1]
		ite_pre = repo.split("<[!ITERABLE_MAX_RA]>")[0]
		ite_post = ite.split("<[ITERABLE_MAX_RA!]>")[1]
		ite = ite.split("<[ITERABLE_MAX_RA!]>")[0]
		count = 0
		r3_values={}
		r3_count={}
		for r3 in r3list:
			count += 1
			pivot = ite
			if not r3["Risk"] in r3_values:
				r3_values[r3["Risk"]] = round(r3["R"])
				r3_count[r3["Risk"]] = 1
			else:
				r3_values[r3["Risk"]] += round(r3["R"])
				r3_count[r3["Risk"]] += 1
			pivot = pivot.replace("<IT_ITER_COUNT>", str(count))
			pivot = pivot.replace("<[IT_ASSET_NAME]>", str(r3["Asset"]))
			pivot = pivot.replace("<[IT_ASSET_ID]>", str(r3["AssetId"]))
			pivot = pivot.replace("<[IT_RISK_NAME]>", str(r3["Risk"]))
			pivot = pivot.replace("<[IT_RISK_DIM]>", str(r3["dim"]))
			pivot = pivot.replace("<[IT_RISK_VALUE_SHORT]>", str(round(r3["R"])))
			pivot = pivot.replace("<[IT_RISK_VALUE_FULL]>", str(round(r3["R"], 2)))
			if r3["R"] > 80:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "black")
			elif  r3["R"] > 60:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "red")
			elif  r3["R"] > 30:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "yellow")
			else:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "green")
			
			composed += pivot
		repo = ite_pre + composed + ite_post			

		composed = ""
		ite = repo.split("<[!ITERABLE_COUNT_RA]>")[1]
		ite_pre = repo.split("<[!ITERABLE_COUNT_RA]>")[0]
		ite_post = ite.split("<[ITERABLE_COUNT_RA!]>")[1]
		ite = ite.split("<[ITERABLE_COUNT_RA!]>")[0]
		for r3_index in r3_count:
			pivot = ite
			pivot = pivot.replace("<IT_RISK_NAME>", r3_index)
			pivot = pivot.replace("<IT_RISK_COUNT>", str(r3_count[r3_index]))
			pivot = pivot.replace("<IT_RISK_VALUE>", str(r3_values[r3_index]))
			composed += pivot
		repo = ite_pre + composed + ite_post	



		#---------------------------------------------------------------------------------------------
		repo = repo.replace('<MAX_RR_COUNT>', str(self.project_config["report_max_rr"]))
		db.DBQUERY_table_set('Risk2')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		dbv = db.DBQUERY_query()

		composed = ""
		rlist = []
		r2list = []
		for r2 in dbv:
			for x in range (1, 6):
				risk = round(r2["R"+str(x)], 2)
				if risk>0:
					if not risk in rlist:
						rlist.append(risk)
		rlist.sort(reverse=True)
		rdims = ["Disponibilidad", "Integridad", "Confidencialidad", "Autenticidad", "Trazabilidad"]
		db.DBQUERY_table_set('Risk2')
		db.DBQUERY_filter_set('Iteration = ' + str(iteration))
		dbv = db.DBQUERY_query()
		
		while len(r2list) < int(self.project_config["report_max_rr"]):
			rreference = rlist.pop(0)
			for r2 in dbv:
				for x in range (1, 6):
					risk = round(r2["R"+str(x)], 2)
					if risk == rreference and len(r2list) < int(self.project_config["report_max_rr"]) + 1:
						r2list.append({"ApplicabilityId": r2["ApplicabilityId"], "dim":rdims[x-1], "R":r2["R"+str(x)]})
		for x in r2list:
			db.DBQUERY_table_set('Applicability')
			db.DBQUERY_filter_set('Iteration = ' + str(iteration))
			db.DBQUERY_filter_set('Id = ' + str(x["ApplicabilityId"]))
			dbv = db.DBQUERY_query()[0]
			dbv_asset = dbv["AssetId"]
			dbv_risk = dbv["RiskId"]
			db.DBQUERY_table_set('Assets')
			db.DBQUERY_filter_set('Iteration = ' + str(iteration))
			db.DBQUERY_filter_set('Id = ' + str(dbv_asset))
			dbv = db.DBQUERY_query()[0]
			x["Asset"] = dbv["Name"]
			x["AssetId"] = dbv["Id"]
			db.DBQUERY_table_set('RiskCatalog')
			db.DBQUERY_filter_set('Iteration = ' + str(iteration))
			db.DBQUERY_filter_set('Id = ' + str(dbv_risk))
			dbv = db.DBQUERY_query()[0]
			x["Risk"] = dbv["InternalId"] + ". " + dbv["Name"]
		ite = repo.split("<[!ITERABLE_MAX_RR]>")[1]
		ite_pre = repo.split("<[!ITERABLE_MAX_RR]>")[0]
		ite_post = ite.split("<[ITERABLE_MAX_RR!]>")[1]
		ite = ite.split("<[ITERABLE_MAX_RR!]>")[0]
		count = 0
		r2_values={}
		r2_count={}
		for r2 in r2list:
			count += 1
			pivot = ite
			pivot = pivot.replace("<IT_ITER_COUNT>", str(count))
			pivot = pivot.replace("<[IT_ASSET_NAME]>", str(r2["Asset"]))
			pivot = pivot.replace("<[IT_ASSET_ID]>", str(r2["AssetId"]))
			pivot = pivot.replace("<[IT_RISK_NAME]>", str(r2["Risk"]))
			if not r2["Risk"] in r2_values:
				r2_values[r2["Risk"]] = round(r2["R"])
				r2_count[r2["Risk"]] = 1
			else:
				r2_values[r2["Risk"]] += round(r2["R"])
				r2_count[r2["Risk"]] += 1
			pivot = pivot.replace("<[IT_RISK_DIM]>", str(r2["dim"]))
			pivot = pivot.replace("<[IT_RISK_VALUE_SHORT]>", str(round(r2["R"])))
			pivot = pivot.replace("<[IT_RISK_VALUE_FULL]>", str(round(r2["R"], 2)))
			if r2["R"] > 80:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "black")
			elif  r2["R"] > 60:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "red")
			elif  r2["R"] > 30:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "yellow")
			else:
				pivot = pivot.replace("<[IT_RISK_COLOUR]>", "green")
			
			composed += pivot
		repo = ite_pre + composed + ite_post	
		
		composed = ""
		ite = repo.split("<[!ITERABLE_COUNT_RR]>")[1]
		ite_pre = repo.split("<[!ITERABLE_COUNT_RR]>")[0]
		ite_post = ite.split("<[ITERABLE_COUNT_RR!]>")[1]
		ite = ite.split("<[ITERABLE_COUNT_RR!]>")[0]
		for r2_index in r2_count:
			pivot = ite
			pivot = pivot.replace("<IT_RISK_NAME>", r2_index)
			pivot = pivot.replace("<IT_RISK_COUNT>", str(r2_count[r2_index]))
			pivot = pivot.replace("<IT_RISK_VALUE>", str(r2_values[r2_index]))
			composed += pivot
		repo = ite_pre + composed + ite_post	



		f = open(os.path.join('.', fp), 'w')
		f.write(repo)
		f.close()



#-------------------------------------------------------------------

	def common_get_asset_icons(self, asset):
		
		
		nature = ""
		if "Personal" in asset["Category"]:
			nature += "<i title='Personal' class='fa fa-user w3-text-blue w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Instalaciones" in asset["Category"]:
			nature += "<i title='Instalaciones' class='fa fa-building w3-text-amber w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Comunicaciones" in asset["Category"]:
			nature += "<i title='Comunicaciones' class='fa fa-exchange w3-text-aqua w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Hardware" in asset["Category"]:
			nature += "<i title='Hardware' class='fa fa-microchip w3-text-green w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Software" in asset["Category"]:
			nature += "<i title='Software' class='fa fa-slack w3-text-grey w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Servicios" in asset["Category"]:
			nature += "<i title='Servicios' class='fa fa-server w3-text-pink w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Soporte" in asset["Category"]:
			nature += "<i title='Soporte de información' class='fa fa-hdd-o w3-text-deep-purple w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Auxiliar" in asset["Category"]:
			nature += "<i title='Auxiliar' class='fa fa-fire-extinguisher w3-text-lime w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "interno" in asset["Category"]:
			nature += "<i title='Servicio interno' class='fa fa-etsy w3-large' style='color:#E73C2F!important'></i>&nbsp;&nbsp;&nbsp;"
		if "nube" in asset["Category"]:
			nature += "<i title='Servicio en nube' class='fa fa-cloud w3-text-indigo w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "negocio" in asset["Category"]:
			nature += "<i title='Proceso de negocio' class='fa fa-briefcase w3-text-khaki w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "external" in asset["Category"]:
			nature += "<i title='Servicio externalizado' class='fa fa-vcard-o w3-text-brown w3-large'></i>&nbsp;&nbsp;&nbsp;"
		if "Informaci" in asset["Category"]:
			nature += "<i title='Información' class='fa fa-file-text w3-text-deep-orange w3-large'></i>&nbsp;&nbsp;&nbsp;"	
		if "Ajeno" in asset["Category"]:
			nature += "<i title='Ajeno' class='fa fa-exclamation-triangle  w3-text-black w3-large'></i>&nbsp;&nbsp;&nbsp;"	

		return nature
		

#-------------------------------------------------------------------

	def common_asset_x_risk(self, ite, asset_id, asset_name):

		composed = ""

		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('AssetId = ' + str(asset_id))
		self.db.DBQUERY_filter_set('Active = 1')
		self.db.DBQUERY_order_set("ORDER BY AutoComm ASC")
		dbv_ap = self.db.DBQUERY_query()
			
		for ap in dbv_ap:
			self.db.DBQUERY_table_set('RiskCatalog')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('Id = ' + str(ap["RiskId"]))
			rc = self.db.DBQUERY_query()[0]

			self.db.DBQUERY_table_set('Risk3')
			self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
			self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap['Id']))		
			r3 = self.db.DBQUERY_query()

			if len(r3) > 0:
				r3 = r3[0]
				if r3['R1'] > 0 or r3['R2'] > 0 or r3['R3'] > 0 or r3['R4'] > 0 or r3['R5'] > 0:

					pivot = ite

					self.db.DBQUERY_table_set('Risk1')
					self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
					self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap['Id']))		
					r1 = self.db.DBQUERY_query()
						
					self.db.DBQUERY_table_set('Risk2')
					self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
					self.db.DBQUERY_filter_set('ApplicabilityId = ' + str(ap['Id']))		
					r2 = self.db.DBQUERY_query()
						
					pivot = pivot.replace("<IT_ASSETxRISK_RISK_ID>", str(rc["InternalId"]))
					pivot = pivot.replace("<IT_ASSETxRISK_RISK_NAME>", str(rc["Name"]))
					pivot = pivot = pivot.replace("<IT_ASSETxRISK_COMMENTS>", str(asset_name) + "\n" + self.get_control_list_by_cross(ap['Id']))
					
					if round(r3["P"]) == -9:
						pivot = pivot.replace("<IT_ASSETxRISK_RISK_RA_P>", "_")
					else:
						pivot = pivot.replace("<IT_ASSETxRISK_RISK_RA_P>", str(round(r3["P"], 2)))
					for x in range (1,6):
						if(r3["R"+str(x)]) > 0:
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RA_I_D"+str(x)+">", str(round(r3["D"+str(x)], 2)))
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RA_R_D"+str(x)+">", ""+str(round(r3["R"+str(x)], 2)))+""
						else:
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RA_R_D"+str(x)+">", "_")
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RA_I_D"+str(x)+">", "_")
						
					if(len(r2) > 0):
						r2 = r2[0]
						if round(r2["P"]) == -9:
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_P>", "_")
						else:
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_P>", str(round(r2["P"], 2)))
						for x in range (1,6):
							if(r2["R"+str(x)]) > 0:
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_I_D"+str(x)+">", str(round(r2["D"+str(x)], 2)))
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_R_D"+str(x)+">", ""+str(round(r2["R"+str(x)], 2)))+""
							else:
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_R_D"+str(x)+">", "_")
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_I_D"+str(x)+">", "_")
					else:
						pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_P>", "_")
						for x in range (1,6):
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_R_D"+str(x)+">", "_")
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RR_I_D"+str(x)+">", "_")
					
					if(len(r1) > 0):
						r1 = r1[0]
						if round(r1["P"]) == -9:
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_P>", "_")
						else:
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_P>", str(round(r1["P"], 2)))
						for x in range (1,6):
							if(r1["R"+str(x)]) > 0:
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_I_D"+str(x)+">", str(round(r1["D"+str(x)], 2)))
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_R_D"+str(x)+">", ""+str(round(r1["R"+str(x)], 2)))+""
							else:
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_R_D"+str(x)+">", "_")
								pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_I_D"+str(x)+">", "_")
					else:
						pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_P>", "_")
						for x in range (1,6):
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_R_D"+str(x)+">", "_")
							pivot = pivot.replace("<IT_ASSETxRISK_RISK_RI_I_D"+str(x)+">", "_")
							
					composed += pivot
					

		return composed

#-------------------------------------------------------------------

	def get_control_list_by_cross(self, applicabilityid):

		control_list = ""
		
		self.db.DBQUERY_table_set('Applicability')
		self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
		self.db.DBQUERY_filter_set('Id = ' + str(applicabilityid))
		sc_ids = self.db.DBQUERY_query()[0]["SecurityControlsId"].split(",")
		
		for c in sc_ids:
			
			if not (c=="None" or c==None or c==""):
			
				self.db.DBQUERY_table_set('SecurityControls')
				self.db.DBQUERY_filter_set('Iteration = ' + str(self.iteration))
				self.db.DBQUERY_filter_set('Id = ' + str(c))
				cr = self.db.DBQUERY_query()[0]
				control_list += cr["Name"]
		
		if len(control_list) > 2:
			control_list = control_list[:-2]
		
		return control_list


#-------------------------------------------------------------------
