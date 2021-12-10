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
        self.dataSocket.bind(AddressPortData)
        
        AddressPortAnn = (self.host,23456)
        self.announcementSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.announcementSocket.bind(AddressPortAnn)
        
        self.threads = []


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
    
    
    
    
    
    def announcementReceiverWorker(self,name,conn,download = False):
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
                        if download:
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
                                if self.vizinhos[ip][3] is None:
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
                                
                            
                            
                            
                    
                    
                    else:
                        print("não tenho rota ativa")

    
    
    
    
    
    def announcementWorker(self,name,download): 
 
        anThread = threading.Thread(target=self.announce)
        self.threads.append(anThread)
        anThread.daemon = True
        anThread.start()
    
        while True:
       
            if download and self.table.hasRoute():
                globals.printDebug(name,"Existe servidor")
                s = self.vizinhos[self.table.get_next_hop()][2]
                print("ip2: " + self.table.get_next_hop())
                s.sendall(Packet(type=4,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
                globals.printDebug(name,"sended ...")
            elif download and not self.table.hasRoute():
                globals.printDebug(name,"Não existe servidor")

            self.announcementSocket.listen()
            conn, addr = self.announcementSocket.accept()
            print('[announcementWorker] Connected by', addr)
            thread = threading.Thread(target=self.announcementReceiverWorker,args=("announcementReceiverWorker",conn,download,))
            self.threads.append(thread)
            thread.daemon = True
            thread.start()
            
    
    
                       
    def dataReceiverWorker(self,name,conn,download):
        while data:=conn.recv(1024):
            if data: 
                packet = Packet(bytes=data)
                if packet.type == globals.DATA: # Send from Server
                    if download:
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
          
                    
    
    
    def dataWorker(self,name,download):     
        while True:
            self.dataSocket.listen()
            conn, addr = self.dataSocket.accept()
            print('[dataWorker] Connected by', addr)
            datareceiver = threading.Thread(target=self.dataReceiverWorker,args=("dataReceiverWorker",conn,download,))
            self.threads.append(datareceiver)
            datareceiver.daemon = True
            datareceiver.start()
     
        
    
    def start(self, download=False):
        signal.signal(signal.SIGINT, self.signalINT_handler)
        
        announcementThread = threading.Thread(target=self.announcementWorker, args=("annoucementWorker",download,)) # 23456
        self.threads.append(announcementThread)
        announcementThread.daemon = True
        announcementThread.start()
        
        workerThread =threading.Thread(target=self.dataWorker,args=("Worker",download,)) # 65432
        self.threads.append(workerThread)
        workerThread.daemon = True
        workerThread.start()
         
        for i in self.threads:
            i.join()
         
            #inp = input("What to say: ")
            #while inp != "":
            #    s.sendall(bytes(inp,encoding='utf8'))
            #    inp = input("What to say: ")
#    def start(self)