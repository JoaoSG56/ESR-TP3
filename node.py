import socket
import threading

from packet import Packet

class Node:
    def __init__(self,params):
        annport = 23456
        port = 65432
        self.table = {}
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
        """
        for ip in params:
            if ip not in self.table:
                self.table[ip] = {"next_hop":ip,"port":port,"announcement_port":annport,"cost":1,"active":False}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self.table)
        
    def start(self):

        for ipv in self.table:
            print("found 1 ip ...") 
            print(ipv)
            print(self.table[ipv]["announcement_port"])
            try:
                self.socket.connect((ipv,self.table[ipv]["announcement_port"]))
                print("connected")
                self.socket.sendall(Packet(type=1,ip=ipv,port=self.table[ipv]["announcement_port"],payload=self.table).packetToBytes())
                print("sended ...")
                self.socket.close()
            except socket.error as exc:
                print(f"Caught exception socket.error : {exc}")
        
        
        
    def updateTable(self):
        for neighbor in self.table:
            self.socket.connect((neighbor,self.table[neighbor]["announcement_port"]))
            
            #inp = input("What to say: ")
            #while inp != "":
            #    s.sendall(bytes(inp,encoding='utf8'))
            #    inp = input("What to say: ")
#    def start(self)