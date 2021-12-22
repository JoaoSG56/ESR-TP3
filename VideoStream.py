import cv2,imutils
import base64
WIDTH=400
class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			#self.vidcap = cv2.VideoCapture(filename)
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		
	def nextFrame(self):
		"""Get next frame."""
		
		data = self.file.read(5) # Get the framelength from the first 5 bits

		if data: 
			framelength = int(data)
							
			# Read the current frame
			data = self.file.read(framelength)
			self.frameNum += 1
		else:
			self.file.seek(0)
		return data
		"""
		s , frame = self.vidcap.read()
		if not s:
			self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, 0)
			s , frame = self.vidcap.read()
		self.frameNum += 1
		frame = imutils.resize(frame,width=WIDTH)
		encoded, buffer = cv2.imencode('.jpg', frame,[cv2.IMWRITE_JPEG_QUALITY,80])
		data = base64.b64encode(buffer)
  		
		return data
  		"""
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
	
	