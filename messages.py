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
