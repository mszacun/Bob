from itertools import cycle

from cryptography.base import NoKeyCipher, ShiftBasedCipher, SingleKeyCipher


class NoneEncryption(NoKeyCipher):
    ENCRYPTION_NAME = 'None'

    def encrypt(self, plaintext):
        return plaintext

    def encrypt_binary(self, plaintext):
        return plaintext

    def decrypt(self, ciphertext):
        return ciphertext

    def decrypt_binary(self, ciphertext):
        return ciphertext


class CaesarCipher(ShiftBasedCipher, SingleKeyCipher):
    ENCRYPTION_NAME = 'Caesar cipher'

    def encrypt(self, plaintext):
        return ''.join(self._shift_character(c, self.key) for c in plaintext)

    def encrypt_binary(self, plaintext):
        return ''.join(self._shift_binary_character(c, self.key) for c in plaintext)

    def decrypt(self, ciphertext):
        return ''.join(self._shift_character(c, -self.key) for c in ciphertext)

    def decrypt_binary(self, ciphertext):
        return ''.join(self._shift_binary_character(c, -self.key) for c in ciphertext)


class Rot13Cipher(CaesarCipher, NoKeyCipher):
    KEY = 13
    ENCRYPTION_NAME = 'Rot13 Cipher'

    def __init__(self):
        super(Rot13Cipher, self).__init__(Rot13Cipher.KEY)

    def serialize(self):
        return {'name': self.ENCRYPTION_NAME}

    @classmethod
    def deserialize(cls, encryption_params):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        return cls()


class VigenereCipher(ShiftBasedCipher, SingleKeyCipher):
    ENCRYPTION_NAME = 'Vigenere cipher'

    def encrypt(self, plaintext):
        return ''.join(self._shift_character(c, self._calculate_shift(key_letter))
                       for c, key_letter in zip(plaintext, cycle(self.key)))

    def encrypt_binary(self, plaintext):
        return ''.join(self._shift_binary_character(c, self._calculate_shift(key_letter))
                       for c, key_letter in zip(plaintext, cycle(self.key)))

    def decrypt(self, ciphertext):
        return ''.join(self._shift_character(c, -self._calculate_shift(key_letter))
                       for c, key_letter in zip(ciphertext, cycle(self.key)))

    def decrypt_binary(self, ciphertext):
        return ''.join(self._shift_binary_character(c, -self._calculate_shift(key_letter))
                       for c, key_letter in zip(ciphertext, cycle(self.key)))

    def _calculate_shift(self, key_letter):
        return self.UPPER_LETTERS.index(key_letter)

