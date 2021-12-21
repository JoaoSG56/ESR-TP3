import socket, threading, signal

from VideoStream import VideoStream
from RtpPacket import RtpPacket

from packet import Packet
import globals

import sys, traceback

import time

class Server:
    def __init__(self,port,annport,params):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.host = local_ip
        self.port = port
        self.annport = annport
    
        """
        "ip":[0,0,sA,sD]           desligado, rota inativa, Socket announcement, Socket Data
        "ip2":[1,0,sA,sD]          ligado, rota inativa, Socket announcement, Socket Data
        etc...
        
        """
        self.vizinhos = {}
        for name in params:
            ip = socket.gethostbyname(name)
            print(ip)
            self.vizinhos[ip] = [0,0,None]
        self.annSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.annSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.threads = []
            
      
    
    def signalINT_handler(self,signum, frame):
        try:
            self.annSocket.close()
            for ip in self.vizinhos:
                if self.vizinhos[ip][2] is not None:
                    self.vizinhos[ip][2].close()
            
        except socket.error as exc:
            print(f"Caught exception socket.error : {exc}")
        print("exiting ...")    
        sys.exit(0)
       
    
    def announce(self):
        for ip in self.vizinhos:
            print("found 1 ip ...") 
            print(ip)
            try:
                self.vizinhos[ip][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                self.vizinhos[ip][2].connect((ip,23456))
                print("connected Announcement")
                
                self.vizinhos[ip][0] = 1
                self.vizinhos[ip][1] = 0
                self.vizinhos[ip][2].sendall(Packet(packetID=0,type=globals.ANNOUNCEMENT,ip_origem=self.host,ip_destino=ip,port=23456,payload="0").packetToBytes())
                print("sended ...")
                #self.vizinhos[ipv][2].close()
            
            except socket.error as exc:
                print(f"Caught exception socket.error : {exc}")

    
    
    def serverConnWorker(self,name,conn):
        ipFrom = None
        while data := conn.recv(1024):
            if not data:
                break
            packet = Packet(bytes=data)
            print("\n\n")
            packet.printa()
            print("\n\n")
            if ipFrom == None:
                ipFrom = packet.getIpOrigem()
            if packet.type == globals.IM_HERE:
                print(self.vizinhos)
                if self.vizinhos[ipFrom][2] is None:
                    self.vizinhos[ipFrom][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.vizinhos[ipFrom][2].connect((ipFrom,23456))
                print("connected Announcement")
                
                self.vizinhos[ipFrom][0] = 1
                self.vizinhos[ipFrom][1] = 0
                self.vizinhos[ipFrom][2].sendall(Packet(packetID=0,type=globals.ANNOUNCEMENT,ip_origem=self.host,ip_destino=ipFrom,port=23456,payload="0").packetToBytes())
                print("sended ...")
            elif packet.type == globals.REQUEST:
                globals.printDebug("Updated to active",name)
                self.vizinhos[ipFrom][1] = 1
            elif packet.type == globals.STOP:
                globals.printDebug("Updated to inactive",name)
                self.vizinhos[ipFrom][1] = 0
        globals.printDebug("Ligação caiu",name)
        self.vizinhos[ipFrom][0] = 0
        self.vizinhos[ipFrom][1] = 0
        if self.vizinhos[ipFrom][2] is not None:
            self.vizinhos[ipFrom][2].close()
            self.vizinhos[ipFrom][2] = None
        globals.printDebug("Stoping sending to " + ipFrom)
    
#   Worker for thread
#   Listens for connections and decides what to do depending on type of the packet    
    def serverListenerWorker(self,name):    
        self.annSocket.bind((self.host, self.annport))
    
        while True:
            print(self.annSocket)
            self.annSocket.listen()
            conn, addr = self.annSocket.accept()
            print('[PORTLISTENER] Connected by', addr)
            x = threading.Thread(target=self.serverConnWorker,args=("serverConnWorker",conn,))
            self.threads.append(x)
            x.daemon = True
            x.start()
            

    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26 # MJPEG type
        seqnum = frameNbr
        ssrc = 0

        rtpPacket = RtpPacket()

        rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, self.host, payload)

        return rtpPacket.getPacket()   
            
         

    def sendData(self,name):
        stream = VideoStream("files/test.Mjpeg")
        while True:    
            time.sleep(0.033)
            data = stream.nextFrame()

            if data:
                frameNumber = stream.frameNbr()
                for ip in self.vizinhos:
                    if self.vizinhos[ip][0] == 1 and self.vizinhos[ip][1] == 1:
                        try:
                            self.rtpSocket.sendto(self.makeRtp(data,frameNumber), (ip,65432))
                            print("[" + name + "] sended ...")
                        except:
                            print("Connection Error")
                            print('-'*60)
                            traceback.print_exc(file=sys.stdout)
                            print('-'*60)
                    
        
    def inputWorker(self,name):
        while True:
            inp = input("server>> ")
            if inp == "help":
                print("commands:\nprint")
            elif inp == "print":
                print(self.vizinhos)

          
                
    def start(self):
        signal.signal(signal.SIGINT, self.signalINT_handler)
        
        datathread = threading.Thread(target=self.serverListenerWorker,args=("serverListenerWorker",))
        self.threads.append(datathread)
        datathread.daemon = True
        datathread.start()
        
        
        sendDataThread = threading.Thread(target=self.sendData,args=("sendData",))
        self.threads.append(sendDataThread)
        sendDataThread.daemon = True
        sendDataThread.start()
        
        inputThread = threading.Thread(target=self.inputWorker,args=("inputThread",))
        self.threads.append(inputThread)
        inputThread.daemon=True
        inputThread.start()
        
        self.announce()
        
        print("[Server] Listening at " + self.host)
        
        for i in self.threads:
            i.join()
            
        
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while True:       
            print("[ANNOUNCEMENT PORT] Listening at " + self.host)
            self.socket.listen()
            conn, addr = self.socket.accept()
            print("here")
            x = threading.Thread(target=self.dataListener, args=("listener",conn,addr))
            x.start()
        """