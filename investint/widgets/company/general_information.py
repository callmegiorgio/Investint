import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets, models
import cvm

class CompanyGeneralInformationWidget(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
        self.retranslateUi()

    def _initWidgets(self):
        self._cnpj_lbl                       = widgets.DoubleLabel()
        self._cvm_code_lbl                   = widgets.DoubleLabel()
        self._corporate_name_lbl             = widgets.DoubleLabel()
        self._prev_corp_name_lbl             = widgets.DoubleLabel()
        self._trade_name_lbl                 = widgets.DoubleLabel()
        self._establishment_date_lbl         = widgets.DoubleLabel()
        self._industry_lbl                   = widgets.DoubleLabel()
        self._activity_desc_lbl              = widgets.DoubleLabel()
        self._cvm_registration_date_lbl      = widgets.DoubleLabel()
        self._cvm_registration_status_lbl    = widgets.DoubleLabel()
        self._cvm_registration_categ_lbl     = widgets.DoubleLabel()
        self._cancelation_date_lbl           = widgets.DoubleLabel()
        self._cancelation_reason_lbl         = widgets.DoubleLabel()
        self._home_country_lbl               = widgets.DoubleLabel()
        self._securities_custody_country_lbl = widgets.DoubleLabel()
        self._issuer_status_lbl              = widgets.DoubleLabel()
        self._fiscal_year_closing_date       = widgets.DoubleLabel()
        self._webpage_lbl                    = widgets.DoubleLabel()

    def _initLayouts(self):
        main_layout = QtWidgets.QGridLayout()
        main_layout.addWidget(self._cnpj_lbl,                       0, 0)
        main_layout.addWidget(self._cvm_code_lbl,                   0, 1)
        main_layout.addWidget(self._corporate_name_lbl,             1, 0)
        main_layout.addWidget(self._prev_corp_name_lbl,             1, 1)
        main_layout.addWidget(self._trade_name_lbl,                 1, 2)
        main_layout.addWidget(self._industry_lbl,                   2, 0)
        main_layout.addWidget(self._activity_desc_lbl,              2, 1)
        main_layout.addWidget(self._cvm_registration_date_lbl,      3, 0)
        main_layout.addWidget(self._cvm_registration_status_lbl,    3, 1)
        main_layout.addWidget(self._cvm_registration_categ_lbl,     3, 2)
        main_layout.addWidget(self._cancelation_date_lbl,           4, 0)
        main_layout.addWidget(self._cancelation_reason_lbl,         4, 1)
        main_layout.addWidget(self._home_country_lbl,               5, 0)
        main_layout.addWidget(self._securities_custody_country_lbl, 5, 1)
        main_layout.addWidget(self._establishment_date_lbl,         6, 0)
        main_layout.addWidget(self._issuer_status_lbl,              7, 0)
        main_layout.addWidget(self._fiscal_year_closing_date,       8, 0)
        main_layout.addWidget(self._webpage_lbl,                    9, 0)

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setCompany(self, co: models.PublicCompany):
        self._cnpj_lbl.setLowerText(cvm.datatypes.CNPJ(co.cnpj).to_string())
        self._cvm_code_lbl.setLowerText(co.cvm_code)

        def labelSince(text, date):
            if date is None:
                return text
            else:
                return text + self.tr(' (since {})').format(date)

        self._corporate_name_lbl.setLowerText(labelSince(co.corporate_name, co.corporate_name_date))
        self._prev_corp_name_lbl.setLowerText(co.prev_corporate_name or '')
        self._trade_name_lbl.setLowerText(co.trade_name or '')

        self._establishment_date_lbl.setLowerText(str(co.establishment_date))

        self._industry_lbl.setLowerText(co.industry.description)
        self._activity_desc_lbl.setLowerText(co.activity_description)

        self._cvm_registration_date_lbl.setLowerText(str(co.registration_date))
        self._cvm_registration_status_lbl.setLowerText(labelSince(co.registration_status.description, co.registration_status_date))
        self._cvm_registration_categ_lbl.setLowerText(labelSince(co.registration_category.description, co.registration_category_date))

        self._cancelation_date_lbl.setLowerText(str(co.cancelation_date))
        self._cancelation_reason_lbl.setLowerText(co.cancelation_reason)

        self._home_country_lbl.setLowerText(co.home_country.description)
        self._securities_custody_country_lbl.setLowerText(co.securities_custody_country.description)

        self._issuer_status_lbl.setLowerText(labelSince(co.issuer_status.description, co.issuer_status_date))
        self._fiscal_year_closing_date.setLowerText(labelSince(f'{co.fiscal_year_closing_day}/{co.fiscal_year_closing_month}', co.fiscal_year_change_date))
        self._webpage_lbl.setLowerText(co.webpage)

    def retranslateUi(self):
        def bold(text: str):
            return f'<b>{text}</b>'

        self._cnpj_lbl.                      setUpperText(bold(self.tr('CNPJ')))
        self._cvm_code_lbl.                  setUpperText(bold(self.tr('CVM code')))
        self._corporate_name_lbl.            setUpperText(bold(self.tr('Corporate Name')))
        self._prev_corp_name_lbl.            setUpperText(bold(self.tr('Previous Corporate Name')))
        self._trade_name_lbl.                setUpperText(bold(self.tr('Trade Name')))
        self._establishment_date_lbl.        setUpperText(bold(self.tr('Establishment Date')))
        self._industry_lbl.                  setUpperText(bold(self.tr('Industry')))
        self._activity_desc_lbl.             setUpperText(bold(self.tr('Activity Description')))
        self._cvm_registration_date_lbl.     setUpperText(bold(self.tr('Registration Date')))
        self._cvm_registration_status_lbl.   setUpperText(bold(self.tr('Registration Status')))
        self._cvm_registration_categ_lbl.    setUpperText(bold(self.tr('Registration Category')))
        self._cancelation_date_lbl.          setUpperText(bold(self.tr('Cancelation Date')))
        self._cancelation_reason_lbl.        setUpperText(bold(self.tr('Cancelation Reason')))
        self._home_country_lbl.              setUpperText(bold(self.tr('Home Country')))
        self._securities_custody_country_lbl.setUpperText(bold(self.tr('Securities Custody Country')))
        self._issuer_status_lbl.             setUpperText(bold(self.tr('Issuer Status')))
        self._fiscal_year_closing_date.      setUpperText(bold(self.tr('Fiscal Year Closing Date')))
        self._webpage_lbl.                   setUpperText(bold(self.tr('Webpage')))

        # self._cnpj_lbl.                      setUpperText(bold(self.tr('CNPJ')))
        # self._cvm_code_lbl.                  setUpperText(bold(self.tr('Código CVM')))
        # self._corporate_name_lbl.            setUpperText(bold(self.tr('Nome Empresarial')))
        # self._prev_corp_name_lbl.            setUpperText(bold(self.tr('Nome Empresarial Anterior')))
        # self._trade_name_lbl.                setUpperText(bold(self.tr('Nome Fantasia')))
        # self._establishment_date_lbl.        setUpperText(bold(self.tr('Data de Constituição')))
        # self._industry_lbl.                  setUpperText(bold(self.tr('Setor de Atividade')))
        # self._activity_desc_lbl.             setUpperText(bold(self.tr('Descrição da Atividade')))
        # self._cvm_registration_date_lbl.     setUpperText(bold(self.tr('Data de Registro na CVM')))
        # self._cvm_registration_status_lbl.   setUpperText(bold(self.tr('Situação do Registro')))
        # self._cvm_registration_categ_lbl.    setUpperText(bold(self.tr('Categoria do Registro')))
        # self._cancelation_date_lbl.          setUpperText(bold(self.tr('Data de Cancelamento')))
        # self._cancelation_reason_lbl.        setUpperText(bold(self.tr('Motivo do Cancelamento')))
        # self._home_country_lbl.              setUpperText(bold(self.tr('País de Origem')))
        # self._securities_custody_country_lbl.setUpperText(bold(self.tr('País de Custódia dos Valores Mobiliários')))
        # self._issuer_status_lbl.             setUpperText(bold(self.tr('Situação do Emissor')))
        # self._fiscal_year_closing_date.      setUpperText(bold(self.tr('Data de Encerramento de Exercício')))
        # self._webpage_lbl.                   setUpperText(bold(self.tr('Página da Web')))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()
        
        super().changeEvent(event)