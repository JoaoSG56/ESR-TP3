import base64
from tkinter import *
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk
import cv2
import numpy as np

import socket, threading
import time, sys,signal
from RtpPacket import RtpPacket


from packet import Packet
from table import Table
import random

import globals

CACHE_FILE_NAME = ".cache-"
CACHE_FILE_EXT = ".jpg"


class Node:
    def __init__(self,params,master):
        self.master = master
        
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.createWidgets()
        self.frameNbr = 0
        self.session = socket.gethostname()
        
        self.table = Table()
        """
        table:
        {
            "primaria":
                {
                    "next_hop":"$ip",
                    "cost":"$cost",
                },
            "secundaria":
                {
                    "next_hop":"$ip",
                    "cost":"$cost",
                }
        }
        vizinhos:
        {
            "ip":[0,0,sA,sD]           desligado, rota inativa, Socket announcement, Socket Data
            "ip2":[1,0,sA,sD]          ligado, rota inativa, Socket announcement, Socket Data
            etc...
        }
        """
        self.vizinhos = {}
        for name in params:
            ip = socket.gethostbyname(name)
            self.vizinhos[ip] = [0,0,None,None]
            
        
        self.host = socket.gethostbyname(socket.gethostname())
        
        AddressPortData = (self.host,65432)
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.dataSocket.bind(AddressPortData)
        
        AddressPortAnn = (self.host,23456)
        self.announcementSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.announcementSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.announcementSocket.bind(AddressPortAnn)
        
        self.threads = []
        self.downloading = False
        self.stack = []

    def createWidgets(self):
        """Build GUI."""
        # Create Play button		
        self.setup = Button(self.master, width=20, padx=3, pady=3)
        self.setup["text"] = "Setup"
        self.setup["command"] = self.start
        self.setup.grid(row=1, column=1, padx=2, pady=2)

        # Create Play button		
        self.play = Button(self.master, width=20, padx=3, pady=3)
        self.play["text"] = "Play"
        self.play["command"] = self.requestVideo
        self.play.grid(row=1, column=2, padx=2, pady=2)
        
        # Create Pause button			
        self.pause = Button(self.master, width=20, padx=3, pady=3)
        self.pause["text"] = "Pause"
        self.pause["command"] = self.stopVideo
        self.pause.grid(row=1, column=3, padx=2, pady=2)
        
        # Create Debug button			
        self.debugB = Button(self.master, width=20, padx=3, pady=3)
        self.debugB["text"] = "Debug"
        self.debugB["command"] = self.debug
        self.debugB.grid(row=1, column=4, padx=2, pady=2)
        
        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 

    
    def signalINT_handler(self,signum, frame):
        try:
            for ip in self.vizinhos:
            
                if self.vizinhos[ip][2] is not None:
                    self.vizinhos[ip][2].close()
                if self.vizinhos[ip][3] is not None:
                    self.vizinhos[ip][3].close()
            self.dataSocket.close()
            self.announcementSocket.close()
        except socket.error as exc:
            print(f"Caught exception socket.error : {exc}")
        print("exiting ...")    
        sys.exit(0)
       

    def hasFluxo(self):
        for ip in self.vizinhos:
            if self.vizinhos[ip][1]:
                return True
        return False

        
    def announce(self):
        for ip in self.vizinhos:
            print("found 1 ip ...") 
            print(ip)
            try:
                if self.vizinhos[ip][2] is None:
                    self.vizinhos[ip][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.vizinhos[ip][2].connect((ip,23456))
                print("connected Announcement")
                
                self.vizinhos[ip][0] = 1
                self.vizinhos[ip][1] = 0
                self.vizinhos[ip][2].sendall(Packet(packetID=0,type=globals.IM_HERE,ip_origem=self.host,ip_destino=ip,port=23456,payload="").packetToBytes())
                print("sended ...")
                #self.vizinhos[ipv][2].close()
            
            except socket.error as exc:
                print(f"[PORTA 23456] Caught exception socket.error : {exc}")
        #announcement_done.set()
            

    # ip -> ip de onde não é para mandar
    def announceChange(self,ipN,cost):
        for ip in self.vizinhos:
            if self.vizinhos[ip][0] and ip != ipN:
                # announce
                self.vizinhos[ip][2].sendall(Packet(packetID=0,type=globals.ANNOUNCEMENT,ip_origem=self.host,ip_destino=ip,port=23456,payload=str(cost)).packetToBytes())
        
    def announceTo(self,ipToAnnounce,cost):
        if self.vizinhos[ipToAnnounce][0]:    
            self.vizinhos[ipToAnnounce][2].sendall(Packet(packetID=0,type=globals.ANNOUNCEMENT,ip_origem=self.host,ip_destino=ipToAnnounce,port=23456,payload=str(cost)).packetToBytes())

    
    def announcementReceiverWorker(self,name,conn):
        ipFrom = None
        while data := conn.recv(1024):
            if data: 
                packet = Packet(bytes=data)
                print("\n\n")
                packet.printa()
                print("\n\n")
                
                if ipFrom == None:
                    ipFrom = packet.getIpOrigem()
                if packet.type == globals.IM_HERE:
                    if ipFrom in self.vizinhos:
                        self.vizinhos[ipFrom][0] = 1
                        if self.vizinhos[ipFrom][2] is None:
                            self.vizinhos[ipFrom][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.vizinhos[ipFrom][2].connect((ipFrom,23456))
                        globals.printDebug("connected",name)
                        if self.table.hasRoute():
                            cost = self.table.getRouteCost()
                            globals.printDebug(cost,name)
                            if cost is not None:
                                print("tem cost: " + str(cost))

                                p = Packet(packetID=0,type=2,ip_origem=self.host,ip_destino=ipFrom,port=23456,payload=str(cost))
                                self.vizinhos[ipFrom][2].sendall(p.packetToBytes())
                                globals.printDebug("sended ...",name)
                            else:
                                globals.printDebug("annWorker","cost é none")
                    else:
                        print("algo está mal")
                    
                    
                elif packet.type == globals.ANNOUNCEMENT:
                    if not self.vizinhos[ipFrom][0]:
                        globals.printDebug("Server connected",name)
                        self.vizinhos[ipFrom][0] = 1
                        if self.vizinhos[ipFrom][2] is None:
                            self.vizinhos[ipFrom][2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        print(self.vizinhos[ipFrom][2])
                        self.vizinhos[ipFrom][2].connect((ipFrom,23456))
                    globals.printDebug("Type announcement","annworker")
                    changed = self.table.updateTable(ipFrom,int(packet.getPayload())+1)
                    if changed == 1:
                        # anuncia a todos

                        ## Se rota melhor então muda a cena
                        if (self.downloading or self.hasFluxo()):            
                            next = self.table.get_next_hop()
                            if self.vizinhos[next][0]:
                                try:
                                    self.vizinhos[next][2].sendall(Packet(packetID=0,type=4,ip_origem=self.host,ip_destino=next,port=23456,payload="").packetToBytes())
                                    globals.printDebug("sended ...",name)
                                    
                                    
                                except socket.error as exc:
                                    print(f"[PORTA 65432] Caught exception socket.error : {exc}")
                        globals.printDebug("mudou a rota primária","annworker")
                        self.announceChange(ipFrom,self.table.getRouteCost())
                    elif int(packet.getPayload()) > (self.table.getRouteCost()+1):
                        self.announceTo(ipFrom,self.table.getRouteCost())
                elif packet.type == globals.REQUEST:
                    # request
                    if self.table.hasRoute():
                        
                        print("tenho rota ativa")
                        # request Server
                        next = self.table.get_next_hop()
                        if self.vizinhos[next][0]:
                            
                            try:
                                
                                self.vizinhos[ipFrom][3] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                #self.vizinhos[ip][3].connect((ip,65432))
                                print("connected Datas")
                                
                                s = self.vizinhos[next][2]

                                if self.hasFluxo():
                                    globals.printDebug("tem fluxo",name)
                                    self.vizinhos[ipFrom][1] = 1
                                else:
                                    s.sendall(Packet(packetID=0,type=4,ip_origem=self.host,ip_destino=next,port=23456,payload="").packetToBytes())
                                    globals.printDebug("sended ...",name)
                                    self.vizinhos[ipFrom][1] = 1
                                
                            except socket.error as exc:
                                print(f"[PORTA 65432] Caught exception socket.error : {exc}")
                elif packet.type == globals.STOP:
                    # stop
                    self.vizinhos[packet.getIpOrigem()][1] = 0 # rota inativa
                    self.vizinhos[packet.getIpOrigem()][3].close()
                    if not self.hasFluxo():
                        globals.printDebug("Existe servidor",name)
                        s = self.vizinhos[self.table.get_next_hop()][2]
                        print("ip2: " + self.table.get_next_hop())
                        s.sendall(Packet(packetID=0,type=globals.STOP,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
                        globals.printDebug("sended ...",name)
                            
                    else:
                        print("não tenho rota ativa")
        globals.printDebug("Ligação caiu",name)
        if ipFrom is not None and ipFrom in self.vizinhos:
            self.vizinhos[ipFrom][0] = 0
            self.vizinhos[ipFrom][1] = 0
            if self.vizinhos[ipFrom][2] is not None:
                self.vizinhos[ipFrom][2].close()
                self.vizinhos[ipFrom][2] = None
            if self.vizinhos[ipFrom][3] is not None:
                self.vizinhos[ipFrom][3].close()
                self.vizinhos[ipFrom][3] = None
            
            if ipFrom == self.table.get_next_hop():
                self.stack.clear()
                self.table.removePrimaryRoute()
                if self.table.hasRoute():
                    if self.hasFluxo() or self.downloading: # se tiver de receber data
                        self.requestData()
                else:
                    globals.printError("No Route Available",name)
                    #self.downloading = False
                pass
            elif not self.hasFluxo() and not self.downloading:
                # do stop request
                globals.printDebug("Stoping download ... No flux")
                self.sendStopRequest()
        else:
            globals.printError("what?",name)
    
    
    def sendStopRequest(self):
        s = self.vizinhos[self.table.get_next_hop()][2]
        print("ip2: " + self.table.get_next_hop())
        s.sendall(Packet(packetID=0,type=globals.STOP,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
        globals.printDebug("sended ...")
       
    
    
    def announcementWorker(self,name): 
        while True:

            self.announcementSocket.listen()
            conn, addr = self.announcementSocket.accept()
            print('[announcementWorker] Connected by', addr)
            thread = threading.Thread(target=self.announcementReceiverWorker,args=("announcementReceiverWorker",conn,))
            self.threads.append(thread)
            thread.daemon = True
            thread.start()
            
    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + self.session + CACHE_FILE_EXT
        
        """
        d = base64.b64decode(data,' /')
        npdata = np.fromstring(d,np.uint8)
        frame = cv2.imdecode(npdata,1)
        cv2.imwrite(cachename,frame)
        """
        
        file = open(cachename, "wb")
        file.write(data)
        file.close()

        return cachename

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image = photo, height=288)
        self.label.image = photo
 
    def dataWorker(self,name):     
        while True:

            data, addr = self.dataSocket.recvfrom(20480)
            
            if data: 
                rtpPacket = RtpPacket()
                rtpPacket.decode(data)
                ip_O = rtpPacket.getIpOrigem()
                if ip_O not in self.stack:
                    self.stack.append(ip_O)
                    if len(self.stack) > 1:
                        globals.printError("2 ips diferentes!!!!",name)
                        sh = self.table.get_next_hop() 
                        for ip in self.stack:
                            if ip != sh:
                                s = self.vizinhos[ip][2]
                                print("stoping: " + ip)
                                s.sendall(Packet(packetID=0,type=globals.STOP,ip_origem=self.host,ip_destino=ip,port=23456,payload="").packetToBytes())
                                globals.printDebug("sended ...",name)
                                self.stack.remove(ip)
                            socket.gethostbyname
                    
                if self.downloading:
                    
                    
                    currFrameNbr = rtpPacket.seqNum()
                    if currFrameNbr > self.frameNbr:
                        self.frameNbr = currFrameNbr
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
                
                rtpPacket.setIpOrigem(self.host)
                newData = rtpPacket.getPacket()
                for ip in self.vizinhos:
                    if self.vizinhos[ip][1] == 1:
                        globals.printDebug("found rota ativa ...","dataWorker")
                        self.vizinhos[ip][3].sendto(newData, (ip,65432))
                        globals.printDebug("sended ...","dataWorker")
            
         
      
    def requestData(self):
        globals.printDebug("Existe servidor")
        s = self.vizinhos[self.table.get_next_hop()][2]
        s.sendall(Packet(packetID=0,type=globals.REQUEST,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
        globals.printDebug("sended ...")
     
      
    def requestVideo(self):
        if not self.downloading:
            if self.table.hasRoute():
                if not self.stack:
                    globals.printDebug("Existe servidor")
                    s = self.vizinhos[self.table.get_next_hop()][2]
                    s.sendall(Packet(packetID=0,type=globals.REQUEST,ip_origem=self.host,ip_destino=self.table.get_next_hop(),port=23456,payload="").packetToBytes())
                    globals.printDebug("sended ...")
                self.downloading = True
            else:
                globals.printDebug("No server available")
        
    def stopVideo(self):
        if self.downloading:
            if self.table.hasRoute():
                globals.printDebug("Existe servidor")
                if not self.hasFluxo():
                    self.sendStopRequest()
                self.downloading = False
                self.stack.clear()

            else:
                globals.printDebug("não devia entrar aqui")
    
    def debug(self):
        self.table.print()
        globals.printDebug("downloading: ",end="")
        if self.downloading:
            globals.printSuccess(str(self.downloading))
        else:
            globals.printError(str(self.downloading))
        print(24*'*' + " VIZINHOS " + 24*'*')
        for i in self.vizinhos:
            globals.printDebug("ip: ",end="")
            globals.printSuccess(i)
            
            globals.printDebug("\tonline: ",end="")
            globals.printSuccess(self.vizinhos[i][0])
            
            globals.printDebug("\tactive: ",end="")
            globals.printSuccess(self.vizinhos[i][1])
            
            globals.printDebug("\tsocket1: ",end="")
            if self.vizinhos[i][2]:
                globals.printSuccess("True")
            else:
                globals.printError("False")
            
            globals.printDebug("\tsocket2: ",end="")
            if self.vizinhos[i][3]:
                globals.printSuccess("True")
            else:
                globals.printError("False")
        
        print(58*'*')

    def handler(self):
	    #self.pauseMovie()
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.signalINT_handler(None,None)
        else: # When the user presses cancel, resume playing.
            #self.playMovie()
            pass
    
    def start(self):
        signal.signal(signal.SIGINT, self.signalINT_handler)
        
        announcementThread = threading.Thread(target=self.announcementWorker, args=("annoucementWorker",)) # 23456
        self.threads.append(announcementThread)
        announcementThread.daemon = True
        announcementThread.start()
        
        workerThread =threading.Thread(target=self.dataWorker,args=("Worker",)) # 65432
        self.threads.append(workerThread)
        workerThread.daemon = True
        workerThread.start()

        self.announce()
         



    