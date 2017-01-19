BOB_LOCATION=`pwd`
PKI_LOCATION="$BOB_LOCATION/pki"

SERVER_NAME=$1
CERTIFICATE_TYPE=$2

echo "Creating certificate"
cd key_build
mkdir $SERVER_NAME
cd $SERVER_NAME
cp -r /etc/easy-rsa ./
cd easy-rsa

easyrsa init-pki
easyrsa gen-req $SERVER_NAME nopass

echo "Signing certificate"
cd ../../ca/easy-rsa/

easyrsa import-req ../../$SERVER_NAME/easy-rsa/pki/reqs/$SERVER_NAME.req $SERVER_NAME
easyrsa sign-req $CERTIFICATE_TYPE $SERVER_NAME

mkdir $PKI_LOCATION/$SERVER_NAME
cp $BOB_LOCATION/key_build/ca/easy-rsa/pki/issued/$SERVER_NAME.crt $PKI_LOCATION/$SERVER_NAME
cp $BOB_LOCATION/key_build/$SERVER_NAME/easy-rsa/pki/private/$SERVER_NAME.key $PKI_LOCATION/$SERVER_NAME
