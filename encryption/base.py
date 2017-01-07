from itertools import izip_longest
import math

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

class NotThisEncryptionSerialized(Exception):
    pass


class CipherWithoutKey(object):
    def serialize(self):
        return {'name': self.ENCRYPTION_NAME}

    @classmethod
    def deserialize(cls, encryption_params, his_public_key, my_private_key):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        return cls()

    def __str__(self):
        return self.ENCRYPTION_NAME


class SingleKeyCipher(object):
    def __init__(self, key):
        self.key = key

    def serialize(self):
        return {'name': self.ENCRYPTION_NAME, 'key': self.key}

    @classmethod
    def deserialize(cls, encryption_params, his_public_key, my_private_key):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        return cls(key=encryption_params['key'])

    def __str__(self):
        return '{} (key: {})'.format(self.ENCRYPTION_NAME, self.key)


class ShiftBasedCipher(object):
    LOWER_LETTERS = 'abcdefghijklmnopqrstuvwxyz'
    UPPER_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    DIGITS = '0123456789'

    def _shift_character(self, character, shift):
        if character in self.LOWER_LETTERS:
            return self._shift_using_alphabet(character, self.LOWER_LETTERS, shift)

        if character in self.UPPER_LETTERS:
            return self._shift_using_alphabet(character, self.UPPER_LETTERS, shift)

        if character in self.DIGITS:
            return self._shift_using_alphabet(character, self.DIGITS, shift)

        return character

    def _shift_using_alphabet(self, character, alphabet, shift):
        index = alphabet.index(character)
        shifted = index + shift
        redundant_shifted = shifted + len(alphabet) # Removes problem with negative numbers during decrypting
        based = redundant_shifted % len(alphabet)

        return alphabet[based]

    def _shift_binary_character(self, character, shift):
        shifted = ord(character) + shift
        redundant_shifted = shifted + 256

        return chr(redundant_shifted % 256)


class BlockCipher(object):
    def _pad(self, block, padding):
        padder = padding.padder()
        return padder.update(block) + padder.finalize()

    def _unpad(self, block, padding):
        try:
            unpadder = padding.unpadder()
            return unpadder.update(block) + unpadder.finalize()
        except:
            return block


class RSACipher(BlockCipher):
    returns_binary_data = True

    def __init__(self, his_public_key, my_private_key):
        self.his_public_key = serialization.load_pem_public_key(his_public_key, default_backend())
        self.my_private_key = serialization.load_pem_private_key(my_private_key, None, default_backend())

        self.his_public_key_length = self._get_integer_byte_size(self.his_public_key.public_numbers().n)

        self.my_private_key_n = self.my_private_key.private_numbers().q * self.my_private_key.private_numbers().p
        self.my_private_key_length = self._get_integer_byte_size(self.my_private_key_n)

        self.outcoming_block_size = self.his_public_key_length
        self.incoming_block_size = self.my_private_key_length

        self.preferred_file_chunk = self.outcoming_block_size - 1

    def encrypt(self, plaintext):
        return self.encrypt_binary(plaintext, True)

    def decrypt(self, ciphertext):
        return self.decrypt_binary(ciphertext, True)

    def _get_integer_byte_size(self, number):
        return int(math.ceil(number.bit_length() / 8.0))

    def _split_into_blocks(self, iterable, n, fillvalue=''):
        "Collect data into fixed-length chunks or blocks"
        args = [iter(iterable)] * n
        for chunk in izip_longest(fillvalue=fillvalue, *args):
            yield ''.join(chunk)

    def serialize(self):
        return {'name': self.ENCRYPTION_NAME}

    @classmethod
    def deserialize(cls, encryption_params, his_public_key, my_private_key):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        return cls(his_public_key, my_private_key)

    def __str__(self):
        return '{} (key: {}, IV: {})'.format(self.ENCRYPTION_NAME, dump(self.key, sep=''), dump(self.iv, sep=''))
