import cvm
import datetime
import typing
from PyQt5     import QtCore, QtWidgets
from investint import models, widgets

__all__ = [
    'CompanyDMPLWidget'
]

class CompanyDMPLWidget(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self) -> None:
        self._tabs = QtWidgets.QTabWidget()

    def _initLayouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._tabs)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def select(self,
               company_id: int,
               reference_date: datetime.date,
               document_type: cvm.DocumentType,
               balance_type: cvm.BalanceType
    ) -> None:
        self._tabs.clear()

        document = models.Document.find(company_id, document_type, reference_date)

        if document is None:
            return

        dmpls = models.Statement.find(document.id, cvm.StatementType.DMPL, balance_type)
        dmpls: typing.List[models.Statement] = sorted(dmpls, key=lambda dmpl: dmpl.period_end_date, reverse=True)

        for dmpl in dmpls:
            model = models.DMPLAccountTreeModel()
            model.select(dmpl)

            account_tree = widgets.AccountTreeWidget()
            account_tree.setModel(model)

            if dmpl.period_start_date is not None:
                tab_name = f'{dmpl.period_start_date} - {dmpl.period_end_date}'
            else:
                tab_name = str(dmpl.period_end_date)

            self._tabs.addTab(account_tree, tab_name)

    def retranslateUi(self):
        for i in range(self._tabs.count()):
            model: models.DMPLAccountTreeModel = self._tabs.widget(i).model()
            model.retranslateUi()

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()
        
        super().changeEvent(event)