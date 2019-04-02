import serial

class RfidDevice(object):
	def __init__(self,port,baudrate=38400):
		self.device = serial.Serial()
		self.device.port = (port)
		self.device.baudrate = 38400
		self.device.bytesize = serial.EIGHTBITS
		self.device.parity = serial.PARITY_NONE
		self.device.stopbits = serial.STOPBITS_ONE
		self.device.timeout = 1
		self.device.xonxoff = False
		self.device.rtscts = False
		self.device.dsrdtr = False
		self.device.writeTimeout = 2

		self.state = 'Closed'

		self.initcommand = [0xAA, 0xDD, 0x00, 0x03, 0x01, 0x02, 0x03]
		self.bipcommand = [0xAA, 0xDD, 0x00, 0x04, 0x01, 0x03, 0x0A, 0x08]
		self.readcommand = [0xAA, 0xDD, 0x00, 0x03, 0x01, 0x0C, 0x0D]

	def initialise(self):
		if self.state == 'Closed':
			try:
				self.device.open()
			except:
				raise Exception('Error trying to open the specified port')
			if self.device.isOpen():
				self.device.flushInput()
				self.device.flushOutput()
				self.device.write(serial.to_bytes(self.initcommand))
				response = self.device.readline()
				response = str((response[7:-1]))
				if 'ID card reader & writer' in response:
					self.state = 'Ready'
				else:
					raise Exception('Error trying to initialise RFID device')

		else:
			raise Exception('RFID Device is already initialised.')

	def bleep(self):
		if self.state == 'Ready':
			self.device.flushInput()
			self.device.flushOutput()
			self.device.write(serial.to_bytes(self.bipcommand))
			response = self.device.readline()

	def disconnect(self):
		if self.state == 'Ready':
			self.device.close()
		else:
			raise Exception('RFID Device is already disconnected')

	def read(self):
		if self.state == 'Ready':
			self.device.flushInput()
			self.device.flushOutput()
			self.device.write(serial.to_bytes(self.readcommand))
			response = self.device.readline()
			if len(response) < 10:
				return(False)
			else:
				if len(response) == 12:
					response = str((response[7:]).hex())
				elif len(response) == 13:
					response = str((response[6:-1]).hex())
				newdata = str((int(response, 16)))
				return(newdata)
		else:
			raise Exception('You must initialise the device in order to read or write data.')

	def write(self,data):
		def rfidchecksum(var):
			XOR_sum = 0x0
			for char in var:
				# print(char)
				XOR_sum = XOR_sum ^ char

			return (hex(XOR_sum))
		def rfidhex(data):
			return ("{:010X}".format(data))
		def formatRfidData(data):
			newdata = []
			data = rfidhex(data)
			for x in range(len(data)):
				if (x + 1) % 2 != 0:
					newdata.append(int(data[x] + data[x + 1], 16))
			return (newdata)

		if self.state == 'Ready':
			try:
				int(data)
				if (data) > 9999999999:
					raise Exception('The length of the value cannot be more than 10.')
			except:
				raise Exception('Value could only be an integer.')

			def send1(data):
				sendchain = [0xAA, 0xDD, 0x00, 0x09]
				sendchain2 = [0x03, 0x0C, 0x00]
				data = formatRfidData(int(data))
				for x in data:
					sendchain2.append(x)
				sendchain3 = int(rfidchecksum(sendchain2), 16)
				sendchaincomplete = sendchain
				for x in sendchain2:
					sendchaincomplete.append(x)
				sendchaincomplete.append(sendchain3)
				try:
					self.device.flushInput()
					self.device.flushOutput()
					self.device.write(serial.to_bytes(sendchaincomplete))
					response = self.device.readline()
					if response[5:7].hex() == '0c00':
						return(True)
					else:
						return(False)
				except:
					return(False)
			def send2(data):
				sendchain = [0xAA, 0xDD, 0x00, 0x09]
				sendchain2 = [0x02, 0x0C, 0x00]
				data = formatRfidData(int(data))
				for x in data:
					sendchain2.append(x)
				sendchain3 = int(rfidchecksum(sendchain2), 16)
				sendchaincomplete = sendchain
				for x in sendchain2:
					sendchaincomplete.append(x)
				sendchaincomplete.append(sendchain3)
				try:
					self.device.flushInput()
					self.device.flushOutput()
					self.device.write(serial.to_bytes(sendchaincomplete))
					response = self.device.readline()
					if response[5:7].hex() == '0c00':
						return(True)
					else:
						return(False)
				except:
					return(False)

			if send1(data) == True:
				if send2(data) == True:
					if str(self.read()) == str(data):
						return(True)
					else:
						return(False)
				else:
					return(False)
			else:
				return(False)

		else:
			raise Exception('You must initialise the device in order to read or write data.')
