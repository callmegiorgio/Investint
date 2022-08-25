import dataclasses
import icvm
import typing
from PyQt5     import QtCore
from investint import models

class CompanyIndebtednessModel(models.CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = {
            'general_debt':         'Dívida Geral',
            'debt_composition':     'Composição da Dívida',
            'net_debt_to_equity':   'Div. Líq./PL',
            'net_debt_to_ebitda':   'Div. Líq./EBITDA',
            'net_debt_to_ebit':     'Div. Líq./EBIT',
            'net_equity_to_assets': 'Div. Líq./Ativo',
            'current_ratio':        'Ativo/Passivo',
        }

        super().__init__(mapped_row_names, parent)

    def appendIndebtedness(self, year: int, indebtedness: icvm.Indebtedness):
        self.append(year, dataclasses.asdict(indebtedness))