import base64
from threading import Thread
from Queue import Queue
import json
import os
from time import sleep

from networking.file_transfer import IncomingFileTransfer, OutcomingFileTransfer
from messages import TextMessage, DisconnectMessage, ConnectionEstablishedMessage, ChangeEncryptionMessage, \
     OfferFileTransmissionMessage, FileChunkMessage, FileSendingCompleteMessage, FileReceivingCompleteMessage
from encryption.ciphers import CaesarCipher, NoneEncryption, VigenereCipher, Rot13Cipher, AESCipher
from encryption.base import NotThisEncryptionSerialized


TEXT_MESSAGE_TYPE = 'TEXT_MESSAGE'
CHANGE_ENCRYPTION_MESSAGE_TYPE = 'CHANGE_ENCRYPTION'
OFFER_FILE_TRANSMISSION_MESSAGE_TYPE = 'OFFER_FILE_TRANSMISSION'
ACCEPT_FILE_TRANSMISSION_MESSAGE_TYPE = 'ACCEPT_FILE_TRANSMISSION'
FILE_CHUNK_MESSAGE_TYPE = 'FILE_CHUNK'


class NetworkProtocol(Thread):
    KNOWN_ENCRYPTIONS = [CaesarCipher, NoneEncryption, VigenereCipher, Rot13Cipher, AESCipher]
    FILE_CHUNK_SIZE = 65536
    RECV_BUFFER_SIZE = 131072
    BETWEEN_FILE_CHUNKS_TIME = 0.08

    def __init__(self, encryption):
        super(NetworkProtocol, self).__init__()
        self.queue = Queue()
        self.daemon = True
        self.encryption = encryption

    def send_message(self, message):
        if self.encryption.returns_binary_data:
            message = base64.b64encode(message)
        self._send({'type': TEXT_MESSAGE_TYPE, 'content': message})

    def _send(self, message_dict):
        self.socket.sendall(json.dumps(message_dict))

    def disconnect(self):
        if hasattr(self, 'socket'):
            self.socket.close()

    def request_encryption(self, encryption):
        self._send({'type': CHANGE_ENCRYPTION_MESSAGE_TYPE, 'encryption_params': encryption.serialize()})
        self.encryption = encryption

    def offer_file_transmission(self, filepath, encryption):
        message = {'type': OFFER_FILE_TRANSMISSION_MESSAGE_TYPE, 'filename': os.path.basename(filepath),
                   'number_of_bytes': os.path.getsize(filepath)}
        self._send(message)
        self.outcoming_file_transfer = OutcomingFileTransfer(filepath, encryption)

    def receive_file(self, save_destination, expected_number_of_bytes, encryption):
        self.incoming_file_transfer = IncomingFileTransfer(save_destination, expected_number_of_bytes, encryption)
        self.incoming_file_transfer.open()
        self._send({'type': ACCEPT_FILE_TRANSMISSION_MESSAGE_TYPE})

    def main_loop(self):
        while True:
            data = self.socket.recv(self.RECV_BUFFER_SIZE)
            if not data:
                self.queue.put(DisconnectMessage())
            else:
                self._dispatch(json.loads(data))

    def _dispatch(self, message_dict):
        if message_dict['type'] == TEXT_MESSAGE_TYPE:
            self._recive_message(message_dict)
        if message_dict['type'] == CHANGE_ENCRYPTION_MESSAGE_TYPE:
            self.encryption = self._dispatch_change_encryption(message_dict)
            self.queue.put(ChangeEncryptionMessage(self.encryption))
        if message_dict['type'] == OFFER_FILE_TRANSMISSION_MESSAGE_TYPE:
            message = OfferFileTransmissionMessage(message_dict['filename'], message_dict['number_of_bytes'])
            self.queue.put(message)
        if message_dict['type'] == ACCEPT_FILE_TRANSMISSION_MESSAGE_TYPE:
            self._send_file()
        if message_dict['type'] == FILE_CHUNK_MESSAGE_TYPE:
            self._recive_file_chunk(message_dict)

    def _recive_message(self, message_dict):
        content = message_dict['content']
        if self.encryption.returns_binary_data:
            content = base64.b64decode(content)
        self.queue.put(TextMessage(content))

    def _dispatch_change_encryption(self, message_dict):
        for known_encryption in self.KNOWN_ENCRYPTIONS:
            try:
                return known_encryption.deserialize(message_dict['encryption_params'])
            except NotThisEncryptionSerialized:
                pass

    def _send_file(self):
        self.outcoming_file_transfer.open()

        while not self.outcoming_file_transfer.is_completed:
            chunk = self.outcoming_file_transfer.get_chunk(self.FILE_CHUNK_SIZE)
            self._send({'type': FILE_CHUNK_MESSAGE_TYPE, 'content': chunk})
            sleep(self.BETWEEN_FILE_CHUNKS_TIME)

        message = FileSendingCompleteMessage(self.outcoming_file_transfer.filepath,
                                             self.outcoming_file_transfer.plaintext,
                                             self.outcoming_file_transfer.ciphertext)
        self.queue.put(message)
        self.outcoming_file_transfer.close()
        self.outcoming_file_transfer = None


    def _recive_file_chunk(self, message_dict):
        self.incoming_file_transfer.write(message_dict['content'])
        message = FileChunkMessage(self.incoming_file_transfer.received_bytes)
        self.queue.put(message)

        if self.incoming_file_transfer.is_completed:
            self.incoming_file_transfer.close()
            self.queue.put(FileReceivingCompleteMessage(self.incoming_file_transfer.filepath,
                                                        self.incoming_file_transfer.plaintext,
                                                        self.incoming_file_transfer.ciphertext))
            self.incoming_file_transfer = None
