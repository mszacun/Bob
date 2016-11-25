#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import re
import curses
import npyscreen
import logging

from networking.client import Client
from networking.server import Server
from gui.application import BobApplication
from encryption.ciphers import NoneEncryption


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bob - Simple and safe instant messaging')
    parser.add_argument('-l', '--listen', action='store_true', help='Start in server mode (listen on specified port)')
    parser.add_argument('--port', '-p', default=1306, help='Port used for communication (to listen to, or to connect to)')
    parser.add_argument('hostname', nargs='?', default='127.0.0.1', help='Host to which connect when running in client mode')

    args = parser.parse_args()
    port = int(args.port)

    logger = logging.getLogger('bob')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('/tmp/bob.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    encryption = NoneEncryption()
    protocol = Server(port, encryption) if args.listen else Client(args.hostname, port, encryption)
    protocol.start()
    app = BobApplication(protocol, encryption)
    app.run()
