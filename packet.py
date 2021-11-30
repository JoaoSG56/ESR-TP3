import json
class Packet:
    def __init__(self,**kwargs):
        if "bytes" not in kwargs:
            self.type = kwargs.get("type",None)
            self.ip_destination = kwargs.get("ip",None)
            self.port = kwargs.get("port",None)
            self.payload = kwargs.get("payload",None)
        else:
            self.bytesToPacket(kwargs.get("bytes"))


    def getType(self):
        return self.type

    def bytesToPacket(self,bytes):
        message = bytes.decode('utf8').split(';')
        self.type = message[0]
        self.ip_destination = message[1]
        self.port = message[2]
        self.payload = json.loads(message[3])

    def packetToBytes(self):
        print(type(self.payload))
        if type(self.payload) is dict:
            message = ";".join([str(self.type),self.ip_destination,str(self.port),json.dumps(self.payload)])
        else:
            message = ";".join([str(self.type),self.ip_destination,str(self.port),json.dumps(self.payload)])
        return message.encode('utf8')
    
    def toString(self):
        return ";".join([str(self.type),self.ip_destination,str(self.port),str(self.payload)])
