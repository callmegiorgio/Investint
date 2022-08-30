import sqlalchemy as sa
import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets

class DatabaseClientDialog(widgets.DatabaseConnectionDialog):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self.setWindowTitle('Database Connection')
        self.setFixedSize(300, 300)

        self._dialect_lbl = QtWidgets.QLabel('Dialect')
        self._dialect_combo = QtWidgets.QComboBox()
        self._dialect_combo.addItem('PostgreSQL',           'postgresql')
        self._dialect_combo.addItem('MySQL/MariaDB',        'mysql')
        self._dialect_combo.addItem('Oracle',               'oracle')
        self._dialect_combo.addItem('Microsoft SQL Server', 'mssql')
        self._dialect_combo.currentIndexChanged.connect(self.setDefault)

        self._driver_lbl  = QtWidgets.QLabel('Driver')
        self._driver_edit = QtWidgets.QLineEdit()
        self._driver_edit.textChanged.connect(self._onLineEditTextChanged)

        self._username_lbl  = QtWidgets.QLabel('Username')
        self._username_edit = QtWidgets.QLineEdit()
        self._username_edit.textChanged.connect(self._onLineEditTextChanged)

        self._password_lbl  = QtWidgets.QLabel('Password')
        self._password_edit = QtWidgets.QLineEdit()
        self._password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self._password_edit.textChanged.connect(self._onLineEditTextChanged)

        self._host_lbl  = QtWidgets.QLabel('Host')
        self._host_edit = QtWidgets.QLineEdit()
        self._host_edit.textChanged.connect(self._onLineEditTextChanged)

        self._port_lbl  = QtWidgets.QLabel('Port')
        self._port_spin = QtWidgets.QSpinBox()
        self._port_spin.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self._port_spin.setRange(1024, 65535)

        self._database_lbl  = QtWidgets.QLabel('Database')
        self._database_edit = QtWidgets.QLineEdit('')
        self._database_edit.textChanged.connect(self._onLineEditTextChanged)

        self._confirm_button = QtWidgets.QPushButton('Confirm')
        self._confirm_button.clicked.connect(self.accept)
        self._confirm_button.setMaximumWidth(80)

        self.setDefault()

    def _initLayouts(self):
        dialect_driver_layout = QtWidgets.QGridLayout()
        dialect_driver_layout.addWidget(self._dialect_lbl,   0, 0)
        dialect_driver_layout.addWidget(self._dialect_combo, 1, 0)
        dialect_driver_layout.addWidget(self._driver_lbl,    0, 1)
        dialect_driver_layout.addWidget(self._driver_edit,   1, 1)

        host_port_layout = QtWidgets.QGridLayout()
        host_port_layout.addWidget(self._host_lbl,  0, 0)
        host_port_layout.addWidget(self._host_edit, 1, 0)
        host_port_layout.addWidget(self._port_lbl,  0, 1)
        host_port_layout.addWidget(self._port_spin, 1, 1)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(dialect_driver_layout)
        main_layout.addWidget(self._username_lbl)
        main_layout.addWidget(self._username_edit)
        main_layout.addWidget(self._password_lbl)
        main_layout.addWidget(self._password_edit)
        main_layout.addLayout(host_port_layout)
        main_layout.addWidget(self._database_lbl)
        main_layout.addWidget(self._database_edit)
        main_layout.addWidget(self._confirm_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def setEngine(self, engine: sa.engine.Engine):
        self.setUrl(engine.url)
    
    def setDialect(self, dialect: str):
        index = self._dialect_combo.findData(dialect)

        if index == -1:
            return

        self._dialect_combo.setCurrentIndex(index)

    def setDriver(self, driver: str):
        self._driver_edit.setText(driver)

    def setUsername(self, username: str):
        self._username_edit.setText(username)

    def setPassword(self, password: str):
        self._password_edit.setText(password)

    def setHost(self, host: str):
        self._host_edit.setText(host)

    def setPort(self, port: int):
        self._port_spin.setValue(port)

    def setDatabase(self, database: str):
        self._database_edit.setText(database)

    def setUrl(self, url: sa.engine.URL):
        try:
            dialect, driver = url.drivername.split('+')
        except ValueError:
            dialect = url.drivername
            driver  = ''

        self.setDialect(dialect)
        self.setDriver(driver)
        self.setUsername(url.username or '')
        self.setPassword(url.password or '')
        self.setHost(url.host or '')
        self.setPort(url.port or 0)
        self.setDatabase(url.database or '')

    def dialect(self) -> str:
        return self._dialect_combo.currentData()

    def driver(self) -> str:
        return self._driver_edit.text()

    def username(self) -> str:
        return self._username_edit.text()

    def password(self) -> str:
        return self._password_edit.text()

    def host(self) -> str:
        return self._host_edit.text()

    def port(self) -> int:
        return self._port_spin.value()

    def database(self) -> str:
        return self._database_edit.text()

    def url(self) -> sa.engine.URL:
        return sa.engine.URL.create(
            drivername = f'{self.dialect()}+{self.driver()}',
            username   = self.username(),
            password   = self.password(),
            host       = self.host(),
            port       = self.port(),
            database   = self.database()
        )
    
    def setDefault(self):
        current_dialect = self._dialect_combo.currentData()

        default_driver = ''
        default_port   = 0

        if current_dialect == 'postgresql':
            default_driver = 'psycopg2'
            default_port   = 5432

        elif current_dialect == 'mysql':
            default_driver = 'mysqldb'
            default_port   = 3306

        elif current_dialect == 'oracle':
            default_driver = 'cx_oracle'
            default_port   = 1521

        elif current_dialect == 'mssql':
            default_driver = 'pyodbc'
            default_port   = 1433

        else:
            return

        self.setDriver(default_driver)
        self.setHost('localhost')
        self.setPort(default_port)

    @QtCore.pyqtSlot()
    def _onLineEditTextChanged(self):
        string_methods = (
            self.driver,
            self.username,
            self.password,
            self.host,
            self.database
        )
        
        enabled = all(method() != '' for method in string_methods)

        self._confirm_button.setEnabled(enabled)