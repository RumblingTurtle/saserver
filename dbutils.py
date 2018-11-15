import psycopg2
dbname = "transport_company_db"
user = "postgres"
host = "transport-company-db.cos8isyuakyn.us-east-2.rds.amazonaws.com"
port = "5432"
passw = "user1234"

def checkOperator(login,password):
	conn = psycopg2.connect("dbname={} user={} password={} host={} port={}".format(dbname,user,passw,host,port))
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM public.operator WHERE login='{}'".format(login))
	userData = cursor.fetchone()
	if userData == None:
		return
	recordpass = userData[2]
	conn.close()
	if recordpass == password:
		return True
	else:
		return False

def getDrivers():
	conn = psycopg2.connect("dbname={} user={} password={} host={} port={}".format(dbname,user,passw,host,port))
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM public.delivery_operator")
	records = cursor.fetchall()
	result = []
	conn.close()
	for record in records:
		dId = record[0]
		name = record[3]
		surname = record[4]
		lat = record[6][0]
		longt = record[6][1]
		result.append({"id":dId,"name":name,"surname":surname,"lat":lat,"long":longt})
	return result

def getWarehouses():
	conn = psycopg2.connect("dbname={} user={} password={} host={} port={}".format(dbname,user,passw,host,port))
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM public.warehouses")
	records = cursor.fetchall()
	result = []
	conn.close()
	for record in records:
		wId = record[1]
		desc = record[0]
		lat = record[3]
		longt = record[2]
		result.append({"id":wId,"lat":lat,"long":longt,"desc":desc})
	return result

def getOrders():
	conn = psycopg2.connect("dbname={} user={} password={} host={} port={}".format(dbname,user,passw,host,port))
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM public.order WHERE status!='DENIED' LIMIT 10")
	records = cursor.fetchall()
	result = []
	cursor.execute("SELECT address_text,id FROM address")
	addrs = cursor.fetchall()
	conn.close()
	for record in records:
		oId = record[0]
		rAddressId = record[1]
		sAddressId = record[2]

		sAddress=""
		rAddress=""

		for address,aid in addrs:
			if aid == int(rAddressId):
				rAddress=address
			if aid == int(sAddressId):
				sAddress=address	

		receiverId = record[3]
		senderId =  record[4]
		status = record[5]
		note = record[6]
		sendDate = record[8].strftime("%Y-%m-%d")
		expectedDeliveryDate = record[9].strftime("%Y-%m-%d")
		path = record[10]
		carrier = record[12]

		result.append({"id":oId,"rAddress":rAddress \
			,"sAddress":sAddress,"receiverId":receiverId,"senderId":senderId \
			,"status":status,"note":note,"sendDate":sendDate,"expectedDeliveryDate":expectedDeliveryDate \
			,"path":path,"carrier":carrier})
	return result

def setOrderRoute(oid,route):
	conn = psycopg2.connect("dbname={} user={} password={} host={} port={}".format(dbname,user,passw,host,port))
	cursor = conn.cursor()
	cursor.execute("UPDATE public.order SET path='"+route+"',status='APPROVED' WHERE id="+oid)
	conn.commit()
	conn.close()

def denyOrder(oid):
	conn = psycopg2.connect("dbname={} user={} password={} host={} port={}".format(dbname,user,passw,host,port))
	cursor = conn.cursor()
	cursor.execute("UPDATE public.order SET status='DENIED' WHERE id="+oid)
	conn.commit()
	conn.close()
