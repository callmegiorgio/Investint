import cvm
import datetime
import sqlalchemy as sa
import typing
from PyQt5     import QtCore
from investint import models

class CompanyIncomeStatementModel(models.CompanyStatementModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = {
            'revenue':                       'Receita',
            'costs':                         'Custos',
            'gross_profit':                  'Lucro Bruto',
            'operating_income_and_expenses': 'Receitas e Despesas Operacionais',
            'operating_result':              'Resultado Operacional (EBITDA)',
            'depreciation_and_amortization': 'Depreciação e Amortização',
            'operating_profit':              'Lucro Operacional (EBIT)',
            'nonoperating_result':           'Resultado Não Operacional (Resultado Financeiro)',
            'earnings_before_tax':           'Resultado Antes dos Tributos sobre o Lucro (EBT)',
            'tax_expenses':                  'Imposto de Renda e Contribuição Social sobre o Lucro',
            'continuing_operation_result':   'Resultado Líquido das Operações Continuadas',
            'discontinued_operation_result': 'Resultado Líquido das Operações Descontinuadas',
            'net_income':                    'Lucro Líquido'
        }

        super().__init__(mapped_row_names, parent)

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