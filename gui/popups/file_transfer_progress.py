import npyscreen

from etaprogress.progress import ProgressBarWget

from messages import FileChunkMessage, FileReceivingCompleteMessage
from gui.utils import humanize_bytes
from gui.history import FileTransfer


class ProcessBar(npyscreen.SliderPercent):
    def __init__(self, *args, **keywords):
        super(ProcessBar, self).__init__(*args, **keywords)
        self.editable = False


class ProcessBarBox(npyscreen.BoxTitle):
    _contained_widget = ProcessBar


class FileTransferProgressPopup(npyscreen.Popup):
    def __init__(self, filename, save_destination, expected_number_of_bytes, protocol):
        self.expected_number_of_bytes = expected_number_of_bytes
        self.filename = filename
        self.eta_progressbar = ProgressBarWget(expected_number_of_bytes, max_width=20)
        self.protocol = protocol
        self.save_destination = save_destination

        super(FileTransferProgressPopup, self).__init__(name='File transfer in progress')

    def create(self):
        self.keypress_timeout = 1

        self.add(npyscreen.TitleFixedText, name='Filename:', value=self.filename, editable=False)
        self.speed = self.add(npyscreen.TitleFixedText, name='Avg. speed:', value='', editable=False)
        self.bytes_received = self.add(npyscreen.TitleFixedText, name='Completed', value = '-', editable=False)
        self.eta = self.add(npyscreen.TitleFixedText, name='ETA:', value='--:--', editable=False)
        self.progressbar = self.add(ProcessBar, value=0, out_of=self.expected_number_of_bytes, rely=7)

    def set_progress(self, number_of_bytes_received_so_far):
        number_of_bytes_received_so_far = min(number_of_bytes_received_so_far, self.expected_number_of_bytes) #FIXME
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
        if isinstance(message, FileReceivingCompleteMessage):
            self.file_transfer = FileTransfer(self.protocol.encryption, self.save_destination, message.plaintext,
                                              message.ciphertext, self.protocol.participant_name)
