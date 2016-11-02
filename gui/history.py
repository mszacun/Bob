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
            super(Message, self).__init__(encryption, plaintext, encryption.encrypt(plaintext), sender, time)
        else:
            super(Message, self).__init__(encryption, encryption.decrypt(ciphertext), ciphertext, sender, time)

    def __str__(self):
        return '{} - {}: {}'.format(self.formatted_time, self.sender, self.plaintext)


class FileTransfer(HistoryItem):
    def __init__(self, encryption, filepath, sender=None, time=None):
        self.filename = os.path.basename(filepath)

        file_content = self._read_file(filepath)

        plaintext = hexdump(file_content, result='return')
        ciphertext = hexdump(encryption.encrypt_binary(file_content), result='return')

        super(FileTransfer, self).__init__(encryption, plaintext, ciphertext, sender, time)

    def _read_file(self, filepath):
        with open(filepath, 'rb') as open_file:
            return open_file.read()

    def __str__(self):
        direction = 'sent' if self.sender == self.YOU_SENDER else 'received'

        return '{} ! -> File {} was {}'.format(self.formatted_time, self.filename, direction)
