import npyscreen

from gui.main_window import MainWindow


class BobApplication(npyscreen.NPSAppManaged):
    def __init__(self, protocol, encryption):
        super(BobApplication, self).__init__()
        self.protocol = protocol
        self.initial_encryption = encryption

    def onStart(self):
        F = MainWindow(self.protocol, self.initial_encryption)
        F.wStatus1.value = "History "
        F.value.set_values([])
        F.wMain.values = F.value.get()

        self.registerForm('MAIN', F)
