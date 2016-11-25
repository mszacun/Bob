import os
from datetime import datetime

from hexdump import hexdump


class HistoryItem(object):
    YOU_SENDER = 'You'

    def __init__(self, encryption, plaintext=None, ciphertext=None, sender=None, time=None):
        self.encryption = encryption
        self.sender = sender or self.YOU_SENDER
        self.time = time or datetime.now()
        self.plaintext = plaintext
        self.ciphertext = ciphertext

    @property
    def formatted_time(self):
        return self.time.strftime('%H:%M:%S')



class Message(HistoryItem):
    def __init__(self, encryption, plaintext=None, ciphertext=None, sender=None, time=None):
        if plaintext:
            ciphertext = encryption.encrypt(plaintext)
        else:
            plaintext = encryption.decrypt(ciphertext)

        super(Message, self).__init__(encryption, plaintext, ciphertext, sender, time)

    def get_ciphertext_for_user_presentation(self):
        if self.encryption.returns_binary_data:
            return hexdump(self.ciphertext, result='return')

    def __str__(self):
        return '{} - {}: {}'.format(self.formatted_time, self.sender, self.plaintext)


class FileTransfer(HistoryItem):
    def __init__(self, encryption, filepath, plaintext, ciphertext, sender=None, time=None):
        self.filename = os.path.basename(filepath)

        plaintext = hexdump(plaintext, result='return')
        self._dumped_ciphertext = hexdump(ciphertext, result='return')

        super(FileTransfer, self).__init__(encryption, plaintext, ciphertext, sender, time)

    def get_ciphertext_for_user_presentation(self):
        return self._dumped_ciphertext

    def __str__(self):
        direction = 'sent' if self.sender == self.YOU_SENDER else 'received'

        return '{} ! -> File {} was {}'.format(self.formatted_time, self.filename, direction)
