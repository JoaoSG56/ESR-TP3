class Packet:
    def __init__(self,packetID,payload):
        self.packetID = packetID
        self.payload = payload

    def packetToBytes(self):
        message = ";".join([self.packetID,self.payload])