import npyscreen
from npyscreen.utilNotify import ConfirmCancelPopup


class CaesarEncryptionConfigurationPopup(ConfirmCancelPopup):
    def __init__(self):
        super(CaesarEncryptionConfigurationPopup, self).__init__(name='Configure Caeser cipher')

    def create(self):
        self.shift_slider = self.add(npyscreen.TitleSlider, name='Key (shift)', lowest=1, out_of=26, value=3)
        self.preserve_selected_widget = True

    def get_key(self):
        return self.shift_slider.value
