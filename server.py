import socket
import threading
import signal

from packet import Packet
from table import Table
from debugger import Debugger
import globals
import time

import sys

class Server:
    def __init__(self,port,annport,params):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.host = local_ip
        self.port = port
        self.annport = annport
    
        """
        "ip":[0,0,sA,sD]           desligado, rota inativa, Socket announcement, Socket Data
        "ip2":[1,0,sA,sD]          ligado, rota inativa, Socket announcement, Socket Data
        etc...
        
        """
        self.vizinhos = {}
        for name in params:
            ip = socket.gethostbyname(name)
            print(ip)
            self.vizinhos[ip] = [0,0,None,None]
        self.annSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.annSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.threads = []
            
      
    
    def signalINT_handler(self,signum, frame):
        try:
            self.annSocket.close()
            for ip in self.vizinhos:
            
                if self.vizinhos[ip][2] is not None:
                    self.vizinhos[ip][2].close()
                if self.vizinhos[ip][3] is not None:
                    self.vizinhos[ip][3].close()
            
        except socket.error as exc:
            print(f"Caught exception socket.error : {exc}")
        print("exiting ...")    
        sys.exit(0)
       
    
    def announce(self):
        for ip in self.vizinhos:
            print("found 1 ip ...") 
            print(ip)
            try:
                self.vizinhos[ip][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.vizinhos[ip][3] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                self.vizinhos[ip][2].connect((ip,23456))
                print("connected Announcement")
                self.vizinhos[ip][3].connect((ip,65432))
                print("connected Datas")
                
                self.vizinhos[ip][0] = 1
                self.vizinhos[ip][1] = 0
                self.vizinhos[ip][2].sendall(Packet(type=globals.ANNOUNCEMENT,ip_origem=self.host,ip_destino=ip,port=23456,payload="0").packetToBytes())
                print("sended ...")
                #self.vizinhos[ipv][2].close()
            
            except socket.error as exc:
                print(f"Caught exception socket.error : {exc}")

    
    
    def serverConnWorker(self,name,conn):
        while data := conn.recv(1024):
            if not data:
                break
            packet = Packet(bytes=data)
            print("\n\n")
            packet.printa()
            print("\n\n")
            ip = packet.getIpOrigem()
            if packet.type == globals.IM_HERE:
                print(self.vizinhos)
                self.vizinhos[ip][2].connect((ip,23456))
                print("connected Announcement")
                self.vizinhos[ip][3].connect((ip,65432))
                print("connected Datas")
                
                self.vizinhos[ip][0] = 1
                self.vizinhos[ip][1] = 0
                self.vizinhos[ip][2].sendall(Packet(type=globals.ANNOUNCEMENT,ip_origem=self.host,ip_destino=ip,port=23456,payload="0").packetToBytes())
                print("sended ...")
            elif packet.type == globals.REQUEST:
                globals.printDebug(name,"Updated to active")
                self.vizinhos[ip][1] = 1
            elif packet.type == globals.STOP:
                globals.printDebug(name,"Updated to inactive")
                self.vizinhos[ip][1] = 0
    
    
#   Worker for thread
#   Listens for connections and decides what to do depending on type of the packet    
    def serverListenerWorker(self,name):     
        self.announce()
        
        
        self.annSocket.bind((self.host, self.annport))

        while True:
            self.annSocket.listen()
            conn, addr = self.annSocket.accept()
            print('[PORTLISTENER] Connected by', addr)
            x = threading.Thread(target=self.serverConnWorker,args=("serverConnWorker",conn,))
            self.threads.append(x)
            x.daemon = True
            x.start()
            

            
            
         

    def sendData(self,name):
        file = open("files/starwars.txt",'r')
        lines = file.readlines()
        output = ""
        LINES_PER_FRAME = 14
        DELAY = 0.47
        i = 0
        for line in lines:
           
            if i < LINES_PER_FRAME:
                output = output + line
                i += 1
            else:
                bytePayload = Packet(type=3,ip_origem=self.host,ip_destino="0.0.0.0",port=65432,payload=output).packetToBytes()
                for ip in self.vizinhos:
                    if self.vizinhos[ip][0] == 1 and self.vizinhos[ip][1] == 1:
                        self.vizinhos[ip][3].sendall(bytePayload)
                        print("[" + name + "] sended ...")
                     
                output = ""
                i = 0
                
                time.sleep(DELAY)
          
                
    def start(self):
        signal.signal(signal.SIGINT, self.signalINT_handler)
        
        datathread = threading.Thread(target=self.serverListenerWorker,args=("serverListenerWorker",))
        self.threads.append(datathread)
        datathread.daemon = True
        datathread.start()
        
        
        sendDataThread = threading.Thread(target=self.sendData,args=("sendData",))
        self.threads.append(sendDataThread)
        sendDataThread.daemon = True
        sendDataThread.start()
        
       
        
        
        print("[Server] Listening at " + self.host)
        
        for i in self.threads:
            i.join()
            
        
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while True:       
            print("[ANNOUNCEMENT PORT] Listening at " + self.host)
            self.socket.listen()
            conn, addr = self.socket.accept()
            print("here")
            x = threading.Thread(target=self.dataListener, args=("listener",conn,addr))
            x.start()
        """