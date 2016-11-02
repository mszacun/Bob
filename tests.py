import unittest

from cryptography import CaesarCipher


class CipherTests(unittest.TestCase):
    def setUp(self):
        self.cipher = CaesarCipher(key=3)

    def test_caesar_cipher(self):
        self.assertEncryptAndDecrypt('abcdefghijklmnopqrstuvwxyz', 'defghijklmnopqrstuvwxyzabc')
        self.assertEncryptAndDecrypt('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'DEFGHIJKLMNOPQRSTUVWXYZABC')
        self.assertEncryptAndDecrypt('1234567890', '4567890123')
        self.assertEncryptAndDecrypt('@#$#%$^*^%   ,./,.', '@#$#%$^*^%   ,./,.')
        self.assertEncryptAndDecrypt('sdf%nsd324fjkSRERYHBsfa4sdWERWE.', 'vgi%qvg657imnVUHUBKEvid7vgZHUZH.')

        all_binary_string = ''.join(chr(i) for i in range(256))
        all_binary_string_shfted = ''.join(chr((i + 3) % 256) for i in range(256))
        self.assertEncryptAndDecryptBinary(all_binary_string, all_binary_string_shfted)

    def assertEncryptAndDecrypt(self, plaintext, expected_ciphertext):
        self.assertEqual(self.cipher.encrypt(plaintext), expected_ciphertext)
        self.assertEqual(self.cipher.decrypt(expected_ciphertext), plaintext)

    def assertEncryptAndDecryptBinary(self, plaintext, expected_ciphertext):
        self.assertEqual(self.cipher.encrypt_binary(plaintext), expected_ciphertext)
        self.assertEqual(self.cipher.decrypt_binary(expected_ciphertext), plaintext)


if __name__ == '__main__':
    unittest.main()
