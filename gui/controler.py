import npyscreen


class SendMessageActionController(npyscreen.ActionControllerSimple):
    def create(self):
        self.add_action('.*', self.send_message, False)

    def send_message(self, command_line, widget_proxy, live):
        self.parent.send_message(command_line)
