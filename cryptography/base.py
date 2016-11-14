
class NotThisEncryptionSerialized(Exception):
    pass


class NoKeyCipher(object):
    def serialize(self):
        return {'name': self.ENCRYPTION_NAME}

    @classmethod
    def deserialize(cls, encryption_params):
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
    def deserialize(cls, encryption_params):
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

