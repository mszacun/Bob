from npyscreen.utilNotify import ConfirmCancelPopup
import npyscreen


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
