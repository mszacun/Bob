class TextMessage(object):
    def __init__(self, content):
        self.content = content


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
