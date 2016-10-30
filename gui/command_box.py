import npyscreen
import curses


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
