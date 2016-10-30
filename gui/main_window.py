import npyscreen

from messages import TextMessage, DisconnectMessage, ConnectionEstablishedMessage

from gui.command_box import HistoryRemeberingTextCommandBox
from gui.highlightning import MessageHighlightMultiLine
from gui.controler import SendMessageActionController
from gui.controler import Message


class MainWindow(npyscreen.FormMuttActiveWithMenus):
    COMMAND_WIDGET_CLASS = HistoryRemeberingTextCommandBox
    ACTION_CONTROLLER = SendMessageActionController
    MAIN_WIDGET_CLASS = MessageHighlightMultiLine

    def __init__(self, protocol):
        super(MainWindow, self).__init__()
        self.protocol = protocol

    def create(self):
        super(MainWindow, self).create()
        self.keypress_timeout = 1

        menu = self.new_menu(name='Menu')
        menu.addItem('Send file')
        encryption = menu.addNewSubmenu('Encryption')
        encryption.addItem('None')
        encryption.addItem('Caesar Cipher')
        menu.addItem('Exit', self.exit_application)
        self.editw = 3

    def while_waiting(self):
        while (not self.protocol.queue.empty()):
            self.dispatch(self.protocol.queue.get())

    def dispatch(self, message):
        if isinstance(message, TextMessage):
            self.wMain.values.append(Message(message.content, self.protocol.participant_name))
            self.wMain.display()
        if isinstance(message, DisconnectMessage):
            self.exit_application()
        if isinstance(message, ConnectionEstablishedMessage):
            status_message = 'connected with {}'.format(message.get_formatted_remote_address())
            self.refresh_statusbar(status_message, 'None')

    def refresh_statusbar(self, status_message, encryption_message):
            self.wStatus2.value = "{}: {}         Encryption: {} ".format(self.protocol.myself_name,
                                                                          status_message, encryption_message)
            self.wStatus2.display()

    def send_message(self, message):
        self.protocol.send_message(message)

    def exit_application(self):
        self.protocol.disconnect()

        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()
