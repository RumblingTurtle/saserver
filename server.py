import socket
import sys
import traceback
import threading
import sqlite3
import json

#TODO add threaded server console input commands
class Server:
	dbpath = ""

	def __init__(self,hostAddr, port, dbPath):
		self.host = hostAddr
		self.port = port
		Server.dbpath = dbPath

		self.initSocket()

		hostRes = self.bindHost()
		listenerRes = self.initConnectionListener()

		if hostRes+listenerRes==0:
			self.serverLoop()

		self.terminateConnectionListener()

	def terminateConnectionListener(self):
		self.connectionListenerThread.do_run = False

	def terminateAllUserSessions(self):
		for u in self.users:
			u.disconnect()

	def initConnectionListener(self):
		try:
			self.connectionListenerThread = threading.Thread(target= self.connectionListener)
			self.connectionListenerThread.setDaemon(True)
			self.connectionListenerThread.start()
		except Exception:
			print("Connection listener creation failed.")
			return -1
		return 0

	def initSocket(self):
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# SO_REUSEADDR flag tells the kernel to reuse a local socket
		# in TIME_WAIT state, without waiting for its natural timeout to expire
		self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print("Server socket initiated")

	def bindHost(self):
		if self.host != None and self.port!=None:		
			try:
				self.soc.bind((self.host, self.port))
			except Exception as e:
				print("Host binding failed. Error : " + str(e))
				return -1

		self.soc.listen(5)       # queue up to 5 requests
		print("Socket now listening")
		return 0

	def serverLoop(self):
		try:
			while True:
				a = 42
		except KeyboardInterrupt:
				self.terminateAllUserSessions()
				self.soc.close()

	class User():
		def __init__(self, ip, port, connection, bufferSize = 1024):
			self.ip = ip
			self.port = port
			self.connection = connection
			self.bufferSize = bufferSize
			self.is_active = True
			self.initInputThread()

		def initInputThread(self):
			try:
				self.t = threading.Thread(target=self.userInputThread)
				self.t.setDaemon(True)
				self.t.start()
			except Exception as e:
				print("Listener thread for user " + str(self.ip)+":"+str(self.port)+" failed to start: "+ str(e))

		def terminateInputThread(self):
			self.t.do_run = False

		def disconnect(self):
			self.is_active = False

		def userInputThread(self,max_buffer_size=1024):
			t = threading.currentThread()
			#if not terminated run listening loop
			while self.is_active and getattr(t, "do_run", True):
				#TODO add threads for receiving and processings
				client_input = self.receive_input()
				if "--quit--" in client_input:
					self.connection.send(b"OK")
					print("Client is requesting to quit")
					self.connection.close()
					print("Connection " + self.ip + ":" + self.port + " closed")
					self.is_active = False
				elif "checkuser" in client_input:
					payload = client_input.split(":")[1]
					username, password = payload.split("|")
					conn = sqlite3.connect(Server.dbpath)
					cursor = conn.cursor()
					sql = "SELECT * FROM control_operator WHERE login=?"
					cursor.execute(sql, [(username)])
					record = cursor.fetchone()
					recordpass = record[2]
					if recordpass == password:
						self.connection.send(b"OK")
					else:
						self.connection.send(b"NOT OK")
					print("Processed result: {}".format(client_input))
				elif "getDrivers" in client_input:
					result = []
					sql = "SELECT * FROM delivery_operator"
					conn = sqlite3.connect(Server.dbpath)
					cursor = conn.cursor()
					cursor.execute(sql)
					records = cursor.fetchall()
					for record in records:
						dId = record[0]
						name = record[3]
						surname = record[4]
						phone = record[6]
						lat = record[7]
						longt = record[8]
						result.append({"id":dId,"name":name,"surname":surname,"phone":phone,"lat":lat,"long":longt})
					self.connection.send(json.dumps(result, separators=(',',':')).encode("utf-8"))


		def receive_input(self):
			client_input = self.connection.recv(self.bufferSize)
			client_input_size = sys.getsizeof(client_input)

			if client_input_size > self.bufferSize:
				print("The input size is greater than expected {}".format(client_input_size))

			decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
			result = self.process_input(decoded_input)

			return result


		def process_input(self, input_str):
			print("Processing the input received from client " + self.ip +":" + self.port + " :")
			return str(input_str)

	def connectionListener(self):
		self.users = []
		t = threading.currentThread()
		while getattr(t, "do_run", True):
			connection, address = self.soc.accept()

			ip, port = str(address[0]), str(address[1])

			self.users.append(self.User(ip,port, connection))

			print("User connected " + ip + ":" + port)

def main():
	host = "127.0.0.1"
	port = 9090
	server = Server(host,port,"Transport Company DB.db") 

main()

