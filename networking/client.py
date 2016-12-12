import socket

from networking.network_protocol import NetworkProtocol
from messages import ConnectionEstablishedMessage


class Client(NetworkProtocol):
    initial_panel_caption = 'connecting to server...'
    participant_name = 'Server'
    myself_name = 'Client'
    private_key_file = 'client_private_key.pem'
    public_key_file = 'client_public_key.pem'

    def __init__(self, hostname, remote_port, encryption):
        super(Client, self).__init__(encryption)
        self.remote_port = remote_port
        self.hostname = hostname

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.hostname, self.remote_port))

        self.queue.put(ConnectionEstablishedMessage((self.hostname, self.remote_port)))

        self.main_loop()
