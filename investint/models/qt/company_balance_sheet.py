import cvm
import datetime
import sqlalchemy as sa
import typing
from PyQt5     import QtCore
from investint import models

class CompanyBalanceSheetModel(models.CompanyStatementModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = {
            'total_assets':                   'Ativo Total',
            'current_assets':                 'Ativo Circulante',
            'cash_and_cash_equivalents':      'Caixa e Equivalente de Caixa',
            'financial_investments':          'Aplicações Financeiras',
            'receivables':                    'Recebíveis',
            'noncurrent_assets':              'Ativo Não Circulante',
            'investments':                    'Investimentos',
            'fixed_assets':                   'Imobilizado',
            'intangible_assets':              'Intangível',
            'total_liabilities':              'Passivo Total',
            'current_liabilities':            'Passivo Circulante',
            'current_loans_and_financing':    'Empréstimos e Financiamentos',
            'noncurrent_liabilities':         'Passivo Não Circulante',
            'noncurrent_loans_and_financing': 'Empréstimos e Financiamentos',
            'equity':                         'Patrimônio Líquido'
        }

        super().__init__(mapped_row_names, parent)

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