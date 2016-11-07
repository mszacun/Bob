import unittest

from cryptography import CaesarCipher, VigenereCipher


class CipherTests(unittest.TestCase):
    def test_caesar_cipher(self):
        cipher = CaesarCipher(key=3)
        self.assertEncryptAndDecrypt(cipher, 'abcdefghijklmnopqrstuvwxyz', 'defghijklmnopqrstuvwxyzabc')
        self.assertEncryptAndDecrypt(cipher, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'DEFGHIJKLMNOPQRSTUVWXYZABC')
        self.assertEncryptAndDecrypt(cipher, '1234567890', '4567890123')
        self.assertEncryptAndDecrypt(cipher, '@#$#%$^*^%   ,./,.', '@#$#%$^*^%   ,./,.')
        self.assertEncryptAndDecrypt(cipher, 'sdf%nsd324fjkSRERYHBsfa4sdWERWE.', 'vgi%qvg657imnVUHUBKEvid7vgZHUZH.')

        all_binary_string = ''.join(chr(i) for i in range(256))
        all_binary_string_shfted = ''.join(chr((i + 3) % 256) for i in range(256))
        self.assertEncryptAndDecryptBinary(cipher, all_binary_string, all_binary_string_shfted)

    def test_vigenere_cipher(self):
        self.assertEncryptAndDecrypt(VigenereCipher(key='LEMON'), 'ATTACKATDAWN', 'LXFOPVEFRNHR')
        self.assertEncryptAndDecrypt(VigenereCipher(key='COUNTON'), 'VIGENERECIPHER', 'XWARGSEGQCCASE')
        self.assertEncryptAndDecrypt(VigenereCipher(key='HOUGHTON'), 'michigantechnologicaluniversity', 'twwnpzoaaswnuhzbnwwgsnbvcslypmm')
        self.assertEncryptAndDecrypt(VigenereCipher(key='MARCIN'), 'lubie placki12', 'xuskm blresv32')



    def assertEncryptAndDecrypt(self, cipher, plaintext, expected_ciphertext):
        self.assertEqual(cipher.encrypt(plaintext), expected_ciphertext)
        self.assertEqual(cipher.decrypt(expected_ciphertext), plaintext)

    def assertEncryptAndDecryptBinary(self, cipher, plaintext, expected_ciphertext):
        self.assertEqual(cipher.encrypt_binary(plaintext), expected_ciphertext)
        self.assertEqual(cipher.decrypt_binary(expected_ciphertext), plaintext)


if __name__ == '__main__':
    unittest.main()
