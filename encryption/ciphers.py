from itertools import cycle

from hexdump import dump, dehex

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives import hashes

from encryption.base import CipherWithoutKey, ShiftBasedCipher, SingleKeyCipher, BlockCipher, RSACipher, \
     NotThisEncryptionSerialized


class NoneEncryption(CipherWithoutKey):
    ENCRYPTION_NAME = 'None'
    returns_binary_data = False

    def encrypt(self, plaintext):
        return plaintext

    def encrypt_binary(self, plaintext, is_last_chunk):
        return plaintext

    def decrypt(self, ciphertext):
        return ciphertext

    def decrypt_binary(self, ciphertext, is_last_chunk):
        return ciphertext


class CaesarCipher(ShiftBasedCipher, SingleKeyCipher):
    ENCRYPTION_NAME = 'Caesar cipher'
    returns_binary_data = False

    def encrypt(self, plaintext):
        return ''.join(self._shift_character(c, self.key) for c in plaintext)

    def encrypt_binary(self, plaintext, is_last_chunk):
        return ''.join(self._shift_binary_character(c, self.key) for c in plaintext)

    def decrypt(self, ciphertext):
        return ''.join(self._shift_character(c, -self.key) for c in ciphertext)

    def decrypt_binary(self, ciphertext, is_last_chunk):
        return ''.join(self._shift_binary_character(c, -self.key) for c in ciphertext)


class Rot13Cipher(CipherWithoutKey, CaesarCipher):
    KEY = 13
    ENCRYPTION_NAME = 'Rot13 Cipher'

    def __init__(self):
        CaesarCipher.__init__(self, Rot13Cipher.KEY)


class VigenereCipher(ShiftBasedCipher, SingleKeyCipher):
    ENCRYPTION_NAME = 'Vigenere cipher'
    returns_binary_data = False

    def encrypt(self, plaintext):
        return ''.join(self._shift_character(c, self._calculate_shift(key_letter))
                       for c, key_letter in zip(plaintext, cycle(self.key)))

    def encrypt_binary(self, plaintext, is_last_chunk):
        return ''.join(self._shift_binary_character(c, self._calculate_shift(key_letter))
                       for c, key_letter in zip(plaintext, cycle(self.key)))

    def decrypt(self, ciphertext):
        return ''.join(self._shift_character(c, -self._calculate_shift(key_letter))
                       for c, key_letter in zip(ciphertext, cycle(self.key)))

    def decrypt_binary(self, ciphertext, is_last_chunk):
        return ''.join(self._shift_binary_character(c, -self._calculate_shift(key_letter))
                       for c, key_letter in zip(ciphertext, cycle(self.key)))

    def _calculate_shift(self, key_letter):
        return self.UPPER_LETTERS.index(key_letter)


class AESCipher(SingleKeyCipher, BlockCipher):
    ALLOWED_KEY_LENGTHS = [16, 24, 32]
    BLOCK_SIZE = 16
    RECOMMENDED_KEY_LENGTH = 32
    IV_LENGTH = BLOCK_SIZE
    ENCRYPTION_NAME = 'AES'

    returns_binary_data = True

    def __init__(self, key, iv, his_public_key=None, my_private_key=None):
        super(AESCipher, self).__init__(key)

        self.iv = iv
        self.cipher = Cipher(algorithms.AES(key), modes.CBC(iv), default_backend())
        self.encryptor = self.cipher.encryptor()
        self.decryptor = self.cipher.decryptor()
        self.padding = padding.PKCS7(self.BLOCK_SIZE * 8)

        self.his_public_key = his_public_key
        self.my_private_key = my_private_key

    def encrypt(self, plaintext):
        padded_data = self._pad(plaintext, self.padding)
        return self.encryptor.update(padded_data)

    def encrypt_binary(self, plaintext, is_last_chunk):
        if is_last_chunk and (len(plaintext) % self.BLOCK_SIZE != 0):
            plaintext = self._pad(plaintext, self.padding)

        return self.encryptor.update(plaintext)

    def decrypt(self, ciphertext):
        decrypted_data = self.decryptor.update(ciphertext)
        return self._unpad(decrypted_data, self.padding)

    def decrypt_binary(self, ciphertext, is_last_chunk):
        plaintext = self.decryptor.update(ciphertext)
        if is_last_chunk:
            plaintext = self._unpad(plaintext, self.padding)

        return plaintext

    def serialize(self):
        encryption_params = {'name': self.ENCRYPTION_NAME, 'iv': dump(self.iv)}
        if self.his_public_key and self.my_private_key:
            encrypted_key = SzacunProductionRSACipher(self.his_public_key, self.my_private_key).encrypt(dump(self.key))
            encryption_params['key'] = dump(encrypted_key)
            encryption_params['is_key_encrypted'] = True
        else:
            encryption_params['key'] = dump(self.key)
            encryption_params['is_key_encrypted'] = False

        return encryption_params

    @classmethod
    def deserialize(cls, encryption_params, his_public_key, my_private_key):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        if encryption_params['is_key_encrypted']:
            key = SzacunProductionRSACipher(his_public_key, my_private_key).decrypt(dehex(encryption_params['key']))
        else:
            key = encryption_params['key']

        return cls(key=dehex(key), iv=dehex(encryption_params['iv']))

    def __str__(self):
        return '{} (key: {}, IV: {})'.format(self.ENCRYPTION_NAME, dump(self.key, sep=''), dump(self.iv, sep=''))


