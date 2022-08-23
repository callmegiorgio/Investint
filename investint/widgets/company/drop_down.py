import cvm
import typing
from PyQt5     import QtCore, QtGui, QtWidgets
from investint import models

class CompanyDropDown(QtWidgets.QWidget):
    companyChanged = QtCore.pyqtSignal(cvm.datatypes.CNPJ)

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._model = QtGui.QStandardItemModel()
        
        completer = QtWidgets.QCompleter(self._model, self)
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.activated[QtCore.QModelIndex].connect(self._onCompleterIndexActivated)

        self._edit = QtWidgets.QLineEdit()
        self._edit.setPlaceholderText('Name or CVM code...')
        self._edit.setCompleter(completer)
        self._edit.textEdited.connect(self._onTextEdited)
        self.setFocusProxy(self._edit)

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._edit)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    def currentCompany(self) -> typing.Optional[cvm.datatypes.CNPJ]:
        index = self._edit.completer().currentIndex()
        return index.data(QtCore.Qt.ItemDataRole.UserRole + 1)

    @QtCore.pyqtSlot(str)
    def _onTextEdited(self, text: str):
        self._model.clear()

        # if len(text) < 3:
        #     return
        
        for cnpj, name in models.PublicCompany.findInfoByExpression(text):
            cnpj = cvm.datatypes.CNPJ(cnpj)
            item = QtGui.QStandardItem(f'{name} ({cnpj})')
            item.setData(cnpj, QtCore.Qt.ItemDataRole.UserRole + 1)

            self._model.appendRow(item)
    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def _onCompleterIndexActivated(self, index: QtCore.QModelIndex):
        # https://stackoverflow.com/questions/39294136/why-does-my-qstandarditemmodel-itemfromindex-method-return-none-index-invalid
        proxy_model: QtCore.QAbstractProxyModel = index.model()

        source_index = proxy_model.mapToSource(index)
        cnpj         = source_index.data(QtCore.Qt.ItemDataRole.UserRole + 1)
        
        if cnpj is None:
            return

        print('cnpj (str):', repr(cnpj))
        print('cnpj (int):', int(cnpj))
        
        self.companyChanged.emit(cnpj)