import socket

from networking.network_protocol import NetworkProtocol
from messages import ConnectionEstablishedMessage


class Server(NetworkProtocol):
    initial_panel_caption = 'waiting for connection...'
    participant_name = 'Client'
    myself_name = 'Server'
    private_key_file = 'server_private_key.pem'
    public_key_file = 'server_public_key.pem'

    def __init__(self, local_port, encryption):
        super(Server, self).__init__(encryption)
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

