import socket
import threading

from packet import Packet
from table import Table

import globals


class Node:
    def __init__(self,params):
        self.table = Table(params)
        """
        table:
        {
            "ip":
                {
                "next_hop":"$ip",
                "port":"$port",
                "announcement_port":"$annport",
                "cost":"$cost",
                "active":"False"
                }
        }
        
        vizinhos:
        {
            "ip":0,           inativa
            "ip2":1,          ativa
            etc...
        }
        
        """
        self.vizinhos = {}
        for ip in params:
            print("vizinho")
            self.vizinhos[ip] = 0
            
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print("local ip: " + local_ip)
        self.host = local_ip
        print(self.host)
        
        AddressPortData = (self.host,65432)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(AddressPortData)
        
        AddressPortAnn = (self.host,23456)
        self.annoucementSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.annoucementSocket.bind(AddressPortAnn)
        print(self.annoucementSocket)

        print(self.table.value)
        
    def announce(self,type=2,addr = None):
        if addr is not None:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((addr,23456))
                    print("connected")
                    s.sendall(Packet(type=type,ip=addr,port=23456,payload=self.table.table).packetToBytes())
                    print("sended ...")
                    s.close()
            except socket.error as exc:
                print(f"Caught exception socket.error : {exc}")
            
        else:
            for ipv in self.vizinhos:
                print("found 1 ip ...") 
                print(ipv)
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((ipv,23456))
                        print("connected")
                        s.sendall(Packet(type=type,ip=self.host,port=23456,payload=self.table.table).packetToBytes())
                        print("sended ...")
                        s.close()
                
                except socket.error as exc:
                    print(f"Caught exception socket.error : {exc}")

    
    
    def announcementWorkerThread(self,name,download): 
 
        threading.Thread(target=self.announce,args=(1,None,)).start()
        
 
        print(self.annoucementSocket)
        while True:
            
            if download and self.table.has_ip(socket.gethostbyname("server")):
                globals.printDebug(name,"Existe servidor")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    ipToSend = self.table.get_next_hop(socket.gethostbyname("server")) 
                    if ipToSend is not None:
                        print("ip2: " + ipToSend)
                        s.connect((ipToSend,23456))
                        globals.printDebug(name,"connected")
                        s.sendall(Packet(type=4,ip=self.host,port=23456,payload="").packetToBytes())
                        globals.printDebug(name,"sended ...")
                        s.close()
            else:
                globals.printDebug(name,"Não existe servidor")
            self.annoucementSocket.listen()
            conn, addr = self.annoucementSocket.accept()
            print('[announcementWorkerThread] Connected by', addr)
            data = conn.recv(1024)
            if data: 
                packet = Packet(bytes=data)
                if packet.type == globals.ANNOUNCEMENT or packet.type == globals.ANNOUCEMENTANDGET:
                    changed = self.table.updateTable(self.host,addr[0],packet.payload)
                    if changed:
                        # anuncia a todos
                        print("MUDOU CARALHO")
                        self.announce()
                        pass
                    else:
                        if globals.ANNOUCEMENTANDGET:
                            #anuncia ao addr
                            globals.printDebug(name,"Vou enviar ao " + addr[0] + " a tabela")
                            self.announce(type=2,addr=addr[0])
                            pass
                elif packet.type == 4:
                    # request
                    if 1 not in self.vizinhos.values():
                        # request Server
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            ipToSend = self.table.get_next_hop(socket.gethostbyname("server")) 
                            if ipToSend is not None:
                                print("ip: " + ipToSend)
                                s.connect((ipToSend,23456))
                                globals.printDebug(name,"connected")
                                s.sendall(Packet(type=4,ip=self.host,port=23456,payload=packet.getIp()).packetToBytes())
                                globals.printDebug(name,"sended ...")
                                s.close()
                        
                    self.vizinhos[addr[0]] = 1
     
                       
             
                    
    
    
    def workerThread(self,name):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        while True:
            self.socket.listen()
            conn, addr = self.socket.accept()
            print('[workerThread] Connected by', addr)
            data = conn.recv(1024)
            if data: 
                packet = Packet(bytes=data)
                if packet.type == globals.DATA: # Send to Server
                    print(packet.getPayload())
                    for ip in self.vizinhos:
                        if self.vizinhos[ip] == 1:
                            s.connect((ip,65432))
                            s.sendall(data)
                            
                else:
                    print("WHAAAAAAAAAAAAAT?")
                    break
     
        s.close()
        
        
    def start(self, download=False):
        self.announcement = threading.Thread(target=self.announcementWorkerThread, args=("annoucementWorker",download,))
        self.announcement.start()
        
        self.worker=threading.Thread(target=self.workerThread,args=("Worker",))
        self.worker.start()
         
            #inp = input("What to say: ")
            #while inp != "":
            #    s.sendall(bytes(inp,encoding='utf8'))
            #    inp = input("What to say: ")
#    def start(self)