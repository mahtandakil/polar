import app.config
import app.util

import sqlite3

class DB:

#-------------------------------------------------------------------

	def __del__(self):
		print("[!] db connection is out!")


	def __init__(self, path):

		self.applicability_data_model = {
			"Id":0,
			"AssetId":0,
			"RiskId":0,
			"Applicability":'',
			"SecurityControlsId":'',
			"AutoComm":'',
			"Active":0,
			"Updated":'',
			"Reviewed":'',
			"Iteration":0,
			"Scope":'',
			"Comments":'',			
		}

		self.common_data_model = {
			"Id":0,
			"Register":'',
			"Value":'',
		}

		self.iteration_data_model = {
			"Id":0,
			"Name":'',
			"Comments":'',
			"Start":'',
			"End":'',
		}
		
		self.riskcatalog_data_model = {
			"Id":0,
			"InternalId":'',
			"Name":'',
			"Description":'',
			"Applicability":'',
			"Dims":'',
			"Active":0,
			"Updated":'',
			"Reviewed":'',
			"Iteration":0,
			"Comments":'',
		}

		self.assets_data_model = {
			"Id":0,
			"InternalId":'',
			"Name":'',
			"Category":'',
			"Value":0.0,
			"Dependences":'',
			"Active":0,
			"Updated":'',
			"Reviewed":'',
			"Iteration":0,
			"Scope":'',
			"Comments":'',
		}
		
		self.risk1_data_model = {
			"Id":0,
			"ApplicabilityId":0,
			"AutoComm":"",
			"P":0.0,
			"D1":0.0,
			"D2":0.0,
			"D3":0.0,
			"D4":0.0,
			"D5":0.0,
			"D6":0.0,
			"D7":0.0,
			"D8":0.0,
			"D9":0.0,
			"D10":0.0,
			"R1":0.0,
			"R2":0.0,
			"R3":0.0,
			"R4":0.0,
			"R5":0.0,
			"R6":0.0,
			"R7":0.0,
			"R8":0.0,
			"R9":0.0,
			"R10":0.0,
			"Active":0,
			"Updated":"",
			"Reviewed":"",
			"Iteration":0,
			"Scope":"",
			"Comments":"",
		}
		
		self.securitycontrols_data_model = {
			"Id":0,
			"Name":"",
			"P":0.0,
			"D1":0.0,
			"D2":0.0,
			"D3":0.0,
			"D4":0.0,
			"D5":0.0,
			"D6":0.0,
			"D7":0.0,
			"D8":0.0,
			"D9":0.0,
			"D10":0.0,
			"Previous":0,
			"Active":0,
			"Updated":"",
			"Reviewed":"",
			"Iteration":0,
			"Scope":"",
			"Comments":"",
		}	
		
		self.TRANSLATION_data_model = {
			"Common":self.common_data_model,
			"Applicability":self.applicability_data_model,
			"Assets":self.assets_data_model,
			"Iteration":self.iteration_data_model,
			"RiskCatalog":self.riskcatalog_data_model,
			"Risk1":self.risk1_data_model,				
			"Risk2":self.risk1_data_model,				
			"Risk3":self.risk1_data_model,				
			"SecurityControls":self.securitycontrols_data_model,				
		}
	
		self.path = path
		self.conn = sqlite3.connect(self.path)
		self.cur = self.conn.cursor()
		
		self.QUERY = ""
		self.DBQUERY_clean()
		
		
#-------------------------------------------------------------------

	def __del__(self):
		
		self.close()

#-------------------------------------------------------------------

	def close(self):
		
		self.conn.close()


#-------------------------------------------------------------------

	def DB_SELECT_ALL(self, table, count=False):
		
		self.QUERY = "SELECT * FROM '" + table + "';"
		self.cur.execute(self.QUERY)
		results = self.cur.fetchall()
		
		if count:
			return len(results)
		else:
			return results


#-------------------------------------------------------------------

	def assets_select_all(self):
			
		query_result = []
		
		rows = self.DB_SELECT_ALL("Assets")
		
		for r in rows:
			
			data_model = {
				"Id":0,
				"InternalId":"",
				"Name":"",
				"Category":"",
				"Value":0.0,
				"Dependences":"",
				"Updated":"",
				"Reviewed":"",
				"Iteration":"",
				"Scope":"",
				"Comments":"",		
			}
			
			data_model["Id"] = int(r[0])
			data_model["InternalId"] = r[1]
			data_model["Name"] = r[2]
			data_model["Category"] = r[3]
			data_model["Value"] = float(r[4])
			data_model["Dependences"] = r[5]
			data_model["Updated"] = r[6]
			data_model["Reviewed"] = r[7]
			data_model["Iteration"] = r[8]
			data_model["Scope"] = r[9]
			data_model["Comments"] = r[10]

			query_result.append(data_model)

		return query_result


