import itertools
import cvm
import zipfile
from investint import importing, models

class DfpItrWorker(importing.ZipWorker, importing.SqlWorker):
    """Implements a `Worker` that imports data from DFP/ITR files."""

    @staticmethod
    def documentSummary(document: cvm.datatypes.DFPITR, balance_type: cvm.datatypes.BalanceType):
        return (
            f"{document.type.name} id {document.id} by company '{document.company_name}' "
            f"(version: {document.version}, balance type: {balance_type})"
        )

    def readZipFile(self, file: zipfile.ZipFile):
        """Implements `readZipFile()` to import DFP/ITR documents into the database."""

        try:
            # for doc in itertools.islice(cvm.csvio.dfpitr_reader(file), 10):
            for doc in cvm.csvio.dfpitr_reader(file):
                # if 'CIA SEGUROS' not in doc.company_name.upper():
                #     continue

                for balance_type in cvm.datatypes.BalanceType:
                    self.readDocument(doc, balance_type)

        except Exception:
            self.sendTracebackMessage()
        else:
            self.commit()

    def readDocument(self, document: cvm.datatypes.DFPITR, balance_type: cvm.datatypes.BalanceType):
        """First, creates the following ORM-mapped objects:
        - `models.Statement` for each financial statement in `document`;
        - `models.IncomeStatement` from the DRE statement of `document`;
        - `models.BalanceSheet` from the BPA and BPP statements of `document`.
        
        Then, for each ORM-mapped object `o`, calls `merge(o)`.
        """

        stmts = models.Statement.fromDocument(document, balance_type)

        self.sendMessage('Reading document ' + self.documentSummary(document, balance_type) + '...')

        if len(stmts) == 0:
            self.sendMessage('...no statements')
            return

        bpa = None
        bpp = None
        dre = None

        for stmt in stmts:
            self.merge(stmt)
            self.sendMessage('...imported ' + str(stmt.statement_type))

            if balance_type == cvm.datatypes.BalanceType.CONSOLIDATED:
                if stmt.statement_type == cvm.datatypes.StatementType.DRE:
                    dre = stmt
                elif stmt.statement_type == cvm.datatypes.StatementType.BPA:
                    bpa = stmt
                elif stmt.statement_type == cvm.datatypes.StatementType.BPP:
                    bpp = stmt

        if balance_type == cvm.datatypes.BalanceType.CONSOLIDATED:
            if bpa is not None and bpp is not None:
                balance_sheet = models.BalanceSheet.from_document(document, balance_type=balance_type, bpa=bpa, bpp=bpp)
                self.merge(balance_sheet)
                self.sendMessage('...generated Balance Sheet')
            else:
                self.sendMessage('...could not generate balance sheet because there is no BPA or BPP statement')

            if dre is not None:
                income_stmt = models.IncomeStatement.from_document(document, balance_type=balance_type, dre=dre)
                self.merge(income_stmt)
                self.sendMessage('...generated Income Statement')
            else:
                self.sendMessage('...could not generate balance sheet because there is no DRE statement')