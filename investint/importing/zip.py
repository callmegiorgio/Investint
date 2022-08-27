import typing
import zipfile
from investint import importing

class ZipWorker(importing.Worker):
    """Implements a `Worker` that reads Zip files."""

    ################################################################################
    # Overriden methods
    ################################################################################
    def open(self, filepath: str) -> zipfile.ZipFile:
        """Reimplementation of `Worker.open()` to open a `ZipFile`."""

        return zipfile.ZipFile(filepath)