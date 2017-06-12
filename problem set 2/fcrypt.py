import sys, random, os, base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# function to encrypt the symmetric key using dest_public_file
def encrypt_sym_key(sender_symmetric_key, dest_public_key_file):
	#loading sender_private_key
	with open(dest_public_key_file, "rb") as key_file:
		dest_public_key = load_pem_public_key(
			key_file.read(),
			backend = default_backend()
			)
	cipher_sender_symmetric_key = dest_public_key.encrypt(
		sender_symmetric_key,
		padding.OAEP(
			mgf = padding.MGF1(algorithm=hashes.SHA256()),
			algorithm=hashes.SHA1(),
			label=None))
	return base64.b64encode(cipher_sender_symmetric_key)

# function to sign the messege
def sign_message(sender_private_key_file, cipher_text):
	with open(sender_private_key_file, "rb") as key_file:
		sender_private_key = serialization.load_pem_private_key(
		key_file.read(),
		password = None,
		backend = default_backend()
		)
	signature = sender_private_key.sign(
		cipher_text,
		padding.PSS(
			mgf = padding.MGF1(hashes.SHA256()),
			salt_length = padding.PSS.MAX_LENGTH),
		hashes.SHA256()
		)
	return base64.b64encode(signature)	

# function to verify the signature
def verify_signature(signature, sender_public_key_file, sign_message):
	try:
		with open(sender_public_key_file, "rb") as key_file:
			sender_public_key = load_pem_public_key(
				key_file.read(),
				backend = default_backend()
				)
		sender_public_key.verify(
			signature,
			sign_message,
			padding.PSS(
				mgf = padding.MGF1(hashes.SHA256()),
				salt_length = padding.PSS.MAX_LENGTH),
			hashes.SHA256())
	except:
		print "Error: verification of signature failed!"
		exit()	

# function to decrypt for AES key
def sym_key_decryption(dest_private_key_file, cipher_sym_key):
	try:
		with open(dest_private_key_file, "rb") as key_file:
			dest_private_key = serialization.load_pem_private_key(
				key_file.read(),
				password = None,
				backend = default_backend()
				)
		sym_key = dest_private_key.decrypt(
			cipher_sym_key,
			padding.OAEP(
				mgf = padding.MGF1(algorithm = hashes.SHA256()),
				algorithm = hashes.SHA1(),
				label = None))
	except:
		print "Error: decryption of AES key failed!"
		exit()
	return sym_key

def encryption(dest_public_key_file, sender_private_key_file, input_plaintext, cipher_text_file):
	sender_symmetric_key = os.urandom(16) # create the symmetric key for sender in bytes, 128 bits
	#the encryption for the sender_symmetric_key starts here. we use the dest_public_key_file to encrypt the sender_symmetric_key

	#encrypt the symmetric key using dest_public_file
	encoded_cipher_symmetric_key = encrypt_sym_key(sender_symmetric_key, dest_public_key_file)
	# encryption of symmetric_key ends here
	initialization_vector = os.urandom(16) # initialization vector to apply AES algorithm
	encoded_iv = base64.b64encode(initialization_vector)
	cipher = Cipher(algorithms.AES(sender_symmetric_key), modes.CTR(initialization_vector), backend = default_backend())
	# use CTR mode for cryption 
	encryptor = cipher.encryptor()

	# judge the given file is a text file or binary file by file_extension
	if(os.path.splitext(input_plaintext)[1] == ".txt"):		
		try:
			text_object = open(input_plaintext, 'r')
			text = text_object.read()
			binary_flag = 0
			#print text
		except:
			print "Error: File does not exist!"
			exit()
	else:
		try:
			text_object = open(input_plaintext, 'rb')
			text = text_object.read()
			binary_flag = 1
			#print text
		except:
			print "Error: File does not exist!"
			exit()
	cipher_text = encryptor.update(text) + encryptor.finalize()
	#print base64.b64encode(cipher_text)
	encoded_cipher_text = base64.b64encode(cipher_text)
	#enbed the encoded_cipher_symmetric_key and encoded_cipher_text and separate with " "
	cipher_text = encoded_cipher_symmetric_key + " " + encoded_cipher_text
	#print cipher_text

	# signing process starts here
	encoded_signature = sign_message(sender_private_key_file, cipher_text)
	# construction of cipher text
	cipher_text = encoded_signature + " " + cipher_text + " " + encoded_iv + " " + str(binary_flag)

	cipher_text_obj = open(cipher_text_file, "w")
	cipher_text_obj.write(cipher_text)
	cipher_text_obj.close()
	# write to the filename given by the args, end of symmetric encryption


def decryption(dest_private_key_file, sender_public_key_file, cipher_text_file, output_plaintext):
	with open(cipher_text_file, "r") as keyfile:
		recv_cipher_text = keyfile.read()
	tmp_recv_cipher_text = recv_cipher_text.split()
	signature = tmp_recv_cipher_text[0]
	cipher_sym_key = tmp_recv_cipher_text[1]
	cipher_text = tmp_recv_cipher_text[2]
	iv = tmp_recv_cipher_text[3]
	binary_flag = int(tmp_recv_cipher_text[4])
	sign_message = cipher_sym_key + " " + cipher_text
	signature = base64.b64decode(signature)
	cipher_sym_key = base64.b64decode(cipher_sym_key)
	cipher_text = base64.b64decode(cipher_text)
	iv = base64.b64decode(iv)
	#verification of signature
	verify_signature(signature, sender_public_key_file, sign_message)

	#decryption of AES key
	sym_key = sym_key_decryption(dest_private_key_file, cipher_sym_key)

	#decryption of cipher_text_file
	cipher = Cipher(algorithms.AES(sym_key), modes.CTR(iv), backend = default_backend())
	decryptor = cipher.decryptor()
	output = decryptor.update(cipher_text) + decryptor.finalize()

	# write to output file based on binary flag
	if(binary_flag == 1):
		output_plaintext_obj = open(output_plaintext, "wb")
		output_plaintext_obj.write(output)
		output_plaintext_obj.close()
	if(binary_flag == 0):
		output_plaintext_obj = open(output_plaintext, "w")
		output_plaintext_obj.write(output)
		output_plaintext_obj.close()

sys_arg_length = len(sys.argv)
operation_flag = sys.argv[1]
if operation_flag == "-e":
	if sys_arg_length != 6:
		print "Error: the number of parameters not correct!"
		exit()
	if (os.path.isfile(sys.argv[2]) == False or os.path.isfile(sys.argv[3]) == False or os.path.isfile(sys.argv[4]) == False):
		print "Error: essential file does not exist!"
		exit()
	encryption(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
elif operation_flag == "-d":
	if sys_arg_length != 6:
		print "Error: the number of parameters not correct!"
		exit()
	if (os.path.isfile(sys.argv[2]) == False or os.path.isfile(sys.argv[3]) == False or os.path.isfile(sys.argv[4]) == False):
		print "Error: essential file does not exist!"
		exit()
	decryption(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
else:
	print "Error: check the operation flag and try again!"
	exit()