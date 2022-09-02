import cvm
import datetime
import sqlalchemy as sa
import typing
from PyQt5     import QtCore
from investint import models

class CompanyBalanceSheetModel(models.CompanyStatementModel):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = [
            'total_assets',
            'current_assets',
            'cash_and_cash_equivalents',
            'financial_investments',
            'receivables',
            'noncurrent_assets',
            'investments',
            'fixed_assets',
            'intangible_assets',
            'total_liabilities',
            'current_liabilities',
            'current_loans_and_financing',
            'noncurrent_liabilities',
            'noncurrent_loans_and_financing',
            'equity'
        ]

        super().__init__(mapped_row_names, parent)
        self.retranslateUi()

    ################################################################################
    # Public methods
    ################################################################################
    def retranslateUi(self):
        self.setRowName(0,  self.tr('Total Assets'))
        self.setRowName(1,  self.tr('Current Assets'))
        self.setRowName(2,  self.tr('Cash and Cash Equivalents'))
        self.setRowName(3,  self.tr('Financial Investments'))
        self.setRowName(4,  self.tr('Receivables'))
        self.setRowName(5,  self.tr('Noncurrent Assets'))
        self.setRowName(6,  self.tr('Investments'))
        self.setRowName(7,  self.tr('Fixed Assets'))
        self.setRowName(8,  self.tr('Intangible Assets'))
        self.setRowName(9,  self.tr('Total Liabilities'))
        self.setRowName(10, self.tr('Current Liabilities'))
        self.setRowName(11, self.tr('Current Loans and Financing'))
        self.setRowName(12, self.tr('Non-Current Liabilities'))
        self.setRowName(13, self.tr('Non-Current Loans and Financing'))
        self.setRowName(14, self.tr('Equity'))
    
    ################################################################################
    # Overriden methods
    ################################################################################
    def selectStatement(self,
                        cnpj: str,
                        start_date: datetime.date,
                        end_date: datetime.date,
                        document_type: cvm.datatypes.DocumentType
    ) -> sa.select:

        B = models.BalanceSheet
        C = models.PublicCompany
        D = models.Document

        return (
            sa.select(D.reference_date, B)
              .join(D, B.document_id == D.id)
              .join(C, D.company_id  == C.id)
              .where(C.cnpj == cnpj)
              .where(D.reference_date.between(start_date, end_date))
              .where(D.type == document_type)
              .order_by(D.reference_date.asc())
        )

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()

        return super().event(event)