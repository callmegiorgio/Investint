import typing
from PyQt5     import QtCore, QtGui, QtWidgets
from investint import models

class CompanyDropDown(QtWidgets.QWidget):
    companySelected = QtCore.pyqtSignal(int)

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

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

    @QtCore.pyqtSlot(str)
    def _onTextEdited(self, text: str):
        self._model.clear()

        # if len(text) < 3:
        #     return
        
        for cnpj, name in models.PublicCompany.findInfoByExpression(text):
            item = QtGui.QStandardItem(name)
            item.setData(cnpj)

            self._model.appendRow(item)
    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def _onCompleterIndexActivated(self, index: QtCore.QModelIndex):
        # https://stackoverflow.com/questions/39294136/why-does-my-qstandarditemmodel-itemfromindex-method-return-none-index-invalid
        proxy: QtCore.QAbstractProxyModel = index.model()

        source_index = proxy.mapToSource(index)

        item = self._model.itemFromIndex(source_index)
        
        if item is None:
            return
        
        cnpj = item.data()

        self.companySelected.emit(cnpj)