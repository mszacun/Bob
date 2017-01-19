mkdir key_build

BOB_LOCATION=`pwd`
PKI_LOCATION="$BOB_LOCATION/pki"

mkdir $PKI_LOCATION

# CA
mkdir key_build/ca
cp -r /etc/easy-rsa key_build/ca
cd key_build/ca/easy-rsa

echo "Creating CA certificates"
easyrsa init-pki
easyrsa build-ca nopass

mkdir $PKI_LOCATION/ca
cp pki/ca.crt $PKI_LOCATION/ca
cp private/ca.key $PKI_LOCATION/ca
cd ../../../

sh create_certificate.sh server1 server
sh create_certificate.sh client1 client
