import json
class Packet:
    def __init__(self,**kwargs):
        if "bytes" not in kwargs:
            self.packetID = kwargs.get("packetID",None)
            self.type = kwargs.get("type",None)
            self.ip_origem = kwargs.get("ip_origem",None)
            self.ip_destination = kwargs.get("ip_destino",None)
            self.port = kwargs.get("port",None)
            self.payload = kwargs.get("payload",None)
        else:
            self.bytesToPacket(kwargs.get("bytes"))


    def getType(self):
        return self.type
    
    def getPacketID(self):
        return self.packetID

    def getIpDestino(self):
        return self.ip_destination
    
    def getIpOrigem(self):
        return self.ip_origem
    
    def getPayload(self):
        return self.payload

    def bytesToPacket(self,bytes):
        message = bytes.decode('utf8').split(';')
        self.packetID = message[0]
        self.type = message[1]
        self.ip_origem = message[2]
        self.ip_destination = message[3]
        self.port = message[4]
        self.payload = message[5]

    def packetToBytes(self):
        message = ";".join([str(self.packetID),str(self.type),self.ip_origem,self.ip_destination,str(self.port),str(self.payload)])
        return message.encode('utf8')
    
    def toString(self):
        return ";".join([str(self.packetID),str(self.type),self.ip_origem,self.ip_destination,str(self.port),str(self.payload)])


    def setIpDestino(self,ip):
        self.ip_destination = ip
        
    def setIpOrigem(self,ip):
        self.ip_destination = ip
        
        
    def printa(self):
        print(self.packetID)
        print(self.type)
        print(self.ip_origem)
        print(self.ip_destination)
        print(self.port)
        print(self.payload)
