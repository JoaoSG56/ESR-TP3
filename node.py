import socket
import threading

from packet import Packet
from table import Table

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
        """
        
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(self.table.value)
        
    def start(self):

        for ipv in self.table.table:
            print("found 1 ip ...") 
            print(ipv)
            print(self.table.table[ipv]["announcement_port"])
            try:
                self.socket.connect((ipv,self.table.table[ipv]["announcement_port"]))
                print("connected")
                self.socket.sendall(Packet(type=1,ip=ipv,port=self.table.table[ipv]["announcement_port"],payload=self.table.table).packetToBytes())
                print("sended ...")
                self.socket.close()
            except socket.error as exc:
                print(f"Caught exception socket.error : {exc}")
        
        
        
            #inp = input("What to say: ")
            #while inp != "":
            #    s.sendall(bytes(inp,encoding='utf8'))
            #    inp = input("What to say: ")
#    def start(self)