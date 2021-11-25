import sys
import threading
import socket


def listener(name,conn,addr):

    print('Connected by', addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(data)
        conn.sendall(data)

def main():
    
    params = sys.argv[1:]
    if "-s" in params:
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        while True:       
            print("Listening at ")
            s.listen()
            conn, addr = s.accept()
            
            x = threading.Thread(target=listener, args=("listener",conn,addr))
            x.start()
        
    elif len(params) == 1:
        serverIp = params[0]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverIp,65432))
        inp = input("What to say: ")
        while inp != "":
            s.sendall(bytes(inp,encoding='utf8'))
            inp = input("What to say: ")
        
        

main()
