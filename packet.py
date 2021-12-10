import json
class Packet:
    def __init__(self,**kwargs):
        if "bytes" not in kwargs:
            self.type = kwargs.get("type",None)
            self.ip_origem = kwargs.get("ip_origem",None)
            self.ip_destination = kwargs.get("ip_destino",None)
            self.port = kwargs.get("port",None)
            self.payload = kwargs.get("payload",None)
        else:
            self.bytesToPacket(kwargs.get("bytes"))


    def getType(self):
        return self.type

    def getIpDestino(self):
        return self.ip_destination
    
    def getIpOrigem(self):
        return self.ip_origem
    
    def getPayload(self):
        return self.payload

    def bytesToPacket(self,bytes):
        message = bytes.decode('utf8').split(';')
        self.type = message[0]
        self.ip_origem = message[1]
        self.ip_destination = message[2]
        self.port = message[3]
        self.payload = message[4]

    def packetToBytes(self):
        if type(self.payload) is dict:
            print("entrou onde NÃO devia")
            message = ";".join([str(self.type),self.ip_origem,self.ip_destination,str(self.port),json.dumps(self.payload)])
        else:
            message = ";".join([str(self.type),self.ip_origem,self.ip_destination,str(self.port),str(self.payload)])
        return message.encode('utf8')
    
    def toString(self):
        return ";".join([str(self.type),self.ip_origem,self.ip_destination,str(self.port),str(self.payload)])


    def setIpDestino(self,ip):
        self.ip_destination = ip
        
    def setIpOrigem(self,ip):
        self.ip_destination = ip
        
        
    def printa(self):
        print(self.type)
        print(self.ip_origem)
        print(self.ip_destination)
        print(self.port)
        print(self.payload)
