import sys
from server import Server
from node import Node



def main():
    
    params = sys.argv[1:]
    if "-s" in params:
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
        server = Server(HOST,PORT)
        server.start()
    elif "-d" in params:
        pass
    
    elif len(params) > 0:
        port = 65432
        annport = 23456
        node = Node(params,port,annport)
        """
        serverIp = params[0]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverIp,65432))
        inp = input("What to say: ")
        while inp != "":
            s.sendall(bytes(inp,encoding='utf8'))
            inp = input("What to say: ")
        
        """

main()
