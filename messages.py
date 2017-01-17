class TextMessage(object):
    def __init__(self, content, signature):
        self.content = content
        self.signature = signature


class DisconnectMessage(object):
    pass


class ConnectionEstablishedMessage(object):
    def __init__(self, remote_address):
        self.remote_address = remote_address

    def get_formatted_remote_address(self):
        return '{}:{}'.format(self.remote_address[0], self.remote_address[1])


class ChangeEncryptionMessage(object):
    def __init__(self, encryption):
        self.encryption = encryption


class OfferFileTransmissionMessage(object):
    def __init__(self, filename, number_of_bytes):
        self.filename = filename
        self.number_of_bytes = number_of_bytes


class FileChunkMessage(object):
    def __init__(self, number_of_bytes_received_so_far):
        self.number_of_bytes_received_so_far = number_of_bytes_received_so_far


class FileSendingCompleteMessage(object):
    def __init__(self, filepath, plaintext, ciphertext):
        self.filepath = filepath
        self.plaintext = plaintext
        self.ciphertext = ciphertext


class FileReceivingCompleteMessage(object):
    def __init__(self, filepath, plaintext, ciphertext, received_signature):
        self.filepath = filepath
        self.plaintext = plaintext
        self.ciphertext = ciphertext
        self.received_signature = received_signature
