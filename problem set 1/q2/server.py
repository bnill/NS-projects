import sys, socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = ""
user_list = []

def ListenToClient():
	global user_list
	while True:
		#print "Waiting for message from client"
		msg, addr = sock.recvfrom(4096)
		#print "message received from: " + str(addr)
		#print "content: " + msg
		split_msg = msg.split()
		#add signed_in client and the ip address and port to client list
		if(len(split_msg) == 1 and msg == "bye"):
			for user_info in user_list:
				if addr == user_info[1]:
					user_list.remove(user_info)
		if(len(split_msg) == 2 and split_msg[1] == "signed_in"):
			sign_in(split_msg, addr)
		#send the list of users to the client corresponding to the command 'list'
		if(len(split_msg) == 1 and msg == "list"):
			get_list(split_msg, addr)
		elif(len(split_msg) >= 3 and split_msg[0] == "send"):
			send_message(split_msg, addr, msg)
# function to deal with sign in messages
def sign_in(split_msg, addr):
	global user_list
	#check for duplicate
	tmp_user_info = (split_msg[0], addr)
	if tmp_user_info not in user_list:
		user_list.append((split_msg[0], addr))
		#check for new login from different ip and port and update
		for uinfo in user_list:
			if tmp_user_info[0] == uinfo[0] and tmp_user_info != uinfo:
				user_list.remove(uinfo)
				break
# get all sign_in users function
def get_list(split_msg, addr):
	global user_list
	output_message = "<- Signed In Users: "
	usernames = ""
	for user in user_list:
		usernames += user[0] + " "
	output_message = output_message + usernames
	#print output_message
	#print addr
	sock.sendto(output_message, addr)
	#print "list message sent"	
# function to send receiver info
def send_message(split_msg, addr, msg):
	global user_list
	# find the sign_in information from user_list of the message sender and receiver
	receiver_info = ()
	sender_info = ()
	for user_info in user_list:
		if(split_msg[1] == user_info[0]):
			receiver_info = user_info
	if receiver_info == ():
		output_message = "Error: the receiver does not exist! Try again!"
		sock.sendto(output_message, addr)
	else:
		out_message = "receiver_info: " + receiver_info[0] + " " + str(receiver_info[1][0]) + " " + str(receiver_info[1][1]) + " " + str(addr[0]) + " " + str(addr[1])
		sock.sendto(out_message, addr)
		#print "message sent!"	

#correct input format: python server.py -sp 9090
sys_arg_length = len(sys.argv)
if(sys_arg_length != 3):
	print "Error: Wrong number of parameters!"
	exit()
elif(sys.argv[1] != "-sp"):
	print "Error: Wrong parameters!"
	exit()
elif(int(sys.argv[2]) > 65535):
	print "port number too large!"
	exit()

server_port = int(sys.argv[2])
sock.bind((host, server_port))

print "Server initialized..."
ListenToClient()