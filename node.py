import socket
import threading

class Node:
    def __init__(self,params,port,annport):
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
        
        
        
    def updateTable(self):
        for neighbor in self.table:
            self.socket.connect((neighbor,self.table[neighbor]["announcement_port"]))
            
            #inp = input("What to say: ")
            #while inp != "":
            #    s.sendall(bytes(inp,encoding='utf8'))
            #    inp = input("What to say: ")
#    def start(self)