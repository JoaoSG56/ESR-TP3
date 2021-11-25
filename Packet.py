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

    def bytesToPacket(self,bytes):
        message = bytes.decode('utf8').split(';')
        self.type = message[0]
        self.ip_destination = message[1]
        self.por = message[2]
        self.payload = message[3]

    def packetToBytes(self):
        if type(self.payload) == "dict":
            message = ";".join([self.type,self.ip_destination,self.port,json.dumps(self.payload)])
        else:
            message = ";".join([self.type,self.ip_destination,self.port,self.payload])
        return message.encode('utf8')
    