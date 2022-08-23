import cvm
import zipfile
from investint import importing, models

class FcaWorker(importing.ZipWorker, importing.SqlWorker):
    """Implements a `Worker` that reads FCA files."""

    @staticmethod
    def documentSummary(fca: cvm.datatypes.FCA):
        return f"FCA id {fca.id} by company '{fca.company_name}' (version: {fca.version})"

    def readZipFile(self, file: zipfile.ZipFile):
        """Implements `readZipFile()` to import FCA documents into the database."""

        try:
            for fca in cvm.csvio.fca_reader(file):
                self.readDocument(fca)

        except Exception:
            self.sendTracebackMessage()
        else:
            self.commit()

    def readDocument(self, fca: cvm.datatypes.FCA):
        """Creates a `models.PublicCompany` from `fca` and merges it into the database."""

        co = models.PublicCompany.fromFCA(fca)

        self.sendMessage('Reading ' + self.documentSummary(fca) + '...')

        if co is None:
            self.sendMessage('...missing issuer company')
        else:
            self.merge(co)
            self.sendMessage('...imported')