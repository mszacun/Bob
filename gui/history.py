import os
from datetime import datetime

from hexdump import hexdump, dump, dehex

from encryption.signing import sign_bytes, hash_bytes, decrypt_signature


class HistoryItem(object):
    YOU_SENDER = 'You'

    def __init__(self, encryption, plaintext=None, ciphertext=None, sender=None,
                 time=None):
        self.encryption = encryption
        self.sender = sender or self.YOU_SENDER
        self.time = time or datetime.now()
        self.plaintext = plaintext
        self.ciphertext = ciphertext

    @property
    def formatted_time(self):
        return self.time.strftime('%H:%M:%S')

    def _calculate_signatures(self, his_public_key, my_private_key, received_signature):
        self.calculated_hash = dump(hash_bytes(str(self.plaintext)))

        if self.sender == self.YOU_SENDER:
            self.calculated_signature = dump(sign_bytes(self.plaintext, his_public_key, my_private_key))
            self.received_signature = '-----'
            self.received_hash = '-----'
        else:
            self.calculated_signature = '-----'
            self.received_signature = received_signature
            self.received_hash = dump(decrypt_signature(dehex(received_signature), his_public_key, my_private_key))



class Message(HistoryItem):
    def __init__(self, encryption, his_public_key, my_private_key, plaintext=None, ciphertext=None, sender=None,
                 received_signature=None, time=None):
        if plaintext:
            ciphertext = encryption.encrypt(plaintext)
        else:
            plaintext = encryption.decrypt(ciphertext)

        super(Message, self).__init__(encryption, plaintext, ciphertext, sender, time)

        self._calculate_signatures(his_public_key, my_private_key, received_signature)

    def get_ciphertext_for_user_presentation(self):
        if self.encryption.returns_binary_data:
            return hexdump(self.ciphertext, result='return')
        else:
            return self.ciphertext


    def __str__(self):
        return '{} - {}: {}'.format(self.formatted_time, self.sender, self.plaintext)


class FileTransfer(HistoryItem):
    def __init__(self, encryption, filepath, plaintext, ciphertext, his_public_key, my_private_key, sender=None,
                 received_signature=None, time=None):
        self.filename = os.path.basename(filepath)

        plaintext = ''.join(plaintext)
        ciphertext = ''.join(ciphertext)

        super(FileTransfer, self).__init__(encryption, plaintext, ciphertext, sender, time)

        self._calculate_signatures(his_public_key, my_private_key, received_signature or 'AA')

        self.plaintext = hexdump(self.plaintext, result='return')
        self._dumped_ciphertext = hexdump(self.ciphertext, result='return')

    def get_ciphertext_for_user_presentation(self):
        return self._dumped_ciphertext

    def __str__(self):
        direction = 'sent' if self.sender == self.YOU_SENDER else 'received'

        return '{} ! -> File {} was {}'.format(self.formatted_time, self.filename, direction)
