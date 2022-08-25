import dataclasses
import icvm
import typing
from PyQt5     import QtCore
from investint import models

class CompanyEfficiencyModel(models.CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = {
            'gross_margin':  'Margem Bruta',
            'ebitda_margin': 'Margem EBITDA',
            'ebit_margin':   'Margem EBIT',
            'net_margin':    'Margem Líquida'
        }

        super().__init__(mapped_row_names, parent)

        for row in range(self.rowCount()):
            self.setPercentRow(row, True)

    def appendEfficiency(self, year: int, efficiency: icvm.Efficiency):
        self.append(year, dataclasses.asdict(efficiency))