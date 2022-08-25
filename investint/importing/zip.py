import zipfile
from investint import importing

class ZipWorker(importing.Worker):
    """Implements a `Worker` that reads Zip files.
    
    This class implements the method `read()` to open a Zip file
    and passes it to `readZipFile()`, which may be implemented by
    subclasses to process the file.
    """

    def read(self, filepath: str):
        """Tries to open `filepath` as a Zip file.
        
        If `filepath` is not a file path or is not a Zip file,
        sends a message describing the error. Otherwise, calls
        `readZipFile()` passing in the Zip file as a parameter.
        Finally, emits the signal `finished` and returns.
        """

        try:
            with zipfile.ZipFile(filepath) as zip_file:
                self.readZipFile(zip_file)

        except (zipfile.BadZipFile, FileNotFoundError) as exc:
            self.sendMessage(f"Could not open file '{filepath}': {exc.__class__.__name__} {str(exc)}")
            
        finally:
            self._finish()

    def readZipFile(self, file: zipfile.ZipFile):
        pass