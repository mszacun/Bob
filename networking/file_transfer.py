import base64


class IncomingFileTransfer(object):
    def __init__(self, filepath, expected_size, encryption):
        self.filepath = filepath
        self.expected_size = expected_size
        self.encryption = encryption

    def open(self):
        self.file = open(self.filepath, 'wb')
        self.received_bytes = 0

    def close(self):
        self.file.close()

    def write(self, base64_encrypted_data):
        encrypted_data = base64.b64decode(base64_encrypted_data)
        data = self.encryption.decrypt_binary(encrypted_data)
        self.file.write(data)
        self.received_bytes += len(data)

    @property
    def is_completed(self):
        return self.received_bytes == self.expected_size


class OutcomingFileTransfer(object):
    def __init__(self, filepath, encryption):
        self.filepath = filepath
        self.encryption = encryption

    def open(self):
        self.file = open(self.filepath, 'rb')

    def close(self):
        self.file.close()

    def get_chunk(self, chunk_size):
        data = self.file.read(chunk_size)
        encrypted_data = self.encryption.encrypt_binary(data)
        return base64.b64encode(encrypted_data)
