import sys, socket
from threading import Thread
import random

username = ""
host = ""
port = random.randint(40000, 65535)
message_to_send = ""
#print port
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#function for receiving message from the server
def listen():
	global message_to_send
	while True:
		try:
			message, addr = sock.recvfrom(4096)
		except:
			print "Error: Server not online!"
			exit()
		split_msg = message.split()
		if(split_msg[0] == "Signed" and split_msg[1] == "In" and split_msg[2] == "Users:"):
			print message
		elif(split_msg[0] == "receiver_info:"):
			#print message
			out_message = ""
			#for word in split_msg[8:]:
				#out_message += word + " "
			output_message = "<From " + split_msg[4] + ":Port:" + split_msg[5] + ":" + username + ">: "
			output_message = "<- " + output_message + message_to_send
			destination = (split_msg[2], int(split_msg[3]))
			#print destination
			try:
				sock.sendto(output_message, destination)
			except:
				print ("Error: Socket error")
				exit()
		else:
			print message

def send_message(server_ip, server_port):
	global message_to_send
	server = (server_ip, server_port)
	while True:
		input_message = raw_input("+> ")
		#print input_message
		split_message = input_message.split()
		if(input_message == "bye"):
			sock.sendto(input_message, server)
			exit()
		if(input_message == "list"):
			sock.sendto(input_message, server)
		elif(len(split_message) < 3):
			print("Error: invalid input for client! Please try again!")
		elif(split_message[0] == "send" and len(split_message) >= 3):
			#input_message = "sender: " + username + " " + input_message
			# check if the size exceeds the UDP packet size
			if(sys.getsizeof(input_message) >= 65535):
				print "Error: message size too big!"
				exit()
			message_to_send = ""
			for word in split_message[2:]:
				message_to_send += word + " "
			try:
				sock.sendto(input_message, server)
			except:
				print ("Error: Socket error")
				exit()
		else:
			print("Error: invalid input for client! Please try again!")

sys_arg_length = len(sys.argv)
# correct input format: python client.py -u Alice -sip server-ip -sp 9090
if sys_arg_length != 7:
	print "Error: Wrong number of parameters"
	exit()
elif(sys.argv[1] != "-u" or sys.argv[3] != "-sip" or sys.argv[5] != "-sp"):
	print "Error: Wrong parameters!"
	exit()
elif(int(sys.argv[6]) > 65535):
	print "port number too large!"
	exit()

username = sys.argv[2]
server_ip = sys.argv[4]
server_port = int(sys.argv[6])
#bind the port for UDP connection
sock.bind((host, port))
#send the sign_in message when run
signin_message = username + " signed_in"
if(sys.getsizeof(signin_message) >= 65535):
	print "Error: message size too big!"
	exit()
try:
	sock.sendto(signin_message, (server_ip, server_port))
except:
	print ("Error: Socket error not online!")
	exit()
#print localhost
#print username
#print server_ip
#print server_port
t1 = Thread(target = listen)
t2 = Thread(target = send_message, args = (server_ip, server_port))
t1.setDaemon(True)
t1.start()
t2.start()