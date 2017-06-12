To run the program:
====================
Run server.py first, then run client.py
My python version is 2.7.10
For server.py, the running command line is
python server.py -sp <port>

For client.py, the running command line is:
python client.py -u Alice -sip server-ip -sp <port>
if server is not online, there would be an error message. Quit the program by using command <bye>

To list the current logged in clients, type list after running the client.py
To send the message to other clients, type
send <client Username> <message>	

where <port> is any normal unused numbered port between 1-65535
    
HIGH LEVEL APPROACH:
1. Client
    The client uses multithread programming to deal with listening and sending at the same time. The listening thread is the daemon thread for client.
    A sign in message is sent to the server when the client program starts
    commands:
    list command asks the server of the current logged in users.
    send command send the message to the users existing. The server replies to the client with receiver info for making direct client message sending.
    bye command ends the client program	and deletes the info stored in the server.

2. Server
    When receiving the sign-in message, send command, and list command, the server takes the action depends on the header of each type of the command.
    The server sends the Client with the correct receiver's information when receiving the send command. The server ends by key interrupt