class SzacunProductionRSACipher(RSACipher):
    ENCRYPTION_NAME = 'SzacunProductionRSACipher'

    def __init__(self, his_public_key, my_private_key):
        super(SzacunProductionRSACipher, self).__init__(his_public_key, my_private_key)

        self.outcoming_padder = padding.PKCS7((self.outcoming_block_size - 1) * 8)
        self.incoming_padder = padding.PKCS7((self.incoming_block_size - 1) * 8)

    def encrypt_binary(self, plaintext, is_last_chunk):
        if is_last_chunk:
            plaintext = self._pad(plaintext, self.outcoming_padder)

        blocks = self._split_into_blocks(plaintext, self.outcoming_block_size - 1)
        encrypted_blocks = [self._encrypt_block(block) for block in blocks]

        return ''.join(encrypted_blocks)

    def decrypt_binary(self, ciphertext, is_last_chunk):
        blocks = self._split_into_blocks(ciphertext, self.incoming_block_size)
        decrypted_blocks = [self._decrypt_block(block) for block in blocks]

        plaintext = ''.join(decrypted_blocks)
        if is_last_chunk:
            plaintext = self._unpad(plaintext, self.incoming_padder)

        return plaintext

    def _decrypt_block(self, block):
        as_int = self._bytes_to_int(block)
        decrypted = self._decrypt_int(as_int)

        return self._int_to_bytes(decrypted, self.incoming_block_size - 1)

    def _encrypt_block(self, block):
        as_int = self._bytes_to_int(block)
        encrypted = self._encrypt_int(as_int)

        return self._int_to_bytes(encrypted, self.outcoming_block_size)

    def _bytes_to_int(self, bytes):
        return int(dump(bytes, sep=''), 16)

    def _decrypt_int(self, integer):
        n = self.my_private_key_n
        d = self.my_private_key.private_numbers().d

        return pow(integer, d, n)

    def _encrypt_int(self, integer):
        n = self.his_public_key.public_numbers().n
        e = self.his_public_key.public_numbers().e

        return pow(integer, e, n)

    def _int_to_bytes(self, integer, block_length):
        bytes = []
        if integer == 0:
            bytes = ['\x00']

        while integer > 0:
            bytes.insert(0, chr(integer & 0xFF))
            integer >>= 8

        required_padding = (block_length - len(bytes))
        bytes = ['\x00'] * required_padding + bytes

        return ''.join(bytes)

    def __str__(self):
        return 'SzacunProductionRSACipher'


class LibraryRSACipher(RSACipher):
    ENCRYPTION_NAME = 'LibraryRSACipher'

    def __init__(self, his_public_key, my_private_key):
        super(LibraryRSACipher, self).__init__(his_public_key, my_private_key)

        self.hash_algorithm = hashes.SHA1()
        self.padding = asymmetric_padding.OAEP(mgf=asymmetric_padding.MGF1(algorithm=self.hash_algorithm),
                                               algorithm=self.hash_algorithm, label=None)

        self.outcoming_message_size = self.outcoming_block_size - 2 * self.hash_algorithm.digest_size - 2

    def encrypt_binary(self, plaintext, is_last_chunk):
        blocks = self._split_into_blocks(plaintext, self.outcoming_message_size)
        encrypted_blocks = [self._encrypt_block(block) for block in blocks]

        return ''.join(encrypted_blocks)

    def decrypt_binary(self, ciphertext, is_last_chunk):
        blocks = self._split_into_blocks(ciphertext, self.incoming_block_size)
        decrypted_blocks = [self._decrypt_block(block) for block in blocks]

        plaintext = ''.join(decrypted_blocks)

        return plaintext

    def _encrypt_block(self, block):
        return self.his_public_key.encrypt(block, self.padding)

    def _decrypt_block(self, block):
        return self.my_private_key.decrypt(block, self.padding)

    def __str__(self):
        return 'LibraryRSACipher'
