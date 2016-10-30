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

    def assertEncryptAndDecrypt(self, plaintext, expected_ciphertext):
        self.assertEqual(self.cipher.encrypt(plaintext), expected_ciphertext)
        self.assertEqual(self.cipher.decrypt(expected_ciphertext), plaintext)


if __name__ == '__main__':
        unittest.main()
