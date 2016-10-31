import socket
from threading import Thread
from Queue import Queue
import json
import os
import base64
from time import sleep

from messages import TextMessage, DisconnectMessage, ConnectionEstablishedMessage, ChangeEncryptionMessage, \
     OfferFileTransmissionMessage
from cryptography import CaesarCipher, NoneEncryption, NotThisEncryptionSerialized


TEXT_MESSAGE_TYPE = 'TEXT_MESSAGE'
CHANGE_ENCRYPTION_MESSAGE_TYPE = 'CHANGE_ENCRYPTION'
OFFER_FILE_TRANSMISSION_MESSAGE_TYPE = 'OFFER_FILE_TRANSMISSION'
ACCEPT_FILE_TRANSMISSION_MESSAGE_TYPE = 'ACCEPT_FILE_TRANSMISSION'
FILE_CHUNK_MESSAGE_TYPE = 'FILE_CHUNK'


class IncomingFileTransfer(object):
    def __init__(self, filepath, expected_size):
        self.filepath = filepath
        self.expected_size = expected_size

    def open(self):
        self.file = open(self.filepath, 'wb')
        self.received_bytes = 0

    def close(self):
        self.file.close()

    def write(self, base64_data):
        data = base64.b64decode(base64_data)
        self.file.write(data)
        self.received_bytes += len(data)

    @property
    def is_completed(self):
        return self.received_bytes == self.expected_size


class OutcomingFileTransfer(object):
    CHUNK_SIZE = 1024

    def __init__(self, filepath):
        self.filepath = filepath

    def open(self):
        self.file = open(self.filepath, 'rb')

    def close(self):
        self.file.close()

    def get_chunk(self):
        return base64.b64encode(self.file.read(self.CHUNK_SIZE))


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

    def offer_file_transmission(self, filepath):
        message = {'type': OFFER_FILE_TRANSMISSION_MESSAGE_TYPE, 'filename': os.path.basename(filepath),
                   'number_of_bytes': os.path.getsize(filepath)}
        self._send(message)
        self.outcoming_file_transfer = OutcomingFileTransfer(filepath)

    def receive_file(self, save_destination, expected_number_of_bytes):
        self.incoming_file_transfer = IncomingFileTransfer(save_destination, expected_number_of_bytes)
        self.incoming_file_transfer.open()
        self._send({'type': ACCEPT_FILE_TRANSMISSION_MESSAGE_TYPE})

    def main_loop(self):
        while True:
            data = self.socket.recv(2048)
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
        if message_dict['type'] == OFFER_FILE_TRANSMISSION_MESSAGE_TYPE:
            message = OfferFileTransmissionMessage(message_dict['filename'], message_dict['number_of_bytes'])
            self.queue.put(message)
        if message_dict['type'] == ACCEPT_FILE_TRANSMISSION_MESSAGE_TYPE:
            self._send_file()
        if message_dict['type'] == FILE_CHUNK_MESSAGE_TYPE:
            self._recive_file_chunk(message_dict)

    def _dispatch_change_encryption(self, message_dict):
        for known_encryption in self.KNOWN_ENCRYPTIONS:
            try:
                return known_encryption.deserialize(message_dict['encryption_params'])
            except NotThisEncryptionSerialized:
                pass

    def _send_file(self):
        self.outcoming_file_transfer.open()
        chunk = self.outcoming_file_transfer.get_chunk()

        while chunk:
            self._send({'type': FILE_CHUNK_MESSAGE_TYPE, 'content': chunk})
            chunk = self.outcoming_file_transfer.get_chunk()
            sleep(0.01)

        self.outcoming_file_transfer.close()
        self.outcoming_file_transfer = None

    def _recive_file_chunk(self, message_dict):
        self.incoming_file_transfer.write(message_dict['content'])
        if self.incoming_file_transfer.is_completed:
            self.incoming_file_transfer.close()
            self.incoming_file_transfer = None


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
