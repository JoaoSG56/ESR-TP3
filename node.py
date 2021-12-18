import socket
import threading
import time
import sys
import signal

from packet import Packet
from table import Table

import globals


class Node:
    def __init__(self,params):
        self.table = Table()
        """
        table:
        {
            "primaria":
                {
                    "next_hop":"$ip",
                    "cost":"$cost",
                },
            "secundaria":
                {
                    "next_hop":"$ip",
                    "cost":"$cost",
                }
        }
        
        vizinhos:
        {
            "ip":[0,0,sA,sD]           desligado, rota inativa, Socket announcement, Socket Data
            "ip2":[1,0,sA,sD]          ligado, rota inativa, Socket announcement, Socket Data
            etc...
        }
        
        """
        self.vizinhos = {}
        for name in params:
            ip = socket.gethostbyname(name)
            print(ip)
            self.vizinhos[ip] = [0,0,None,None]
            
        self.host = socket.gethostbyname(socket.gethostname())
    
        
        AddressPortData = (self.host,65432)
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.dataSocket.bind(AddressPortData)
        
        AddressPortAnn = (self.host,23456)
        self.announcementSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.announcementSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.announcementSocket.bind(AddressPortAnn)
        
        self.threads = []

        self.downloading = False

    def signalINT_handler(self,signum, frame):
        try:
            for ip in self.vizinhos:
            
                if self.vizinhos[ip][2] is not None:
                    self.vizinhos[ip][2].close()
                if self.vizinhos[ip][3] is not None:
                    self.vizinhos[ip][3].close()
            self.dataSocket.close()
            self.announcementSocket.close()
        except socket.error as exc:
            print(f"Caught exception socket.error : {exc}")
        print("exiting ...")    
        sys.exit(0)
       

    def hasFluxo(self):
        for ip in self.vizinhos:
            if self.vizinhos[ip][0] and self.vizinhos[ip][1]:
                return True
        return False

        
    def announce(self):
        time.sleep(1)
        for ip in self.vizinhos:
            print("found 1 ip ...") 
            print(ip)
            try:
                if self.vizinhos[ip][2] is None:
                    self.vizinhos[ip][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.vizinhos[ip][2].connect((ip,23456))
                print("connected Announcement")
                
                self.vizinhos[ip][0] = 1
                self.vizinhos[ip][1] = 0
                self.vizinhos[ip][2].sendall(Packet(type=globals.IM_HERE,ip_origem=self.host,ip_destino=ip,port=23456,payload="").packetToBytes())
                print("sended ...")
                #self.vizinhos[ipv][2].close()
            
            except socket.error as exc:
                print(f"[PORTA 23456] Caught exception socket.error : {exc}")
                
            

    # ip -> ip de onde não é para mandar
    def announceChange(self,ipN,cost):
        for ip in self.vizinhos:
            if self.vizinhos[ip][0] and ip != ipN:
                # announce
                self.vizinhos[ip][2].sendall(Packet(type=globals.ANNOUNCEMENT,ip_origem=self.host,ip_destino=ip,port=23456,payload=str(cost)).packetToBytes())
    
    
    
    
    
    def announcementReceiverWorker(self,name,conn):
        while data := conn.recv(1024):
            if data: 
                packet = Packet(bytes=data)
                print("\n\n")
                packet.printa()
                print("\n\n")
                ip = packet.getIpOrigem()
                if packet.type == globals.IM_HERE:
                    if ip in self.vizinhos:
                        self.vizinhos[ip][0] = 1
                        if self.vizinhos[ip][2] is None:
                            self.vizinhos[ip][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.vizinhos[ip][2].connect((ip,23456))
                        globals.printDebug(name,"connected")
                        if self.table.hasRoute():
                            cost = self.table.getRouteCost()
                            if cost is not None:
                                print("tem cost: " + str(cost))
                                
                                
                                self.vizinhos[ip][2].sendall(Packet(type=2,ip_origem=self.host,ip_destino=ip,port=23456,payload=str(cost)).packetToBytes())
                                globals.printDebug(name,"sended ...")
                            else:
                                globals.printDebug("annWorker","cost é none")
                    else:
                        print("algo está mal")
                    
                    
                elif packet.type == globals.ANNOUNCEMENT:
                    globals.printDebug("annworker","Type announcement")
                    changed = self.table.updateTable(ip,int(packet.getPayload())+1)
                    if changed == 1:
                        # anuncia a todos
                        
                        ## Se rota melhor então muda a cena
                        if self.downloading:
                            next = self.table.get_next_hop()
                            if self.vizinhos[next][0]:
                                
                                try:
                                    if self.hasFluxo():
                                        globals.printDebug(name,"tem fluxo")
                                    else:
                                        globals.printDebug(name,"não tem fluxo")
                                        self.vizinhos[next][2].sendall(Packet(type=4,ip_origem=self.host,ip_destino=next,port=23456,payload="").packetToBytes())
                                        globals.printDebug(name,"sended ...")
                                    
                                except socket.error as exc:
                                    print(f"[PORTA 65432] Caught exception socket.error : {exc}")
                        globals.printDebug("annworker","mudou a rota primária")
                        self.announceChange(ip,self.table.getRouteCost())

                elif packet.type == globals.REQUEST:
                    # request
                    if self.table.hasRoute():
                        print("tenho rota ativa")
                        # request Server
                        next = self.table.get_next_hop()
                        if self.vizinhos[next][0]:
                            
                            try:
                                
                                self.vizinhos[ip][3] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                self.vizinhos[ip][3].connect((ip,65432))
                                print("connected Datas")
                                
                                s = self.vizinhos[next][2]

                                if self.hasFluxo():
                                    globals.printDebug(name,"tem fluxo")
                                    self.vizinhos[ip][1] = 1
                                else:
                                    s.sendall(Packet(type=4,ip_origem=self.host,ip_destino=next,port=23456,payload="").packetToBytes())
                                    globals.printDebug(name,"sended ...")
                                    self.vizinhos[ip][1] = 1
                                
                            except socket.error as exc:
                                print(f"[PORTA 65432] Caught exception socket.error : {exc}")
                elif packet.type == globals.STOP:
                    # stop
                    self.vizinhos[packet.getIpOrigem()][1] = 0 # rota inativa
                    self.vizinhos[packet.getIpOrigem()][3].close()
                    if not self.hasFluxo():
                        globals.printDebug(name,"Existe servidor")
                        s = self.vizinhos[self.table.get_next_hop()][2]
                        print("ip2: " + self.table.get_next_hop())
                        s.sendall(Packet(type=globals.STOP,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
                        globals.printDebug(name,"sended ...")
                    
                            
                            
                            
                    
                    
                    else:
                        print("não tenho rota ativa")

    
    
    
    
    
    def announcementWorker(self,name): 
 
        anThread = threading.Thread(target=self.announce)
        self.threads.append(anThread)
        anThread.daemon = True
        anThread.start()
    
        while True:

            self.announcementSocket.listen()
            conn, addr = self.announcementSocket.accept()
            print('[announcementWorker] Connected by', addr)
            thread = threading.Thread(target=self.announcementReceiverWorker,args=("announcementReceiverWorker",conn,))
            self.threads.append(thread)
            thread.daemon = True
            thread.start()
            
    
    
                       
    def dataReceiverWorker(self,name,conn):
        while data:=conn.recv(1024):
            if data: 
                packet = Packet(bytes=data)
                if packet.type == globals.DATA: # Send from Server
                    if self.downloading:
                        # Caso haja packets com o mesmo id, remover repetidos e cancelar rota alternativa
                        
                        print(packet.getPayload(),end='')
                    for ip in self.vizinhos:
                        if self.vizinhos[ip][1] == 1:
                            globals.printDebug("dataWorker","found rota ativa ...")
                            self.vizinhos[ip][3].sendall(data)
                            globals.printDebug("dataWorker","sended ...")
                            
                else:
                    print("WHAAAAAAAAAAAAAT?")
                    break
        print("SAI CARALHOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
          
                    
    
    
    def dataWorker(self,name):     
        while True:
            self.dataSocket.listen()
            conn, addr = self.dataSocket.accept()
            print('[dataWorker] Connected by', addr)
            datareceiver = threading.Thread(target=self.dataReceiverWorker,args=("dataReceiverWorker",conn,))
            self.threads.append(datareceiver)
            datareceiver.daemon = True
            datareceiver.start()
     
        
    def inputWorker(self,name):
        while True:
            inp = input("node>> ")
            if inp == "help":
                print("commands:\ndownload | stop")
            elif inp == "download":
                if not self.downloading:
                    if self.table.hasRoute():
                        globals.printDebug(name,"Existe servidor")
                        s = self.vizinhos[self.table.get_next_hop()][2]
                        print("ip2: " + self.table.get_next_hop())
                        s.sendall(Packet(type=globals.REQUEST,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
                        globals.printDebug(name,"sended ...")
                        self.downloading = True
                    else:
                        globals.printDebug(name,"No server available")
            elif inp == "stop":
                if self.downloading:
                    if self.table.hasRoute():
                        globals.printDebug(name,"Existe servidor")
                        s = self.vizinhos[self.table.get_next_hop()][2]
                        print("ip2: " + self.table.get_next_hop())
                        s.sendall(Packet(type=globals.STOP,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
                        globals.printDebug(name,"sended ...")
                        self.downloading = False
                    else:
                        globals.printDebug(name,"não devia entrar aqui")

        
    
    
    def start(self):
        signal.signal(signal.SIGINT, self.signalINT_handler)
        
        announcementThread = threading.Thread(target=self.announcementWorker, args=("annoucementWorker",)) # 23456
        self.threads.append(announcementThread)
        announcementThread.daemon = True
        announcementThread.start()
        
        workerThread =threading.Thread(target=self.dataWorker,args=("Worker",)) # 65432
        self.threads.append(workerThread)
        workerThread.daemon = True
        workerThread.start()
        
        inputThread = threading.Thread(target=self.inputWorker,args=("inputThread",))
        self.threads.append(inputThread)
        inputThread.daemon=True
        inputThread.start()
         
        for i in self.threads:
            i.join()
         
            #inp = input("What to say: ")
            #while inp != "":
            #    s.sendall(bytes(inp,encoding='utf8'))
            #    inp = input("What to say: ")
#    def start(self)