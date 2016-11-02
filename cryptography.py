class NotThisEncryptionSerialized(Exception):
    pass


class NoneEncryption(object):
    ENCRYPTION_NAME = 'None'

    def encrypt(self, plaintext):
        return plaintext

    def encrypt_binary(self, plaintext):
        return plaintext

    def decrypt(self, ciphertext):
        return ciphertext

    def decrypt_binary(self, ciphertext):
        return ciphertext

    def serialize(self):
        return {'name': self.ENCRYPTION_NAME}

    @classmethod
    def deserialize(cls, encryption_params):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        return NoneEncryption()

    def __str__(self):
        return self.ENCRYPTION_NAME


class CaesarCipher(object):
    ENCRYPTION_NAME = 'Caesar cipher'
    LOWER_LETTERS = 'abcdefghijklmnopqrstuvwxyz'
    UPPER_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    DIGITS = '0123456789'

    def __init__(self, key):
        self.key = key

    def encrypt(self, plaintext):
        return ''.join(self._encrypt_character(c) for c in plaintext)

    def encrypt_binary(self, plaintext):
        return ''.join(self._shift_binary_character(c, self.key) for c in plaintext)

    def decrypt(self, ciphertext):
        return ''.join(self._decrypt_character(c) for c in ciphertext)

    def decrypt_binary(self, ciphertext):
        return ''.join(self._shift_binary_character(c, -self.key) for c in ciphertext)

    def serialize(self):
        return {'name': self.ENCRYPTION_NAME, 'key': self.key}

    @classmethod
    def deserialize(cls, encryption_params):
        if encryption_params['name'] != cls.ENCRYPTION_NAME:
            raise NotThisEncryptionSerialized()

        return CaesarCipher(key=encryption_params['key'])

    def _encrypt_character(self, character):
        if character in self.LOWER_LETTERS:
            return self._shift_using_alphabet(character, self.LOWER_LETTERS, self.key)

        if character in self.UPPER_LETTERS:
            return self._shift_using_alphabet(character, self.UPPER_LETTERS, self.key)

        if character in self.DIGITS:
            return self._shift_using_alphabet(character, self.DIGITS, self.key)

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

    def _decrypt_character(self, character):
        if character in self.LOWER_LETTERS:
            return self._shift_using_alphabet(character, self.LOWER_LETTERS, -self.key)

        if character in self.UPPER_LETTERS:
            return self._shift_using_alphabet(character, self.UPPER_LETTERS, -self.key)

        if character in self.DIGITS:
            return self._shift_using_alphabet(character, self.DIGITS, -self.key)

        return character

    def __str__(self):
        return '{} (key: {})'.format(self.ENCRYPTION_NAME, self.key)