#-------------------------------------------------------------------

	def riskcatalog_select_all(self):
		
		query_result = []
		
		rows = self.DB_SELECT_ALL("RiskCatalog")
		
		for r in rows:
			
			data_model = self.applicability_data_model.copy()

			data_model["Id"]=int(r[0])
			data_model["InternalId"]=r[1]
			data_model["Name"]=r[2]
			data_model["Description"]=r[3]
			data_model["Applicability"]=r[4]
			data_model["Dims"]=r[5]
			data_model["Active"]=int(r[6])
			data_model["Updated"]=r[7]
			data_model["Reviewed"]=r[8]
			data_model["Iteration"]=r[9]
			data_model["Comments"]=r[10]

			query_result.append(data_model)

		return query_result
		
		
#-------------------------------------------------------------------

	def applicability_insert(self, data_model):
		
		data_model['Id'] = 'Null'
		
		query = "INSERT INTO Applicability("
		for dm in data_model:
			query += dm + ","
		query = query[:-1] + ") VALUES ("
		for dm in data_model:
			if isinstance(data_model[dm], int) or isinstance(data_model[dm], float) or dm=='Id':
				query += str(data_model[dm]) + ","
			else:
				query += "'" + str(data_model[dm]) + "',"
		query = query[:-1] + ");"
			
		self.cur.execute(query)
		self.conn.commit()

		return self.cur.lastrowid		


#-------------------------------------------------------------------

	def applicability_update(self, data_model):
	
		sql1 = "UPDATE Applicability "
		sql2="SET "
		sql3=" WHERE Id='" + str(data_model['Id']) + "'"
		
		for dm in data_model:
			if not dm == 'Id':
				sql2+= dm + "='" + str(data_model[dm]) + "', "
		sql2=sql2[:-2]
		
		query = sql1 + sql2 + sql3
		self.cur.execute(query)
		self.conn.commit()		

		return data_model
	
	
#-------------------------------------------------------------------

	def TABLE_insert(self, table, data_model, comm=False, debugging=False):	

		data_model['Id'] = 'Null'
		
		query = "INSERT INTO " + table + "("
		for dm in data_model:
			query += dm + ","
		query = query[:-1] + ") VALUES ("
		for dm in data_model:
			if isinstance(data_model[dm], int) or isinstance(data_model[dm], float) or dm=='Id':
				query += str(data_model[dm]) + ","
			else:
				query += "'" + str(data_model[dm]) + "',"
		query = query[:-1] + ");"

		if debugging:
			print(query)			

		self.cur.execute(query)
		
		if comm:
			self.conn.commit()	

		return self.cur.lastrowid


#-------------------------------------------------------------------

	def TABLE_update(self, table, data_model, comm=False, debugging=False):
	
		sql1 = "UPDATE " + table + " "
		sql2="SET "
		sql3=" WHERE Id='" + str(data_model['Id']) + "'"
		
		for dm in data_model:
			if not dm == 'Id':
				sql2+= dm + "='" + str(data_model[dm]) + "', "
		sql2=sql2[:-2]
		
		query = sql1 + sql2 + sql3
		self.cur.execute(query)
		if comm:
			self.conn.commit()	

		if debugging:
			print(query)

		return data_model
	
	
#-------------------------------------------------------------------

	def risk1_update(self, data_model, comm=True):
	
		sql1 = "UPDATE Risk1 "
		sql2="SET "
		sql3=" WHERE Id='" + str(data_model['Id']) + "'"
		
		for dm in data_model:
			if not dm == 'Id':
				sql2+= dm + "='" + str(data_model[dm]) + "', "
		sql2=sql2[:-2]
		
		query = sql1 + sql2 + sql3
		self.cur.execute(query)
		if comm:
			self.conn.commit()

		return data_model
	
	
#-------------------------------------------------------------------

	def risk1_insert(self, data_model):
		
		data_model['Id'] = 'Null'
		
		query = "INSERT INTO Risk1("
		for dm in data_model:
			query += dm + ","
		query = query[:-1] + ") VALUES ("
		for dm in data_model:
			if isinstance(data_model[dm], int) or isinstance(data_model[dm], float) or dm=='Id':
				query += str(data_model[dm]) + ","
			else:
				query += "'" + str(data_model[dm]) + "',"
		query = query[:-1] + ");"
			
		self.cur.execute(query)
		self.conn.commit()

		return self.cur.lastrowid
		
		
#-------------------------------------------------------------------

	def risk2_insert(self, data_model):
		
		data_model['Id'] = 'Null'
		
		query = "INSERT INTO Risk2("
		for dm in data_model:
			query += dm + ","
		query = query[:-1] + ") VALUES ("
		for dm in data_model:
			if isinstance(data_model[dm], int) or isinstance(data_model[dm], float) or dm=='Id':
				query += str(data_model[dm]) + ","
			else:
				query += "'" + str(data_model[dm]) + "',"
		query = query[:-1] + ");"
			
		self.cur.execute(query)
		self.conn.commit()

		return self.cur.lastrowid


