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
                        cnpj: int,
                        start_date: datetime.date,
                        end_date: datetime.date,
                        document_type: cvm.datatypes.DocumentType
    ) -> sa.select:

        B = models.BalanceSheet
        S = models.Statement

        return (
            sa.select(S.reference_date, B)
              .join(S, B.bpa_id == S.id)
              .where(S.cnpj == cnpj)
              .where(S.reference_date.between(start_date, end_date))
              .where(S.document_type == document_type)
              .order_by(S.reference_date.asc())
        )