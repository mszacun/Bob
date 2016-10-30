import npyscreen
import re
import curses


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
            sender_color = blue if match.group(2) == 'You: ' else green

            highlight = [yellow for _ in range(len(match.group(1)))]
            highlight += [sender_color for _ in range(len(match.group(2)))]

            self._highlightingdata = highlight


class MessageHighlightMultiLine(npyscreen.MultiLine):
    _contained_widgets = MessageHighlightTextfield

    def set_up_handlers(self):
        super(MessageHighlightMultiLine, self).set_up_handlers()
        self.handlers.update({
            curses.ascii.NL:    self.show_message_details,
            curses.ascii.CR:    self.show_message_details,
        })

    def show_message_details(self, pressed_key):
        seleted_message = self.values[self.cursor_line]
        npyscreen.notify_confirm(str(seleted_message), title='Message details', editw=1)
