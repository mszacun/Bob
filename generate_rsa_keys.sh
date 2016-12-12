openssl genrsa -out server_private_key.pem 1024
openssl genrsa -out client_private_key.pem 1024

openssl rsa -in server_private_key.pem -outform PEM -pubout -out server_public_key.pem
openssl rsa -in client_private_key.pem -outform PEM -pubout -out client_public_key.pem