#-------------------------------------------------------------------

	def risk3_insert(self, data_model):
		
		data_model['Id'] = 'Null'
		
		query = "INSERT INTO Risk3("
		for dm in data_model:
			query += dm + ","
		query = query[:-1] + ") VALUES ("
		for dm in data_model:
			if isinstance(data_model[dm], int) or isinstance(data_model[dm], float) or dm=='Id':
				query += str(data_model[dm]) + ","
			else:
				query += "'" + str(data_model[dm]) + "',"
		query = query[:-1] + ");"
			
		self.cur.execute(query)
		self.conn.commit()

		return self.cur.lastrowid
		
		
#-------------------------------------------------------------------

	def risk2_truncate(self):
		
		query = "DELETE FROM Risk2;"
		self.cur.execute(query)
		self.conn.commit()	


#-------------------------------------------------------------------

	def risk3_truncate(self):
		
		query = "DELETE FROM Risk3;"
		self.cur.execute(query)
		self.conn.commit()	


#-------------------------------------------------------------------

	def risk2_update(self, data_model):
	
		sql1 = "UPDATE Risk2 "
		sql2="SET "
		sql3=" WHERE Id='" + str(data_model['Id']) + "'"
		
		for dm in data_model:
			if not dm == 'Id':
				sql2+= dm + "='" + str(data_model[dm]) + "', "
		sql2=sql2[:-2]
		
		query = sql1 + sql2 + sql3
		self.cur.execute(query)
		self.conn.commit()		

		return data_model
	

#-------------------------------------------------------------------

	def risk3_update(self, data_model, comm=True):
	
		sql1 = "UPDATE Risk3 "
		sql2="SET "
		sql3=" WHERE Id='" + str(data_model['Id']) + "'"
		
		for dm in data_model:
			if not dm == 'Id':
				sql2+= dm + "='" + str(data_model[dm]) + "', "
		sql2=sql2[:-2]
		
		query = sql1 + sql2 + sql3
		self.cur.execute(query)
		if comm:
			self.conn.commit()		

		return data_model
	
	
#-------------------------------------------------------------------	
#-------------------------------------------------------------------

	def applicability_select_all(self, count=False):

		query_result = []

		rows = self.DB_SELECT_ALL("Applicability")
		
		for r in rows:
			
			data_model = self.applicability_data_model.copy()

			data_model["Id"]=int(r[0])
			data_model["AssetId"]=int(r[1])
			data_model["RiskId"]=int(r[2])
			data_model["Applicability"]=r[3]
			data_model["Updated"]=r[4]
			data_model["Reviewed"]=r[5]
			data_model["Iteration"]=r[6]
			data_model["Scope"]=r[7]
			data_model["Comments"]=r[8]			

			query_result.append(data_model)
		
		if count:
			return len(query_result)

		else:
			return query_result

#-------------------------------------------------------------------

	def common_select_all(self, count=False):

		query_result = []

		rows = self.DB_SELECT_ALL("Common")
		
		for r in rows:
			
			data_model = self.common_data_model.copy()

			data_model["Id"]=int(r[0])
			data_model["Register"]=r[1]
			data_model["Value"]=r[2]
			
			query_result.append(data_model)
		
		if count:
			return query_result

		else:
			return len(query_result)
		


#-------------------------------------------------------------------

	def DB_COUNT_ALL(self, table):
		
		return self.DB_SELECT_ALL(table, True)


#-------------------------------------------------------------------

	def DB_COMMIT(self):
		
		return self.conn.commit()	


#-------------------------------------------------------------------

	def DBQUERY_clean(self):
		
		self.DB_QUERY = {'table':'', 'filters':[], 'order':""}


#-------------------------------------------------------------------

	def DBQUERY_table_set(self, table):
		
		self.DBQUERY_clean()
		self.DB_QUERY['table'] = table


#-------------------------------------------------------------------

	def DBQUERY_order_set(self, order):
		
		self.DB_QUERY['order'] = order


#-------------------------------------------------------------------

	def DBQUERY_filter_set(self, bdfilter):

		self.DB_QUERY['filters'].append(bdfilter)
		
		
#-------------------------------------------------------------------

	def DBQUERY_query(self, count=False, debugging=False):

		query = ""
		query_result = []
		first = True
	
		query = "SELECT * FROM '" + self.DB_QUERY['table'] + "'"

		for q in self.DB_QUERY['filters']:
				
			if first:
				first = False
				query += " WHERE " + str(q)
					
			else:
				query += " AND " + str(q)

		if not self.DB_QUERY["order"] == "":
			query += " " + self.DB_QUERY["order"]

		query += ";"

		self.QUERY = query
		
		if debugging:
			print(self.QUERY)

		self.cur.execute(self.QUERY)
		raw_results = self.cur.fetchall()
		
		if count:
			return len(raw_results)

		else:

			data_template = self.TRANSLATION_data_model[self.DB_QUERY['table']]
			
			for r in raw_results:
				data_model = data_template.copy()
				counter = 0
				
				for dt in data_template:
					data_model[dt]=r[counter]
					counter += 1
				query_result.append(data_model)
			
			return query_result		
		

#-------------------------------------------------------------------

