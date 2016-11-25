import base64


class IncomingFileTransfer(object):
    def __init__(self, filepath, expected_size, encryption):
        self.filepath = filepath
        self.expected_size = expected_size
        self.encryption = encryption

        self.ciphertext = ''
        self.plaintext = ''

    def open(self):
        self.file = open(self.filepath, 'wb')
        self.received_bytes = 0

    def close(self):
        self.file.close()

    def write(self, base64_encrypted_data):
        encrypted_data = base64.b64decode(base64_encrypted_data)
        self.received_bytes += len(encrypted_data)
        data = self.encryption.decrypt_binary(encrypted_data, self.is_completed)
        self.file.write(data)

        self.plaintext += data
        self.ciphertext += encrypted_data

    @property
    def is_completed(self):
        return self.received_bytes >= self.expected_size


class OutcomingFileTransfer(object):
    def __init__(self, filepath, encryption):
        self.filepath = filepath
        self.encryption = encryption

        self.ciphertext = ''
        self.plaintext = ''

    def open(self):
        self.file = open(self.filepath, 'rb')
        self.is_completed = False

    def close(self):
        self.file.close()

    def get_chunk(self, chunk_size):
        data = self.file.read(chunk_size)
        self.is_completed = len(data) < chunk_size
        encrypted_data = self.encryption.encrypt_binary(data, self.is_completed)

        self.plaintext += data
        self.ciphertext += encrypted_data

        return base64.b64encode(encrypted_data)
