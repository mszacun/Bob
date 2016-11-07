from npyscreen.utilNotify import ConfirmCancelPopup
import npyscreen


class UppercaseTextfield(npyscreen.Textfield):
    def h_addch(self, inp):
        character = chr(inp)
        if character.isalpha():
            upper = character.upper()
            super(UppercaseTextfield, self).h_addch(ord(upper))


class TitleUppercaseTextfield(npyscreen.TitleText):
    _entry_type = UppercaseTextfield


class VigenereEncryptionConfigurationPopup(ConfirmCancelPopup):
    def __init__(self):
        super(VigenereEncryptionConfigurationPopup, self).__init__(name='Configure Vigenere cipher')

    def create(self):
        self.key_textbox = self.add(TitleUppercaseTextfield, name='Key')
        self.preserve_selected_widget = True

    def get_key(self):
        return self.key_textbox.value
