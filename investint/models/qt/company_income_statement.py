import cvm
import datetime
import sqlalchemy as sa
import typing
from PyQt5     import QtCore
from investint import models

__all__ = [
    'CompanyIncomeStatementModel'
]

class CompanyIncomeStatementModel(models.CompanyStatementModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = [
            'revenue',
            'costs',
            'gross_profit',
            'operating_income_and_expenses',
            'operating_result',
            'depreciation_and_amortization',
            'operating_profit',
            'nonoperating_result',
            'earnings_before_tax',
            'tax_expenses',
            'continuing_operation_result',
            'discontinued_operation_result',
            'net_income'
        ]

        super().__init__(mapped_row_names, parent)
        self.retranslateUi()

    ################################################################################
    # Public methods
    ################################################################################
    def retranslateUi(self):
        self.setRowName(0,  self.tr('Revenue'))
        self.setRowName(1,  self.tr('Costs'))
        self.setRowName(2,  self.tr('Gross Profit'))
        self.setRowName(3,  self.tr('Operating Income and Expenses'))
        self.setRowName(4,  self.tr('EBITDA'))
        self.setRowName(5,  self.tr('Depreciation and Amortization'))
        self.setRowName(6,  self.tr('EBIT'))
        self.setRowName(7,  self.tr('Non-Operating Result'))
        self.setRowName(8,  self.tr('Earnings Before Tax'))
        self.setRowName(9,  self.tr('Tax Expenses'))
        self.setRowName(10, self.tr('Continuing Operation Result'))
        self.setRowName(11, self.tr('Discontinued Operation Result'))
        self.setRowName(12, self.tr('Net Income'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def selectStatement(self,
                        cnpj: str,
                        start_date: datetime.date,
                        end_date: datetime.date,
                        document_type: cvm.datatypes.DocumentType
    ) -> sa.select:

        I = models.IncomeStatement
        C = models.PublicCompany
        D = models.Document

        return (
            sa.select(D.reference_date, I)
              .join(D, I.document_id == D.id)
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