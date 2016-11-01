import npyscreen
from npyscreen.utilNotify import ConfirmCancelPopup

from etaprogress.progress import ProgressBarWget

from messages import FileChunkMessage
from utils import humanize_bytes


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


class ProcessBar(npyscreen.SliderPercent):
    def __init__(self, *args, **keywords):
        super(ProcessBar, self).__init__(*args, **keywords)
        self.editable = False

class ProcessBarBox(npyscreen.BoxTitle):
    _contained_widget = ProcessBar


class FileTransferProgressPopup(npyscreen.Popup):
    def __init__(self, filename, expected_number_of_bytes, protocol):
        self.expected_number_of_bytes = expected_number_of_bytes
        self.filename = filename
        self.eta_progressbar = ProgressBarWget(expected_number_of_bytes, max_width=20)
        self.protocol = protocol

        super(FileTransferProgressPopup, self).__init__(name='File transfer in progress')

    def create(self):
        self.keypress_timeout = 1

        self.add(npyscreen.TitleFixedText, name='Filename:', value=self.filename, editable=False)
        self.speed = self.add(npyscreen.TitleFixedText, name='Avg. speed:', value='', editable=False)
        self.bytes_received = self.add(npyscreen.TitleFixedText, name='Completed', value = '-', editable=False)
        self.eta = self.add(npyscreen.TitleFixedText, name='ETA:', value='--:--', editable=False)
        self.progressbar = self.add(ProcessBar, value=0, out_of=self.expected_number_of_bytes, rely=7)

    def set_progress(self, number_of_bytes_received_so_far):
        self.progressbar.value = number_of_bytes_received_so_far
        self.progressbar.display()

        self.eta_progressbar.numerator = number_of_bytes_received_so_far

        self.eta.value = self.eta_progressbar._eta_string
        self.eta.display()

        completed_str = '{} / {}'.format(humanize_bytes(number_of_bytes_received_so_far),
                                         humanize_bytes(self.expected_number_of_bytes))
        self.bytes_received.value = completed_str
        self.bytes_received.display()

        self.speed.value = self.eta_progressbar.str_rate
        self.speed.display()

    def while_waiting(self):
        while not self.protocol.queue.empty():
            self.dispatch(self.protocol.queue.get())

    def dispatch(self, message):
        if isinstance(message, FileChunkMessage):
            self.set_progress(message.number_of_bytes_received_so_far)
