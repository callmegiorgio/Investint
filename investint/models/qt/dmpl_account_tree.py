import cvm
import dataclasses
import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
import typing
from PyQt5     import QtCore
from investint import database, models

__all__ = [
    'DMPLAccountTreeModel'
]

class DMPLAccountTreeModel(models.AccountTreeModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None):
        super().__init__(parent=parent)

        self._column_dataset = (
            'share_capital',
            'capital_reserve_and_treasury_shares',
            'profit_reserves',
            'unappropriated_retained_earnings',
            'other_comprehensive_income',
            'controlling_interest',
            'non_controlling_interest',
            'consolidated_equity'
        )

        self.retranslateUi()

    def select(self, statement: models.Statement) -> None:
        self.clear()

        if statement.statement_type != cvm.StatementType.DMPL:
            return

        A: models.DMPLAccount = sa_orm.aliased(models.DMPLAccount, name='a')

        select_stmt = sa.select(A).where(A.statement_id == statement.id)
        session     = database.Session()
        results     = session.execute(select_stmt).all()

        if statement.balance_type == cvm.BalanceType.CONSOLIDATED:
            column_dataset = self._column_dataset
        else:
            column_dataset = self._column_dataset[:-1]

        self.setNumericColumnCount(len(column_dataset))
        
        for column, column_data, in enumerate(column_dataset):
            self.setNumericColumnData(column, column_data)

        for row in results:
            account: models.DMPLAccount = row[0]
            quantities = dataclasses.asdict(account)

            self.append(account.code, account.name, quantities)
        
        self.buildTree()

    def numericColumnText(self, column: int) -> str:
        column_data: str = self.numericColumnData(column)
        
        return self._column_texts[column_data]

    def retranslateUi(self):
        super().retranslateUi()

        self._column_texts = {
            'share_capital':                       self.tr('Share Capital'),
            'capital_reserve_and_treasury_shares': self.tr('Capital Reserve and Treasure Shares'),
            'profit_reserves':                     self.tr('Profit Reserves'),
            'unappropriated_retained_earnings':    self.tr('Unappropriated Retained Earnings'),
            'other_comprehensive_income':          self.tr('Other Comprehensive Income'),
            'controlling_interest':                self.tr('Controlling Interest'),
            'non_controlling_interest':            self.tr('Non-Controlling Interest'),
            'consolidated_equity':                 self.tr('Consolidated Equity'),
        }

        self.headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, self.staticColumnCount(), self.columnCount() - 1)