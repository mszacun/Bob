import socket
from threading import Thread
from Queue import Queue
import json

from messages import TextMessage, DisconnectMessage, ConnectionEstablishedMessage, ChangeEncryptionMessage
from cryptography import CaesarCipher, NoneEncryption, NotThisEncryptionSerialized


TEXT_MESSAGE_TYPE = 'TEXT_MESSAGE'
CHANGE_ENCRYPTION_MESSAGE_TYPE = 'CHANGE_ENCRYPTION'


class NetworkProtocol(Thread):
    KNOWN_ENCRYPTIONS = [CaesarCipher, NoneEncryption]

    def __init__(self):
        super(NetworkProtocol, self).__init__()
        self.queue = Queue()
        self.daemon = True

    def send_message(self, message):
        self._send({'type': TEXT_MESSAGE_TYPE, 'content': message})

    def _send(self, message_dict):
        self.socket.sendall(json.dumps(message_dict))

    def disconnect(self):
        if hasattr(self, 'socket'):
            self.socket.close()

    def request_encryption(self, encryption):
        self._send({'type': CHANGE_ENCRYPTION_MESSAGE_TYPE, 'encryption_params': encryption.serialize()})
        self.encryption = encryption

    def main_loop(self):
        while True:
            data = self.socket.recv(128)
            if not data:
                self.queue.put(DisconnectMessage())
            else:
                self._dispatch(json.loads(data))

    def _dispatch(self, message_dict):
        if message_dict['type'] == TEXT_MESSAGE_TYPE:
            self.queue.put(TextMessage(message_dict['content']))
        if message_dict['type'] == CHANGE_ENCRYPTION_MESSAGE_TYPE:
            encryption = self._dispatch_change_encryption(message_dict)
            self.queue.put(ChangeEncryptionMessage(encryption))

    def _dispatch_change_encryption(self, message_dict):
        for known_encryption in self.KNOWN_ENCRYPTIONS:
            try:
                return known_encryption.deserialize(message_dict['encryption_params'])
            except NotThisEncryptionSerialized:
                pass


class Server(NetworkProtocol):
    initial_panel_caption = 'waiting for connection...'
    participant_name = 'Client'
    myself_name = 'Server'

    def __init__(self, local_port):
        super(Server, self).__init__()
        self.local_port = local_port

    def disconnect(self):
        super(Server, self).disconnect()
        self.server_socket.close()

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', self.local_port))
        self.server_socket.listen(5)
        self.socket, self.client_address = self.server_socket.accept()

        self.queue.put(ConnectionEstablishedMessage(self.client_address))

        self.main_loop()

class Client(NetworkProtocol):
    initial_panel_caption = 'connecting to server...'
    participant_name = 'Server'
    myself_name = 'Client'

    def __init__(self, hostname, remote_port):
        super(Client, self).__init__()
        self.remote_port = remote_port
        self.hostname = hostname

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.hostname, self.remote_port))

        self.queue.put(ConnectionEstablishedMessage((self.hostname, self.remote_port)))

        self.main_loop()
