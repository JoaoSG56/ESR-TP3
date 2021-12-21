import sys
from server import Server
from node import Node
from tkinter import Tk
import socket


if __name__ == "__main__":
    
    params = sys.argv[1:]
    if "-s" in params:
        params.remove("-s")
        PORT = 65432      # Port to listen on (non-privileged ports are > 1023)
        ANNPORT = 23456
        server = Server(PORT,ANNPORT,params)
        server.start()
    
    elif len(params) > 0:
        root = Tk()
        node = Node(params,root)
        node.master.title("RTPClient " + socket.gethostname())
        root.mainloop()
        #node.start()
        """
        serverIp = params[0]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverIp,65432))
        inp = input("What to say: ")
        while inp != "":
            s.sendall(bytes(inp,encoding='utf8'))
            inp = input("What to say: ")
        
        """
