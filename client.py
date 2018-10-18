import socket
import sys
import threading
from datetime import datetime
import sys

class ServerClient():
    commandList = [("quit", "Disconnects from the server. Ctrl+C combination has the same effect"),
                    ("connect","Attempt to connect to the server"),
                    ("disconnect","Disconnect from the server"),
                    ]

    def __init__(self, hostAddr, port):
        self.initSocket(hostAddr,port)
        self.connected = False

        res = self.initThreads()

        self.connect()
        #Check if threads are initiated correctly
        if res != 0 :
            return

        #Run client loop
        self.clientLoop()

    def initSocket(self, hostAddr, port):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = hostAddr
        self.port = port

    def initThreads(self):
        #Server listener thread
        self.t = threading.Thread(target=self.listenToServer, args=(1024,"utf-8"))
        #User input listener thread
        self.it  = threading.Thread(target=self.listenToInput, args = ())

        self.t.setDaemon(True)
        self.it.setDaemon(True)

        #Start threads
        self.t.start()
        self.it.start()
        return 0

    def terminateThreads(self):
        self.it.do_run = False
        self.t.do_run = False


    def connect(self):
        #If host address and port are specified 
        if self.host!=None and self.port!=None:
            try:
                #Try to connect
                self.soc.connect((self.host, self.port))
            except Exception as e:
                #In case of failure print exception type
                if e.args[0] == 10061:
                    print("Can't reach server.")
                elif e.args[0] == 10056:
                    print("Can't connect. Socket is already occupied.")
                else:
                    print("Connection error: "+str(e))
                print("Please try again.(Type reconnect)")
                return
            #List all commands
            print("Client connected to the server. you can use following commands:")

            for command in ServerClient.commandList:
                print("\t"+command[0]+":"+command[1])
            print()
            #Let threads do their thing
            self.connected = True
        else:
            print("Default host and port are not specified")

    def sendMessage(self,message, encoding):
        try:
            #Try to send message
            self.soc.sendall(message.encode(encoding))
        except Exception as e:
            print("Message was not sent: " + str(e))

    #Checks if connection is still present
    def connectionIsDead(self):
        try:
            #Try to get server response
            self.soc.recv(1024)
        except:
            #Connection is dead
            return True

        return False
    
    def listenToServer(self,bufferSize, encoding):
        #Get current thread
        t = threading.currentThread()
        #if not terminated run listening loop
        while getattr(t, "do_run", True):
            if not self.connected:
                continue

            data = ""
            try:
                #Try to get server message
                data = self.soc.recv(bufferSize).decode(encoding)
            except Exception as e:
                #Terminate input listener thread
                self.connected = False
                self.closeConnection()
                print("Disconnected from server.")
                return

            #If message is not empty
            if data.strip():
                #Print server message
                print("Server message: " + data)

        #If thread terminated close connection
        self.closeConnection()
        return

    #Input listener thread method
    def listenToInput(self):
        inp = ""
        t = threading.currentThread()
        #While not terminated
        while getattr(t, "do_run", True):
            #Read user input
            inp = sys.stdin.readline()
            print()
            #Check if input is a command
            if "connect" == inp.strip():
                if self.connected:
                    print("Already connected to the server")
                    continue 
                self.connect()
                continue
            if "disconnect" == inp.strip():
                if self.connected:
                    self.closeConnection()
                    self.connected = False
                    print("Disconnected from server")
                else:
                    print("You are already disconnected from server")
                continue
            if "quit" == inp.strip():
                self.closeConnection()
                self.connected = False
                self.terminateThreads()
                continue

            #Don't try to send user messages if not connected
            if not self.connected:
                print("You are currently disconnected from the server. Messages will not be sent")
                continue
            #If not a command send to the sever
            self.sendMessage(inp, "utf-8");
        return
        
    def closeConnection(self):
        #If connection is dead don't try to close it
        if not self.connected:
            return
        self.connected = False
        self.soc.send(b'--quit--')
        self.soc.close()
        self.initSocket(self.host,self.port)

    def clientLoop(self):
        try:
            #Let them run until user types quit or ctrl+C is pressed
            while self.it.isAlive():
                #Random code
                a = 42
        #Ctrl+c is pressed
        except KeyboardInterrupt:
            #Stop input thread
            self.closeConnection()
            self.terminateThreads()
        
#Example
def main():
    host = "127.0.0.1"
    port = 9090
    client = ServerClient(host, port)

main()

