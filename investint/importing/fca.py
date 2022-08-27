import cvm
import typing
import zipfile
from investint import importing, models

class FcaWorker(importing.ZipWorker, importing.SqlWorker):
    """Implements a `Worker` that reads FCA files."""

    ################################################################################
    # Overriden methods
    ################################################################################
    def reader(self, file: typing.IO) -> typing.Iterable[typing.Any]:
        """Reimplements `Worker.reader()` to open a FCA document reader."""

        return cvm.csvio.fca_reader(file)

    def readOne(self, obj: typing.Any):
        """Reimplements `Worker.readOne()` to read
        and import an FCA document to `session()`.
        """

        fca: cvm.datatypes.FCA = obj
        co = models.PublicCompany.fromFCA(fca)

        summary = f"FCA id {fca.id} by company '{fca.company_name}' (version: {fca.version})"

        self.emitMessage('Reading ' + summary)

        if co is None:
            self.emitMessage('...missing issuer company')
        else:
            self.merge(co)
            self.emitMessage('...imported')