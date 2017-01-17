from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from encryption.ciphers import SzacunProductionRSACipher


def hash_bytes(bytes_to_hash):
    digest = hashes.Hash(hashes.SHA512(), backend=default_backend())
    digest.update(bytes_to_hash)

    return digest.finalize()

def hash_file(filepath):
    with open(filepath, 'r') as f:
        return hash_bytes(f.read())

def sign_hash(hashsum, his_public_key, my_private_key):
    return SzacunProductionRSACipher(his_public_key, my_private_key, swap_keys=True).encrypt(hashsum)

def sign_bytes(bytes_to_sign, his_public_key, my_private_key):
    return sign_hash(hash_bytes(bytes_to_sign), his_public_key, my_private_key)

def sign_file(filepath, his_public_key, my_private_key):
    return sign_hash(hash_file(filepath), his_public_key, my_private_key)

def decrypt_signature(signature, his_public_key, my_private_key):
    return SzacunProductionRSACipher(his_public_key, my_private_key, swap_keys=True).decrypt(signature)
