import cvm
import typing
from investint import importing, models

__all__ = [
    'DfpItrWorker'
]

class DfpItrWorker(importing.ZipWorker, importing.SqlWorker):
    """Implements a `Worker` that imports data from DFP/ITR files.
    
    The constructor of this class takes a file path and an iterable
    of CNPJ strings. The file path specifies the file to be opened,
    whereas the CNPJ iterable is used to filter which companies
    to import.
    
    Upon execution of `run()`, the file path is opened as a Zip
    file and a DFP/ITR reader is created to iterate through all
    DFP/ITR documents in that file, as follows. If this class
    received one or more CNPJs upon construction, import only
    companies whose CNPJ matches the given CNPJs. Otherwise,
    import all companies.

    Note that CNPJs are expected to be digit-only strings without
    leading zeroes. For example, "191" rather than "00000000000191".
    """

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, listed_cnpjs: typing.Iterable[str], filepath: str) -> None:
        super().__init__(filepath=filepath)

        self._listed_cnpjs = set(listed_cnpjs)
        self._is_filtering = len(self._listed_cnpjs) > 0
        self._last_cnpj    = None

    ################################################################################
    # Overriden methods
    ################################################################################
    def reader(self, file: typing.IO) -> typing.Iterable[typing.Any]:
        """Reimplements `Worker.reader()` to return a DFP/ITR document reader."""

        return cvm.csvio.dfpitr_reader(file)

    def readOne(self, obj: typing.Any):
        """Reimplements `Worker.readOne()` to read and import a DFP/ITR document."""

        dfpitr: cvm.datatypes.DFPITR = obj

        summary = (
            f"{dfpitr.type.name} id {dfpitr.id} by company '{dfpitr.company_name}' "
            f"(version: {dfpitr.version})"
        )

        self.emitMessage('Reading ' + summary)

        cnpj = dfpitr.cnpj.digits()

        if self._is_filtering and cnpj not in self._listed_cnpjs:
            self.emitMessage('...unlisted CNPJ, skipping')
        else:
            self.importDocument(dfpitr)

        self._updateListedCnpjs(cnpj)

    ################################################################################
    # Public methods
    ################################################################################
    def importDocument(self, dfpitr: cvm.datatypes.DFPITR):
        """First, creates the following ORM-mapped objects:
        - `models.Document` from `dfpitr`;
        - `models.Statement` for each financial statement in `dfpitr`;
        - `models.IncomeStatement` from the DRE statement of `dfpitr`;
        - `models.BalanceSheet` from the BPA and BPP statements of `dfpitr`.
        
        Then, for each ORM-mapped object `o`, calls `merge(o)`.
        """

        company = models.PublicCompany.findByCNPJ(dfpitr.cnpj.digits(), self.session())

        if company is None:
            self.emitMessage('...company not found in the database, skipping')
            return

        doc = models.Document.fromDfpItr(dfpitr)
        doc.company = company

        if len(doc.statements) == 0:
            self.emitMessage('...no statements')
        else:
            found_bpa = False
            found_bpp = False
            found_dre = False
            
            for stmt in doc.statements:
                self.emitMessage(f'...found {stmt.statement_type} ({stmt.balance_type})')

                if stmt.balance_type != cvm.datatypes.BalanceType.CONSOLIDATED:
                    continue
            
                if   stmt.statement_type == cvm.datatypes.StatementType.BPA: found_bpa = True
                elif stmt.statement_type == cvm.datatypes.StatementType.BPP: found_bpp = True
                elif stmt.statement_type == cvm.datatypes.StatementType.DRE: found_dre = True

            if found_bpa and found_bpp:
                doc.balance_sheet = models.BalanceSheet.from_dfpitr(dfpitr)
                self.emitMessage('...generated Balance Sheet')

            if found_dre:
                doc.income_statement = models.IncomeStatement.from_dfpitr(dfpitr)
                self.emitMessage('...generated Income Statement')

        self.merge(doc)

    ################################################################################
    # Private methods
    ################################################################################
    def _updateListedCnpjs(self, cnpj: str):
        if not self._is_filtering:
            return
        
        if self._last_cnpj is None:
            self._last_cnpj = cnpj
        elif self._last_cnpj == cnpj:
            return
        else:
            self._listed_cnpjs.discard(self._last_cnpj)
            
            if len(self._listed_cnpjs) == 0:
                self.emitMessage('Finished reading all documents with the given CNPJs')
                raise StopIteration()
            else:
                self._last_cnpj = cnpj