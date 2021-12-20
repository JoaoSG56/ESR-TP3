import sys
from time import time
HEADER_SIZE = 16

class RtpPacket:
	

	def __init__(self):
		self.header = bytearray(HEADER_SIZE)
		pass

	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, ip, payload):
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())

		# Encode the RTP packet
		# Fill the header bytearray with RTP header fields
		self.header[0] = (self.header[0] | version << 6) & 0xC0; # 2 bits
		self.header[0] = (self.header[0] | padding << 5); # 1 bit
		self.header[0] = (self.header[0] | extension << 4); # 1 bit
		self.header[0] = (self.header[0] | (cc & 0x0F)); # 4 bits
		self.header[1] = (self.header[1] | marker << 7); # 1 bit
		self.header[1] = (self.header[1] | (pt & 0x7f)); # 7 bits
		self.header[2] = (seqnum & 0xFF00) >> 8; # 16 bits total, this is first 8
		self.header[3] = (seqnum & 0xFF); # second 8
		self.header[4] = (timestamp >> 24); # 32 bit timestamp
		self.header[5] = (timestamp >> 16) & 0xFF;
		self.header[6] = (timestamp >> 8) & 0xFF;
		self.header[7] = (timestamp & 0xFF);
		self.header[8] = (ssrc >> 24); # 32 bit ssrc
		self.header[9] = (ssrc >> 16) & 0xFF;
		self.header[10] = (ssrc >> 8) & 0xFF;
		self.header[11] = (ssrc & 0xFF)
		
		ip = ip.split('.')
		self.header[12] = (int(ip[0]) & 0xFF)
		self.header[13] = (int(ip[1]) & 0xFF)
		self.header[14] = (int(ip[2]) & 0xFF)
		self.header[15] = (int(ip[3]) & 0xFF)

		# Get the payload from the argument
		self.payload = payload

	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]

	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)

	def seqNum(self):
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)

	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)

	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)

	def getPayload(self):
		"""Return payload."""
		return self.payload

	def getIpOrigem(self):
		"""Return Ip"""
		ip = str(self.header[12]) +"."+ str(self.header[13]) +"."+ str(self.header[14]) +"."+ str(self.header[15])
		return ip

	def setIpOrigem(self,ip):
		ip = ip.split('.')
		self.header[12] = (int(ip[0]) & 0xFF)
		self.header[13] = (int(ip[1]) & 0xFF)
		self.header[14] = (int(ip[2]) & 0xFF)
		self.header[15] = (int(ip[3]) & 0xFF)

	def getPacket(self):
		"""Return RTP packet."""
		return self.header + self.payload