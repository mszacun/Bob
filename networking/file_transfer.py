import base64


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
    def __init__(self, filepath):
        self.filepath = filepath

    def open(self):
        self.file = open(self.filepath, 'rb')

    def close(self):
        self.file.close()

    def get_chunk(self, chunk_size):
        return base64.b64encode(self.file.read(chunk_size))
