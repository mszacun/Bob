import npyscreen
from npyscreen.utilNotify import ConfirmCancelPopup


class IntegerSlider(npyscreen.Slider):
    def get_value(self):
        return int(super(IntegerSlider, self).get_value())

    def set_value(self, value):
        super(IntegerSlider, self).set_value(value)

    value = property(get_value, set_value)


class TitleIntegerSlider(npyscreen.TitleText):
    _entry_type = IntegerSlider


class CaesarEncryptionConfigurationPopup(ConfirmCancelPopup):
    def __init__(self):
        super(CaesarEncryptionConfigurationPopup, self).__init__(name='Configure Caeser cipher')

    def create(self):
        self.shift_slider = self.add(TitleIntegerSlider, name='Key (shift)', lowest=1, out_of=26, value=3)
        self.preserve_selected_widget = True

    def get_key(self):
        return self.shift_slider.value


class PagerBoxed(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Pager


class MessageDetailsPopup(npyscreen.Popup):
    DEFAULT_LINES = 24

    def __init__(self, message):
        self.preserve_selected_widget = True
        self.message = message

        super(MessageDetailsPopup, self).__init__(name='Message details')

    def create(self):
        self.add(npyscreen.TitleFixedText, name='Author', value=self.message.sender)
        self.add(npyscreen.TitleFixedText, name='Time', value=self.message.formatted_time)
        self.add(npyscreen.TitleFixedText, name='Encryption', value=str(self.message.encryption))
        self.add(PagerBoxed, name='Plaintext', values=[self.message.plaintext], max_height=7, rely=6)
        self.add(PagerBoxed, name='Ciphertext', values=[self.message.ciphertext], max_height=7, rely=14)


    def edit(self):
        self.editw = 5
        self.preserve_selected_widget = True
        super(MessageDetailsPopup, self).edit()
