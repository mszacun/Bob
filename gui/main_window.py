from functools import partial
import os

import npyscreen

from messages import TextMessage, DisconnectMessage, ConnectionEstablishedMessage, ChangeEncryptionMessage, \
     OfferFileTransmissionMessage, FileChunkMessage, FileSendingCompleteMessage

from cryptography import CaesarCipher, NoneEncryption, VigenereCipher
from gui.command_box import HistoryRemeberingTextCommandBox
from gui.highlightning import MessageHighlightMultiLine
from gui.controler import SendMessageActionController
from gui.history import Message, FileTransfer
from utils import humanize_bytes
from gui.popups.file_select import selectFile

from gui.popups.caesar_encryption_configuration import CaesarEncryptionConfigurationPopup
from gui.popups.vigenere_encryption_configuration import VigenereEncryptionConfigurationPopup
from gui.popups.file_transfer_progress import FileTransferProgressPopup


class MainWindow(npyscreen.FormMuttActiveWithMenus):
    COMMAND_WIDGET_CLASS = HistoryRemeberingTextCommandBox
    ACTION_CONTROLLER = SendMessageActionController
    MAIN_WIDGET_CLASS = MessageHighlightMultiLine

    def __init__(self, protocol, encryption):
        self.protocol = protocol
        self.current_encryption = encryption
        self.status_message = ''
        self.encryption_message = ''

        super(MainWindow, self).__init__()

    def create(self):
        super(MainWindow, self).create()
        self.keypress_timeout = 1

        menu = self.new_menu(name='Menu')
        menu.addItem('Send file', self.send_file)
        encryption = menu.addNewSubmenu('Encryption')
        encryption.addItem('None', self.configure_none_encryption)
        encryption.addItem('Caesar Cipher', partial(self.configure_encryption, CaesarEncryptionConfigurationPopup))
        encryption.addItem('Vigenere Cipher', partial(self.configure_encryption, VigenereEncryptionConfigurationPopup))
        menu.addItem('Exit', self.exit_application)
        self.editw = 3

        self.refresh_statusbar(self.protocol.initial_panel_caption, str(self.current_encryption))

    def while_waiting(self):
        while not self.protocol.queue.empty():
            self.dispatch(self.protocol.queue.get())

    def dispatch(self, message):
        if isinstance(message, TextMessage):
            message = Message(self.current_encryption, ciphertext=message.content, sender=self.protocol.participant_name)
            self.wMain.add_message(message)
        if isinstance(message, DisconnectMessage):
            self.exit_application()
        if isinstance(message, ConnectionEstablishedMessage):
            status_message = 'connected with {}'.format(message.get_formatted_remote_address())
            self.refresh_statusbar(status_message=status_message)
        if isinstance(message, ChangeEncryptionMessage):
            self._set_encryption(message.encryption, set_by_remote=True)
        if isinstance(message, OfferFileTransmissionMessage):
            self._ask_to_accept_file_transmission(message.filename, message.number_of_bytes)
        if isinstance(message, FileSendingCompleteMessage):
            self._add_file_transfer(message.filepath)

    def refresh_statusbar(self, status_message=None, encryption_message=None):
        status_message = status_message or self.status_message
        self.status_message = status_message

        encryption_message = encryption_message or self.encryption_message
        self.encryption_message = encryption_message

        self.wStatus2.value = "{}: {}         Encryption: {} ".format(self.protocol.myself_name,
                                                                      status_message, encryption_message)
        self.wStatus2.display()

    def send_message(self, message_text):
        if message_text:
            message = Message(self.current_encryption, plaintext=message_text)
            self.protocol.send_message(message.ciphertext)
            self.wMain.add_message(message)

    def exit_application(self):
        self.protocol.disconnect()

        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()

    def send_file(self):
        file_to_send = selectFile('~/', must_exist=True, confirm_if_exists=False)
        self.protocol.offer_file_transmission(file_to_send, self.current_encryption)

    def configure_encryption(self, configuration_popup_cls):
        configuration_popup = configuration_popup_cls()
        configuration_popup.edit()
        if configuration_popup.value:
            self._set_encryption(configuration_popup.build_encryption(), set_by_remote=False)

    def configure_none_encryption(self):
        self._set_encryption(NoneEncryption(), set_by_remote=False)

    def _set_encryption(self, encryption, set_by_remote=False):
        self.current_encryption = encryption
        self.refresh_statusbar(encryption_message=str(encryption))

        if not set_by_remote:
            self.protocol.request_encryption(encryption)

    def _ask_to_accept_file_transmission(self, filename, number_of_bytes):
        message = '{} wants to send you file {} ({})\nDo you accept?'.format(self.protocol.participant_name,
                                                                             filename,
                                                                             humanize_bytes(number_of_bytes))
        if npyscreen.notify_yes_no(message, 'File transfer offer'):
            self._receive_file(filename, number_of_bytes)

    def _receive_file(self, filename, number_of_bytes):
        suggested_path = os.path.join('/tmp/', filename)
        save_destination = selectFile(suggested_path, must_exist=False, confirm_if_exists=True)
        self.progress_popup = FileTransferProgressPopup(filename, number_of_bytes, self.protocol)
        self.protocol.receive_file(save_destination, number_of_bytes, self.current_encryption)
        self.progress_popup.edit()
        self._add_file_transfer(save_destination, self.protocol.participant_name)

    def _add_file_transfer(self, filepath, sender=None):
        file_transfer = FileTransfer(self.current_encryption, filepath, sender)
        self.wMain.add_message(file_transfer)

