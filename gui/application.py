import npyscreen

from gui.main_window import MainWindow
from encryption.ciphers import NoneEncryption


class BobApplication(npyscreen.NPSAppManaged):
    def __init__(self, protocol):
        super(BobApplication, self).__init__()
        self.protocol = protocol

    def onStart(self):
        F = MainWindow(self.protocol, NoneEncryption())
        F.wStatus1.value = "History "
        F.value.set_values([])
        F.wMain.values = F.value.get()

        self.registerForm('MAIN', F)
