import npyscreen
from hexdump import dump


class CertificateVerificationResultPopup(npyscreen.Popup):
    DEFAULT_COLUMNS = 120
    DEFAULT_LINES = 16

    def __init__(self, certificate_verification_result):
        self.certificate_verification_result = certificate_verification_result

        super(CertificateVerificationResultPopup, self).__init__(name='Certificate received')

    def create(self):
        self.add(npyscreen.TitleFixedText, name='Issuer', begin_entry_at=25,
                 value=self._get_issuer(self.certificate_verification_result.received_certificate))
        self.add(npyscreen.TitleFixedText, name='Subject', begin_entry_at=25,
                 value=self._get_subject(self.certificate_verification_result.received_certificate))
        self.add(npyscreen.TitleFixedText, name='Serial number', begin_entry_at=25,
                 value=str(self.certificate_verification_result.received_certificate.serial_number))
        self.add(npyscreen.TitleFixedText, name='Version', begin_entry_at=25,
                 value=str(self.certificate_verification_result.received_certificate.version.name))
        self.add(npyscreen.TitleFixedText, name='Not valid before', begin_entry_at=25,
                 value=str(self.certificate_verification_result.received_certificate.not_valid_before))
        self.add(npyscreen.TitleFixedText, name='Not valid after', begin_entry_at=25,
                 value=str(self.certificate_verification_result.received_certificate.not_valid_after))

        self.add(npyscreen.TitleFixedText, name='Received certificate', begin_entry_at=25, rely=10,
                 value=dump(self.certificate_verification_result.received_certificate.signature))
        self.add(npyscreen.TitleFixedText, name='Received hash', begin_entry_at=25, rely=11,
                 value=dump(self.certificate_verification_result.received_hash))
        self.add(npyscreen.TitleFixedText, name='Calculated hash', begin_entry_at=25, rely=12,
                 value=dump(self.certificate_verification_result.calculated_hash))

    def edit(self):
        self.editw = 9
        self.preserve_selected_widget = True
        super(CertificateVerificationResultPopup, self).edit()

    def _get_issuer(self, certificate):
        return list(certificate.issuer.rdns[0]._attributes)[0].value

    def _get_subject(self, certificate):
        return list(list(certificate.subject._attributes)[0]._attributes)[0].value
