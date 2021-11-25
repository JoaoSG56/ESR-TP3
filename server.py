import socket
import threading



class Server:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        
    def start(self):
        def listener(name,conn,addr):
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(data)
                conn.sendall(data)
            
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while True:       
            print("Listening at ")
            self.socket.listen()
            conn, addr = self.socket.accept()
            
            x = threading.Thread(target=listener, args=("listener",conn,addr))
            x.start()