import socket
import threading

from packet import Packet
from lib_colors import *
from table import Table
from debugger import Debugger
import globals


class Server:
    def __init__(self,port,annport):
        hostname = socket.gethostname()
        print(hostname)
        local_ip = socket.gethostbyname(hostname)
        self.host = local_ip
        self.port = port
        self.annport = annport
    
        self.table = Table()
    
    
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
            if packet.type == globals.DATA:
                pass
                

                
    def start(self):
        datathread = threading.Thread(target=self.portListener,args=("portlistener",))
        datathread.start()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while True:       
            print("[ANNOUNCEMENT PORT] Listening at " + self.host)
            self.socket.listen()
            conn, addr = self.socket.accept()
            
            x = threading.Thread(target=self.dataListener, args=("listener",conn,addr))
            x.start()