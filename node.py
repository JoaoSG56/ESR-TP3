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
            self.vizinhos[ip] = 0
            
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
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
        
    def announce(self,addr = None):
        if addr is not None:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((addr,23456))
                    print("connected")
                    s.sendall(Packet(type=2,ip=addr,port=23456,payload=self.table.table).packetToBytes())
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
                        s.sendall(Packet(type=2,ip=ipv,port=23456,payload=self.table.table).packetToBytes())
                        print("sended ...")
                        s.close()
                
                except socket.error as exc:
                    print(f"Caught exception socket.error : {exc}")

    
    def announcementWorkerThread(self,name): 
        self.announce()
        print(self.annoucementSocket)
        while True:
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
                            self.announce(addr)
                            pass
                       
             
                    
    
    
    def workerThread(self,name):
        pass
    
    def start(self):
        self.announcement = threading.Thread(target=self.announcementWorkerThread, args=("annoucementWorker",))
        self.announcement.start()
        
        self.worker=threading.Thread(target=self.workerThread,args=("Worker",))
        self.worker.start()
        
        


        
        
        
            #inp = input("What to say: ")
            #while inp != "":
            #    s.sendall(bytes(inp,encoding='utf8'))
            #    inp = input("What to say: ")
#    def start(self)