import socket
import threading

from packet import Packet
from lib_colors import *
from table import Table
from debugger import Debugger
import globals
import time


class Server:
    def __init__(self,port,annport):
        hostname = socket.gethostname()
        print(hostname)
        local_ip = socket.gethostbyname(hostname)
        self.host = local_ip
        self.port = port
        self.annport = annport
    
        self.table = Table()
        self.vizinhos = {}

    
#   Worker for thread
#   Listens for connections and decides what to do depending on type of the packet
    def portListener(self,name):
        self.annSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.annSocket.bind((self.host, self.annport))

     
        while True:
            self.annSocket.listen()
            conn, addr = self.annSocket.accept()
            print('[PORTLISTENER] Connected by', addr)
            data = conn.recv(1024)
            if not data:
                break
            packet = Packet(bytes=data)
            if packet.type == globals.ANNOUNCEMENT or packet.type == globals.ANNOUCEMENTANDGET:
                self.table.updateTable(self.host,addr[0],packet.payload)

                
    def dataListener(self,name,conn,addr):
        # Debugger
        printInfo("server","Initializing debugger ...")
        debugger = Debugger(self.table)
        debugger.start()
        printSuccess("debugger","Initialization sucessful")
        
        
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            packet = Packet(bytes=data)
            if packet.type == globals.REQUEST:
                globals.printDebug(name,"Updated to active")
                self.vizinhos[addr] = 1
            
                

    def sendData(self,name):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file = open("files/starwars.txt",'r')
        lines = file.readlines()
        output = ""
        LINES_PER_FRAME = 14
        DELAY = 0.67
        i = 0
        for line in lines:
           
            if i < LINES_PER_FRAME:
                output = output + line + "\n"
                i += 1
            else:
                bytePayload = Packet(type=3,ip=self.host,port=65432,payload=output).packetToBytes()
                for ip in self.vizinhos:
                    if self.vizinhos[ip] == 1:
                        s.connect((ip,65432))
                        print("[" + name + "] connected")
                        s.sendall(bytePayload)
                        print("[" + name + "] sended ...")        
                
                
                output = ""
                i = 0
                
                time.sleep(DELAY)
        
        s.close()

        pass
                
                
    def start(self):
        datathread = threading.Thread(target=self.portListener,args=("portlistener",))
        datathread.start()
        
        sendDataThread = threading.Thread(target=self.sendData,args=("sendData",))
        sendDataThread.start()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while True:       
            print("[ANNOUNCEMENT PORT] Listening at " + self.host)
            self.socket.listen()
            conn, addr = self.socket.accept()
            print("here")
            x = threading.Thread(target=self.dataListener, args=("listener",conn,addr))
            x.start()