from itertools import cycle

from cryptography.base import CipherWithoutKey, ShiftBasedCipher, SingleKeyCipher


class NoneEncryption(CipherWithoutKey):
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


class Rot13Cipher(CipherWithoutKey, CaesarCipher):
    KEY = 13
    ENCRYPTION_NAME = 'Rot13 Cipher'

    def __init__(self):
        CaesarCipher.__init__(self, Rot13Cipher.KEY)


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

