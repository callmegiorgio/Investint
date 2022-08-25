import dataclasses
import icvm
import typing
from PyQt5     import QtCore
from investint import models

class CompanyProfitabilityModel(models.CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = {
            'roe':            'ROE',
            'roa':            'ROA',
            'roic':           'ROIC',
            'asset_turnover': 'Giro de Ativo'
        }

        super().__init__(mapped_row_names, parent)

        for row in range(self.rowCount() - 1):
            self.setPercentRow(row, True)
    
    def appendProfitability(self, year: int, profitability: icvm.Profitability):
        self.append(year, dataclasses.asdict(profitability))