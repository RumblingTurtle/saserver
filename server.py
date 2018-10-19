import socket
import sys
import traceback
import threading

#TODO run user routines in seperate threads, add server console input commands(store user info for listing and abortion)

class Server:
	def __init__(self,hostAddr, port):
		self.host = hostAddr
		self.port = port

		self.initSocket()
		res = self.bindHost()

		connectionThread = threading.Thread(target= self.connectionListener)
		connectionThread.setDaemon(True)

		connectionThread.start()
		self.serverLoop()

	def terminateAllUserSessions(self):
		for t in self.userThreads:
			t.do_run = False


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

	def serverLoop(self):
		try:
			while True:
				a = 42
		except KeyboardInterrupt:
				self.terminateAllUserSessions()
				self.soc.close()

	def connectionListener(self):
		self.userThreads = []
		while True:
			connection, address = self.soc.accept()

			ip, port = str(address[0]), str(address[1])

			print("User connected " + ip + ":" + port)
			try:
				t = threading.Thread(target=self.client_thread, args=(connection, ip, port))
				t.setDaemon(True)
				self.userThreads.append(t)
				self.userThreads[-1].start()
			except Exception as e:
				print("Listener thread for user " + str(address[0])+":"+str(address[0])+" failed to start: "+ str(e))

	def client_thread(self,connection, ip, port, max_buffer_size=1024):
		is_active = True
		t = threading.currentThread()
		#if not terminated run listening loop
		while is_active and getattr(t, "do_run", True):
			#TODO add threads for receiving and processings
			client_input = self.receive_input(connection, max_buffer_size)

			if "--quit--" in client_input:
				print("Client is requesting to quit")
				connection.close()
				print("Connection " + ip + ":" + port + " closed")
				is_active = False
			else:
				print("Processed result: {}".format(client_input))

	def receive_input(self, connection, max_buffer_size):
		client_input = connection.recv(max_buffer_size)
		client_input_size = sys.getsizeof(client_input)

		if client_input_size > max_buffer_size:
			print("The input size is greater than expected {}".format(client_input_size))

		decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
		result = self.process_input(decoded_input)

		return result


	def process_input(self, input_str):
		print("Processing the input received from client")
		return str(input_str)

def main():
	host = "127.0.0.1"
	port = 9090
	server = Server(host,port)        
main()

