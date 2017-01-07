import os

from hexdump import dump, dehex
from npyscreen.utilNotify import ConfirmCancelPopup
import npyscreen
from npyscreen.wgwidget import EXITED_DOWN, EXITED_UP

from encryption.ciphers import AESCipher

class HexTextfield(npyscreen.Textfield):
    HEX_DIGITS = '1234567890abcdefABCDEFG'
    def h_addch(self, inp):
        character = chr(inp)
        if character in self.HEX_DIGITS:
            upper = character.upper()
            super(HexTextfield, self).h_addch(ord(upper))


class TitleHexTextfield(npyscreen.TitleText):
    _entry_type = HexTextfield


class GenerateBytesButton(npyscreen.MiniButtonPress):
    def __init__(self, *args, **kwargs):
        super(GenerateBytesButton, self).__init__(*args, **kwargs)
        self.number_of_bytes_to_generate = kwargs['number_of_bytes_to_generate']
        self.target_textbox = kwargs['target_textbox']

    def whenPressed(self):
        self.target_textbox.value = self._get_hexified_bytes(self.number_of_bytes_to_generate)
        self.target_textbox.display()

    def _get_hexified_bytes(self, number_of_bytes):
        return dump(os.urandom(number_of_bytes), sep='')


class AESEncryptionConfigurationPopup(ConfirmCancelPopup):
    DEFAULT_COLUMNS = 100

    def __init__(self, his_public_key, my_private_key):
        super(AESEncryptionConfigurationPopup, self).__init__(name='Configure AES cipher')

        self.his_public_key = his_public_key
        self.my_private_key = my_private_key

    def create(self):
        self.key_textbox = self.add(TitleHexTextfield, name='Key', value='')
        self.iv_textbox = self.add(TitleHexTextfield, name='IV', value='')
        self.add(npyscreen.FixedText, value='Generate key:', rely=5, editable=False)
        self.generate_16_bytes_key = self.add(GenerateBytesButton, name='16 bytes', rely=5, relx=15,
                                              number_of_bytes_to_generate=16, target_textbox=self.key_textbox)
        self.generate_24_bytes_key = self.add(GenerateBytesButton, name='24 bytes', rely=5, relx=35,
                                              number_of_bytes_to_generate=24, target_textbox=self.key_textbox)
        self.generate_32_bytes_key = self.add(GenerateBytesButton, name='32 bytes', rely=5, relx=55,
                                              number_of_bytes_to_generate=32, target_textbox=self.key_textbox)

        self.add(npyscreen.FixedText, value='Generate IV:', rely=6, editable=False)
        self.generate_iv = self.add(GenerateBytesButton, name='16 bytes', rely=6, relx=15,
                                    number_of_bytes_to_generate=AESCipher.IV_LENGTH, target_textbox=self.iv_textbox)
        self.send_key_using_rsa = self.add(npyscreen.Checkbox, name='Send key using RSA', rely=8)
        self.preserve_selected_widget = True

    def on_ok(self):
        self.value = True
        return not (self._validate_length('key', self.key_textbox.value, AESCipher.ALLOWED_KEY_LENGTHS) and
                    self._validate_length('IV', self.iv_textbox.value, [AESCipher.IV_LENGTH]))

    def handle_exiting_widgets(self, exit_condition):
        KEY_16_BYTES_BUTTON_EDITW = 3
        KEY_24_BYTES_BUTTON_EDITW = 4
        KEY_32_BYTES_BUTTON_EDITW = 5
        KEY_BUTTONS = (KEY_16_BYTES_BUTTON_EDITW, KEY_24_BYTES_BUTTON_EDITW, KEY_32_BYTES_BUTTON_EDITW)

        GENERATE_IV_BUTTON_EDITW = 7

        if exit_condition == EXITED_DOWN and  self.editw in KEY_BUTTONS:
            self.editw = GENERATE_IV_BUTTON_EDITW
        elif exit_condition == EXITED_UP and self.editw == GENERATE_IV_BUTTON_EDITW:
            self.editw = KEY_16_BYTES_BUTTON_EDITW
        else:
            super(AESEncryptionConfigurationPopup, self).handle_exiting_widgets(exit_condition)

    def _validate_length(self, what_is_validated, to_validate, allowed_lengths):
        error_message = 'Invalid {} length: {} (must be one of: {} bytes)'.format(
            what_is_validated, len(to_validate) / 2.0, ', '.join(str(l) for l in allowed_lengths))

        if not len(to_validate) in self._convert_to_hex_lengths(allowed_lengths):
            npyscreen.notify_confirm(title="Error", message=error_message)
            return False

        return True

    def build_encryption(self):
        key = dehex(self.key_textbox.value)
        iv = dehex(self.iv_textbox.value)

        if self.send_key_using_rsa.value:
            return AESCipher(key=key, iv=iv, his_public_key=self.his_public_key, my_private_key=self.my_private_key)
        else:
            return AESCipher(key=key, iv=iv)

    def _convert_to_hex_lengths(self, allowed_lengths):
        return [l * 2 for l in allowed_lengths]
