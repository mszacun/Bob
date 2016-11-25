import os
from itertools import cycle

from hexdump import dump, dehex

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from encryption.base import CipherWithoutKey, ShiftBasedCipher, SingleKeyCipher


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


class AESCipher(SingleKeyCipher):
    ALLOWED_KEY_LENGTHS = [16, 24, 32]
    BLOCK_SIZE = 16
    RECOMMENDED_KEY_LENGTH = 32
    IV_LENGTH = BLOCK_SIZE
    ENCRYPTION_NAME = 'AES'

    returns_binary_data = True

    def __init__(self, key, iv):
        super(AESCipher, self).__init__(key)

        self.iv = iv
        self.cipher = Cipher(algorithms.AES(key), modes.CBC(iv), default_backend())
        self.encryptor = self.cipher.encryptor()
        self.decryptor = self.cipher.decryptor()
        self.padding = padding.PKCS7(self.BLOCK_SIZE * 8)

    def encrypt(self, plaintext):
        padded_data = self._pad(plaintext)
        return self.encryptor.update(padded_data)

    def encrypt_binary(self, plaintext, is_last_chunk):
        if is_last_chunk and (len(plaintext) % self.BLOCK_SIZE != 0):
            plaintext = self._pad(plaintext)

        return self.encryptor.update(plaintext)

    def decrypt(self, ciphertext):
        decrypted_data = self.decryptor.update(ciphertext)
        return self._unpad(decrypted_data)

    def decrypt_binary(self, ciphertext, is_last_chunk):
        plaintext = self.decryptor.update(ciphertext)
        if is_last_chunk and (len(ciphertext) % self.BLOCK_SIZE != 0):
            plaintext = self._unpad(plaintext)

        return plaintext

    def _pad(self, block):
        padder = self.padding.padder()
        return padder.update(block) + padder.finalize()

    def _unpad(self, block):
        unpadder = self.padding.unpadder()
        return unpadder.update(block) + unpadder.finalize()

    def serialize(self):
        return {'name': self.ENCRYPTION_NAME, 'key': dump(self.key), 'iv': dump(self.iv)}

    @classmethod
    def deserialize(cls, encryption_params):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        return cls(key=dehex(encryption_params['key']), iv=dehex(encryption_params['iv']))

    def __str__(self):
        return '{} (key: {}, IV: {})'.format(self.ENCRYPTION_NAME, dump(self.key, sep=''), dump(self.iv, sep=''))
