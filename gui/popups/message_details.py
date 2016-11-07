import npyscreen


class SynchronizedPager(npyscreen.Pager):
    def h_scroll_line_up(self, ch, synchronize=True):
        super(SynchronizedPager, self).h_scroll_line_up(ch)

        if synchronize:
            self.keep_synchronized_with.entry_widget.h_scroll_line_up(ch, synchronize=False)
            self.keep_synchronized_with.entry_widget.display()

    def h_scroll_line_down(self, ch, synchronize=True):
        super(SynchronizedPager, self).h_scroll_line_down(ch)

        if synchronize:
            self.keep_synchronized_with.entry_widget.h_scroll_line_down(ch, synchronize=False)
            self.keep_synchronized_with.entry_widget.display()

    def h_show_beginning(self, ch, synchronize=True):
        super(SynchronizedPager, self).h_show_beginning(ch)

        if synchronize:
            self.keep_synchronized_with.entry_widget.h_show_beginning(ch, synchronize=False)
            self.keep_synchronized_with.entry_widget.display()

    def h_show_end(self, ch, synchronize=True):
        super(SynchronizedPager, self).h_show_end(ch)

        if synchronize:
            self.keep_synchronized_with.entry_widget.h_show_end(ch, synchronize=False)
            self.keep_synchronized_with.entry_widget.display()

    def h_scroll_page_down(self, ch, synchronize=True):
        super(SynchronizedPager, self).h_scroll_page_down(ch)

        if synchronize:
            self.keep_synchronized_with.entry_widget.h_scroll_page_down(ch, synchronize=False)
            self.keep_synchronized_with.entry_widget.display()

    def h_scroll_page_up(self, ch, synchronize=True):
        super(SynchronizedPager, self).h_scroll_page_up(ch)

        if synchronize:
            self.keep_synchronized_with.entry_widget.h_scroll_page_up(ch, synchronize=False)
            self.keep_synchronized_with.entry_widget.display()


class PagerBoxed(npyscreen.BoxTitle):
    _contained_widget = SynchronizedPager


class MessageDetailsPopup(npyscreen.Popup):
    DEFAULT_LINES = 24
    DEFAULT_COLUMNS = 90

    def __init__(self, message):
        self.preserve_selected_widget = True
        self.message = message

        super(MessageDetailsPopup, self).__init__(name='Message details')

    def create(self):
        self.add(npyscreen.TitleFixedText, name='Sender', value=self.message.sender)
        self.add(npyscreen.TitleFixedText, name='Time', value=self.message.formatted_time)
        self.add(npyscreen.TitleFixedText, name='Encryption', value=str(self.message.encryption))
        self.plaintext = self.add(PagerBoxed, name='Plaintext', values=self.message.plaintext.split('\n'),
                                  max_height=7, rely=6)
        self.ciphertext = self.add(PagerBoxed, name='Ciphertext', values=self.message.ciphertext.split('\n'),
                                   max_height=7, rely=14)

        self.ciphertext.entry_widget.keep_synchronized_with = self.plaintext


    def edit(self):
        self.editw = 5
        self.preserve_selected_widget = True
        super(MessageDetailsPopup, self).edit()
