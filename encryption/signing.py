from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from encryption.ciphers import SzacunProductionRSACipher


def hash_bytes(bytes_to_hash):
    digest = hashes.Hash(hashes.SHA512(), backend=default_backend())
    digest.update(bytes_to_hash)

    return digest.finalize()

def sign_bytes(bytes_to_sign, his_public_key, my_private_key):
    return SzacunProductionRSACipher(his_public_key, my_private_key, swap_keys=True).encrypt(hash_bytes(bytes_to_sign))

def decrypt_signature(signature, his_public_key, my_private_key):
    return SzacunProductionRSACipher(his_public_key, my_private_key, swap_keys=True).decrypt(signature)
