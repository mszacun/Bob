from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from encryption.ciphers import SzacunProductionRSACipher


def hash_bytes(bytes_to_hash, hash_algorithm=hashes.SHA512()):
    digest = hashes.Hash(hash_algorithm, backend=default_backend())
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


class CertificateVerificationResult(object):
    def __init__(self, received_certificate, ca_public_key, my_private_key):
        self.calculated_hash = hash_bytes(received_certificate.tbs_certificate_bytes,
                                          received_certificate.signature_hash_algorithm)
        hash_len = len(self.calculated_hash)
        self.received_certificate = received_certificate
        self.received_hash = decrypt_signature(received_certificate.signature, ca_public_key, my_private_key)[-hash_len:]

