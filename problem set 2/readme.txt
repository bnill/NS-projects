To run the program:
====================
Create two pairs of RSA keys first, then run
python fcrypt.py -e destination_public_key_filename sender_private_key_filename input_plaintext_file ciphertext_file
to encrypt the file

python fcrypt.py -d destination_private_key_filename sender_public_key_filename ciphertext_file output_plaintext_file
to decrypt the file

My python version is 2.7.10
The key format used in the program is .pem
To create the key pairs, use the following commands:
openssl genrsa -out sender_private_key.pem 2048
openssl rsa -in sender_private_key.pem -pubout -outform PEM -out sender_public_key.pem

openssl genrsa -out dest_private_key.pem 2048
openssl rsa -in dest_private_key.pem -pubout -outform PEM -out dest_public_key.pem
key size can be changed
    
HIGH LEVEL APPROACH:
1. Encryption
    The program first judge whether the given file is a text file by file extensions. For text file we use "r" and "w" parameters to read and write. For
    other files we use "rb" and "wb" to read and write. Then we use AES algorithm to encrypt the file. Encrypt the symmetric key created by AES by destination
    public key. Sign the message by sender_private_key to create the signature. Finally add the signature, encrypted symmetric key, IV, encrypted text, binary_flag
    encoded by b64 to the cipher_file waiting to be decrypted.

2. Decryption
    After receiving the cipher_file, we first divide them into five parts: signature, encrypted symmetric key, IV, encrypted_text and binary_flag. We verify the signature
    by sender public flag and sign_message retrieved. Then we decrypt the AES symmetric key using dest_private_key and IV. Use the decrypted symmetric key to decrypt the 
    text we want. Finally, if the binary_flag == 1 then use "wb" to write the output file. Else use "w" to write.