import sys
from server import Server
from node import Node



def main():
    
    params = sys.argv[1:]
    if "-s" in params:

        PORT = 23456        # Port to listen on (non-privileged ports are > 1023)
        server = Server(PORT)
        server.start()
    elif "-d" in params:
        pass
    
    elif len(params) > 0:
        node = Node(params)
        node.start()
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
