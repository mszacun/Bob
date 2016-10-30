import argparse
import re
import curses
import npyscreen
from datetime import datetime

from networking import Client, Server
from messages import TextMessage, DisconnectMessage


class Message(object):
    def __init__(self, content, sender=None, time=None):
        self.content = content
        self.sender = sender or 'You'
        self.time = time or datetime.now()

    def __str__(self):
        return '{} - {}: {}'.format(self.time.strftime('%H:%M:%S'), self.sender, self.content)


class MessageHighlightTextfield(npyscreen.Textfield):
    MESSAGE_REGEXP = re.compile('(\d+:\d+:\d+ - )(\w+: )(.*)')

    def __init__(self, *args, **kwargs):
        super(MessageHighlightTextfield, self).__init__(*args, **kwargs)

        self.syntax_highlighting = True

    def update_highlighting(self, start, end):
        match = self.MESSAGE_REGEXP.match(self.value)

        green  = self.parent.theme_manager.findPair(self, 'IMPORTANT')
        yellow = self.parent.theme_manager.findPair(self, 'WARNING')
        blue = self.parent.theme_manager.findPair(self, 'NO_EDIT')

        if match:
            highlight = [yellow for _ in range(len(match.group(1)))]
            highlight += [blue for _ in range(len(match.group(2)))]

            self._highlightingdata = highlight


class MessageHighlightPager(npyscreen.Pager):
    _contained_widgets = MessageHighlightTextfield


class SendMessageActionController(npyscreen.ActionControllerSimple):
    def create(self):
        self.add_action('.*', self.send_message, False)

    def send_message(self, command_line, widget_proxy, live):
        self.parent.send_message(command_line)
        self.parent.wMain.values.append(Message(command_line))
        self.parent.wMain.display()


class HistoryRemeberingTextCommandBox(npyscreen.TextCommandBox):
    PROMPT = '[Your message] '

    def __init__(self, *args, **kwargs):
        super(HistoryRemeberingTextCommandBox, self).__init__(history=True, set_up_history_keys=True, *args, **kwargs)

    def update(self, clear=True, cursor=True):
        """Update the contents of the textbox, without calling the final refresh to the screen"""
        # cursor not working. See later for a fake cursor
        #if self.editing: pmfuncs.show_cursor()
        #else: pmfuncs.hide_cursor()

        # Not needed here -- gets called too much!
        #pmfuncs.hide_cursor()

        if clear: self.clear()

        if self.hidden:
            return True

        value_to_use_for_calculations = self.PROMPT + self.value

        if self.ENSURE_STRING_VALUE:
            if value_to_use_for_calculations in (None, False, True):
                value_to_use_for_calculations = ''
                self.value = ''

        if self.begin_at < 0: self.begin_at = 0

        if self.left_margin >= self.maximum_string_length:
            raise ValueError

        if self.editing:
            if isinstance(self.value, bytes):
                # use a unicode version of self.value to work out where the cursor is.
                # not always accurate, but better than the bytes
                value_to_use_for_calculations = self.display_value(self.value).decode(self.encoding, 'replace')
            if cursor:
                if self.cursor_position is False:
                    self.cursor_position = len(value_to_use_for_calculations)

                elif self.cursor_position > len(value_to_use_for_calculations):
                    self.cursor_position = len(value_to_use_for_calculations)

                elif self.cursor_position < len(self.PROMPT):
                    self.cursor_position = len(self.PROMPT)

                if self.cursor_position < self.begin_at:
                    self.begin_at = self.cursor_position

                while self.cursor_position > self.begin_at + self.maximum_string_length - self.left_margin: # -1:
                    self.begin_at += 1
            else:
                if self.do_colors():
                    self.parent.curses_pad.bkgdset(' ', self.parent.theme_manager.findPair(self, self.highlight_color) | curses.A_STANDOUT)
                else:
                    self.parent.curses_pad.bkgdset(' ',curses.A_STANDOUT)



        # Do this twice so that the _print method can ignore it if needed.
        if self.highlight:
            if self.do_colors():
                if self.invert_highlight_color:
                    attributes=self.parent.theme_manager.findPair(self, self.highlight_color) | curses.A_STANDOUT
                else:
                    attributes=self.parent.theme_manager.findPair(self, self.highlight_color)
                self.parent.curses_pad.bkgdset(' ', attributes)
            else:
                self.parent.curses_pad.bkgdset(' ',curses.A_STANDOUT)


        if self.show_bold:
            self.parent.curses_pad.attron(curses.A_BOLD)
        if self.important and not self.do_colors():
            self.parent.curses_pad.attron(curses.A_UNDERLINE)


        self._print()

        # reset everything to normal
        self.parent.curses_pad.attroff(curses.A_BOLD)
        self.parent.curses_pad.attroff(curses.A_UNDERLINE)
        self.parent.curses_pad.bkgdset(' ',curses.A_NORMAL)
        self.parent.curses_pad.attrset(0)
        if self.editing and cursor:
            self.print_cursor()

    def display_value(self, value):
        value = super(HistoryRemeberingTextCommandBox, self).display_value(value)

        return self.PROMPT + value


class MainWindow(npyscreen.FormMuttActiveWithMenus):
    COMMAND_WIDGET_CLASS = HistoryRemeberingTextCommandBox
    ACTION_CONTROLLER = SendMessageActionController
    MAIN_WIDGET_CLASS = MessageHighlightPager

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

    def while_waiting(self):
        while (not self.protocol.queue.empty()):
            self.dispatch(self.protocol.queue.get())

    def dispatch(self, message):
        if isinstance(message, TextMessage):
            self.wMain.values.append(Message(message.content, self.protocol.participant_name))
            self.wMain.display()
        if isinstance(message, DisconnectMessage):
            self.exit_application()


    def send_message(self, message):
        self.protocol.send_message(message)

    def exit_application(self):
        self.protocol.disconnect()

        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()


class BobApplication(npyscreen.NPSAppManaged):
    def __init__(self, protocol):
        super(BobApplication, self).__init__()
        self.protocol = protocol

    def onStart(self):
        F = MainWindow(protocol)
        F.wStatus1.value = "History "
        F.wStatus2.value = "{}         Encryption: None ".format(self.protocol.panel_caption)
        F.value.set_values([])
        F.wMain.values = F.value.get()

        self.registerForm('MAIN', F)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bob - Simple and safe instant messaging')
    parser.add_argument('-l', '--listen', action='store_true', help='Start in server mode (listen on specified port)')
    parser.add_argument('--port', '-p', default=1306, help='Port used for communication (to listen to, or to connect to)')
    parser.add_argument('hostname', nargs='?', default='localhost', help='Host to which connect when running in client mode')

    args = parser.parse_args()

    protocol = Server(args.port) if args.listen else Client(args.hostname, args.port)
    protocol.start()
    App = BobApplication(protocol)
    App.run()
