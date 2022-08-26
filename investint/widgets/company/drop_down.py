import cvm
import typing
from PyQt5     import QtCore, QtGui, QtWidgets
from investint import models

class CompanyDropDown(QtWidgets.QWidget):
    companyChanged = QtCore.pyqtSignal(models.PublicCompany)

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

        self._current_model_index = QtCore.QModelIndex()

    def _initWidgets(self):
        self._model = QtGui.QStandardItemModel()

        self._completer = QtWidgets.QCompleter(self._model, self)
        self._completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._completer.activated[QtCore.QModelIndex].connect(self._onCompleterIndexActivated)

        self._edit = QtWidgets.QLineEdit()
        self._edit.setPlaceholderText('Name or CVM code...')
        self._edit.setCompleter(self._completer)
        self._edit.textEdited.connect(self._onTextEdited)
        self.setFocusProxy(self._edit)

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._edit)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    def currentCompany(self) -> typing.Optional[models.PublicCompany]:
        # It seems it is not possible to use `self._completer.currentIndex()`,
        # because it returns an index of a proxy model that has a broken
        # implementation of `QAbstractProxyModel.mapToSource()`. There's
        # no way to map it to the source model, so we can't know what
        # current index is actually selected.
        #
        # Fortunatelly, for some reason, the mapping works when handling
        # the signal `QCompleter.activated`, so we can use that to store
        # the source model index. See `_onCompleterIndexActivated()`.
        return self._current_model_index.data(QtCore.Qt.ItemDataRole.UserRole + 1)

    @QtCore.pyqtSlot(str)
    def _onTextEdited(self, text: str):
        self._model.clear()

        # if len(text) < 3:
        #     return
        
        for company in models.PublicCompany.findByExpression(text):
            name = company.corporate_name
            cnpj = cvm.datatypes.CNPJ(company.cnpj)
            item = QtGui.QStandardItem(f'{name} ({cnpj})')
            item.setData(company, QtCore.Qt.ItemDataRole.UserRole + 1)

            self._model.appendRow(item)
    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def _onCompleterIndexActivated(self, proxy_index: QtCore.QModelIndex):
        # https://stackoverflow.com/questions/39294136/why-does-my-qstandarditemmodel-itemfromindex-method-return-none-index-invalid
        source_index = proxy_index.model().mapToSource(proxy_index)
        company      = source_index.data(QtCore.Qt.ItemDataRole.UserRole + 1)

        self._current_model_index = source_index
        
        if company is None:
            return
        
        self.companyChanged.emit(company)