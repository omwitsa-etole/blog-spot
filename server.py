import os
from pyfiglet import Figlet
os.system("clear")
pyf = Figlet(font='puffy')
a = pyf.renderText("UDP Chat App with Multi-Threading")
os.system("tput setaf 3")
print(a)
import socket, cv2, pickle, struct, threading, time
# Socket Create

class Serve:
	def __init__(self):
		self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		

	def sender(self, host_name):
		host_name  = socket.gethostname()
		host_ip = socket.gethostbyname(host_name)
		print('Host IP:'+host_ip)
		port = 9999
		socket_address = (host_ip,port)
		# Socket Bind
		self.s.bind(socket_address)
		# Socket Listen
		self.s.listen(5)
		print("Listening at:",socket_address)
		while True:
			client_socket,addr = self.s.accept()
			print('Connection to:',addr)
			if client_socket:
				vid = cv2.VideoCapture(0)

				while(vid.isOpened()):
					ret,image = vid.read()
					img_serialize = pickle.dumps(image)
					message = struct.pack("Q",len(img_serialize))+img_serialize
					client_socket.sendall(message)

					cv2.imshow('Video from server', image)
					key = cv2.waitKey(10) 
					if key ==13:
						client_socket.close()
		self.Audio(host_name)
	def Audio(self, IP):
		chunk = 1024
		FORMAT = pyaudio.paInt16
		CHANNELS = 1
		RATE = 44100
		p = pyaudio.PyAudio()
		self.stream = p.open(format = FORMAT,
				channels = CHANNELS,
				rate = RATE,
				input = True,
				frames_per_buffer = chunk)
		#Audio Socket Initialization
		audioSocket = socket.socket()
		port1 = 5000
		audioSocket.bind((IP,port1))
		audioSocket.listen(5)
		cAudio, addr = audioSocket.accept()

	
	def recordAudio(self):
		time.sleep(5)
		while True:
			data = self.stream.read(chunk)
			if data:
				cAudio.sendall(data)
	def rcvAudio(self):
		while True:
			audioData = audioSocket.recv(size)
			self.stream.write(audioData)
	def connect_server(self, IP):
		host_ip = IP 
		port = 1234
		s.connect((host_ip,port)) 
		data = b""
		metadata_size = struct.calcsize("Q")
		while True:
			while len(data) < metadata_size:
				packet = s.recv(4*1024) 
				if not packet: break
				data+=packet
			packed_msg_size = data[:metadata_size]
			data = data[metadata_size:]
			msg_size = struct.unpack("Q",packed_msg_size)[0]
	 
			while len(data) < msg_size:
				data += s.recv(4*1024)
			frame_data = data[:msg_size]
			data  = data[msg_size:]
			frame = pickle.loads(frame_data)
			cv2.imshow("Receiving Video",frame)
			key = cv2.waitKey(10) 
			if key  == 13:
				break
		s.close()
a = Serve()
x3 = threading.Thread(target = a.sender('197.232.61.196'))
#x4 = threading.Thread(target = a.Audio('197.232.61.196'))
x2 = threading.Thread(target = a.connect_server('197.232.61.196'))
x3 = threading.Thread(target = a.recordAudio)
x4 = threading.Thread(target = a.rcvAudio)
# start a thread
x1.start()
x2.start()
x3.start()
x4.start()
