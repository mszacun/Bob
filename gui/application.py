import npyscreen

from gui.main_window import MainWindow


class BobApplication(npyscreen.NPSAppManaged):
    def __init__(self, protocol):
        super(BobApplication, self).__init__()
        self.protocol = protocol

    def onStart(self):
        F = MainWindow(self.protocol)
        F.wStatus1.value = "History "
        F.refresh_statusbar(self.protocol.initial_panel_caption, 'None')
        F.value.set_values([])
        F.wMain.values = F.value.get()

        self.registerForm('MAIN', F)
