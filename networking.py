import socket
from threading import Thread
from Queue import Queue


class NetworkProtocol(Thread):
    def __init__(self):
        super(NetworkProtocol, self).__init__()
        self.queue = Queue()
        self.daemon = True

    def send_message(self, message):
        self.socket.sendall(message)

    def disconnect(self):
        if hasattr(self, 'socket'):
            self.socket.close()


class Server(NetworkProtocol):
    panel_caption = 'Waiting for connection'
    participant_name = 'Client'

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
        self.socket, self.client_addres = self.server_socket.accept()

        while True:
            data = self.socket.recv(128)
            if not data:
                break
            else:
                self.queue.put(data)


class Client(NetworkProtocol):
    panel_caption = 'Connected to localhost:4000'
    participant_name = 'Server'

    def __init__(self, hostname, remote_port):
        super(Client, self).__init__()
        self.remote_port = remote_port
        self.hostname = hostname

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.hostname, self.remote_port))

        while True:
            self.queue.put(self.socket.recv(128))

