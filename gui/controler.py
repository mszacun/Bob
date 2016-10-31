import npyscreen
from datetime import datetime


class Message(object):
    def __init__(self, encryption, plaintext=None, ciphertext=None, sender=None, time=None):
        self.encryption = encryption
        self.sender = sender or 'You'
        self.time = time or datetime.now()

        if plaintext:
            self.plaintext = plaintext
            self.ciphertext = encryption.encrypt(plaintext)
        else:
            self.ciphertext = ciphertext
            self.plaintext = encryption.decrypt(ciphertext)

    @property
    def formatted_time(self):
        return self.time.strftime('%H:%M:%S')

    def __str__(self):
        return '{} - {}: {}'.format(self.formatted_time, self.sender, self.plaintext)


class SendMessageActionController(npyscreen.ActionControllerSimple):
    def create(self):
        self.add_action('.*', self.send_message, False)

    def send_message(self, command_line, widget_proxy, live):
        self.parent.send_message(command_line)
