import socket
import threading

from packet import Packet
from lib_colors import *
from table import Table
from debugger import Debugger



ANNOUNCEMENT = '1'
class Server:
    def __init__(self,port):
        hostname = socket.gethostname()
        print(hostname)
        local_ip = socket.gethostbyname(hostname)
        self.host = local_ip
        self.port = port
    
        self.table = Table()
    
    
#   Worker for thread
#   Listens for connections and decides what to do depending on type of the packet
    def listener(self,name,conn,addr):
        
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
            if packet.type == ANNOUNCEMENT:
                self.table.updateTable(self.host,addr[0],packet.payload)
                
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while True:       
            print("Listening at " + self.host)
            self.socket.listen()
            conn, addr = self.socket.accept()
            
            x = threading.Thread(target=self.listener, args=("listener",conn,addr))
            x.start()