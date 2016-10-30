import npyscreen
from datetime import datetime


class Message(object):
    def __init__(self, content, sender=None, time=None):
        self.content = content
        self.sender = sender or 'You'
        self.time = time or datetime.now()

    def __str__(self):
        return '{} - {}: {}'.format(self.time.strftime('%H:%M:%S'), self.sender, self.content)


class SendMessageActionController(npyscreen.ActionControllerSimple):
    def create(self):
        self.add_action('.*', self.send_message, False)

    def send_message(self, command_line, widget_proxy, live):
        self.parent.send_message(command_line)
        self.parent.wMain.values.append(Message(command_line))
        self.parent.wMain.display()
