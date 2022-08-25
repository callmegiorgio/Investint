import itertools
import cvm
import zipfile
from investint import importing, models

class DfpItrWorker(importing.ZipWorker, importing.SqlWorker):
    """Implements a `Worker` that imports data from DFP/ITR files."""

    def readZipFile(self, file: zipfile.ZipFile):
        """Implements `readZipFile()` to import DFP/ITR documents into the database."""

        try:
            # for dfpitr in itertools.islice(cvm.csvio.dfpitr_reader(file), 10):
            for dfpitr in cvm.csvio.dfpitr_reader(file):
                self.readDfpItr(dfpitr)

                if self.isStopRequested():
                    self.rollback()
                    return

        except Exception:
            self.sendTracebackMessage()
        else:
            self.commit()

    def readDfpItr(self, dfpitr: cvm.datatypes.DFPITR):
        """First, creates the following ORM-mapped objects:
        - `models.Document` from `dfpitr`;
        - `models.Statement` for each financial statement in `dfpitr`;
        - `models.IncomeStatement` from the DRE statement of `dfpitr`;
        - `models.BalanceSheet` from the BPA and BPP statements of `dfpitr`.
        
        Then, for each ORM-mapped object `o`, calls `merge(o)`.
        """

        summary = (
            f"{dfpitr.type.name} id {dfpitr.id} by company '{dfpitr.company_name}' "
            f"(version: {dfpitr.version})"
        )

        self.sendMessage('Reading ' + summary)

        doc = models.Document.fromDfpItr(dfpitr)
        
        if len(doc.statements) == 0:
            self.sendMessage('...no statements')
        else:
            found_bpa = False
            found_bpp = False
            found_dre = False
            
            for stmt in doc.statements:
                self.sendMessage(f'...found {stmt.statement_type} ({stmt.balance_type})')

                if stmt.balance_type != cvm.datatypes.BalanceType.CONSOLIDATED:
                    continue
            
                if   stmt.statement_type == cvm.datatypes.StatementType.BPA: found_bpa = True
                elif stmt.statement_type == cvm.datatypes.StatementType.BPP: found_bpp = True
                elif stmt.statement_type == cvm.datatypes.StatementType.DRE: found_dre = True

            if found_bpa and found_bpp:
                doc.balance_sheet = models.BalanceSheet.from_document(dfpitr)
                self.sendMessage('...generated Balance Sheet')

            if found_dre:
                doc.income_statement = models.IncomeStatement.from_document(dfpitr)
                self.sendMessage('...generated Income Statement')

        self.merge(doc)