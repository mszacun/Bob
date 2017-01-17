import base64


class IncomingFileTransfer(object):
    def __init__(self, original_filename, expected_size, encryption, received_signature):
        self.original_filename = original_filename
        self.expected_size = expected_size
        self.encryption = encryption
        self.received_signature = received_signature

        self.ciphertext = []
        self.plaintext = []

    def open(self):
        self.file = open(self.filepath, 'wb')
        self.received_bytes = 0

    def close(self):
        self.file.close()

    def set_destination(self, filepath):
        self.filepath = filepath

    def write(self, base64_encrypted_data, is_completed):
        self.is_completed = is_completed

        encrypted_data = base64.b64decode(base64_encrypted_data)
        data = self.encryption.decrypt_binary(encrypted_data, self.is_completed)
        self.received_bytes += len(data)
        self.file.write(data)

        self.plaintext.append(data)
        self.ciphertext.append(encrypted_data)


class OutcomingFileTransfer(object):
    def __init__(self, filepath, encryption):
        self.filepath = filepath
        self.encryption = encryption

        self.ciphertext = []
        self.plaintext = []

    def open(self):
        self.file = open(self.filepath, 'rb')
        self.is_completed = False

    def close(self):
        self.file.close()

    def get_chunk(self, chunk_size):
        data = self.file.read(chunk_size)
        self.is_completed = len(data) < chunk_size
        encrypted_data = self.encryption.encrypt_binary(data, self.is_completed)

        self.plaintext.append(data)
        self.ciphertext.append(encrypted_data)

        return base64.b64encode(encrypted_data)
