import os

from hexdump import dump, dehex
from npyscreen.utilNotify import ConfirmCancelPopup
import npyscreen

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


class AESEncryptionConfigurationPopup(ConfirmCancelPopup):
    DEFAULT_COLUMNS = 100

    def __init__(self):
        super(AESEncryptionConfigurationPopup, self).__init__(name='Configure AES cipher')

    def create(self):
        self.key_textbox = self.add(TitleHexTextfield, name='Key',
                                    value=self._get_hexified_bytes(AESCipher.RECOMMENDED_KEY_LENGTH))
        self.iv_textbox = self.add(TitleHexTextfield, name='IV', value=self._get_hexified_bytes(AESCipher.IV_LENGTH))
        self.preserve_selected_widget = True

    def on_ok(self):
        self.value = True
        return not (self._validate_length('key', self.key_textbox.value, AESCipher.ALLOWED_KEY_LENGTHS) and
                    self._validate_length('IV', self.iv_textbox.value, [AESCipher.IV_LENGTH]))

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
        return AESCipher(key=key, iv=iv)

    def _get_hexified_bytes(self, number_of_bytes):
        return dump(os.urandom(number_of_bytes), sep='')

    def _convert_to_hex_lengths(self, allowed_lengths):
        return [l * 2 for l in allowed_lengths]
