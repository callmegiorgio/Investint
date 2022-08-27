import typing
from PyQt5     import QtWidgets
from investint import widgets, models
import cvm

class CompanyGeneralInformationWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._cnpj_lbl                       = widgets.DoubleLabel('<b>CNPJ</b>')
        self._cvm_code_lbl                   = widgets.DoubleLabel('<b>Código CVM</b>')
        self._corporate_name_lbl             = widgets.DoubleLabel('<b>Nome Empresarial</b>')
        self._prev_corp_name_lbl             = widgets.DoubleLabel('<b>Nome Empresarial Anterior</b>')
        self._trade_name_lbl                 = widgets.DoubleLabel('<b>Nome Fantasia</b>')
        self._establishment_date_lbl         = widgets.DoubleLabel('<b>Data de Constituição</b>')
        self._industry_lbl                   = widgets.DoubleLabel('<b>Setor de Atividade</b>')
        self._activity_desc_lbl              = widgets.DoubleLabel('<b>Descrição da Atividade</b>')
        self._cvm_registration_date_lbl      = widgets.DoubleLabel('<b>Data de Registro na CVM</b>')
        self._cvm_registration_status_lbl    = widgets.DoubleLabel('<b>Situação do Registro</b>')
        self._cvm_registration_categ_lbl     = widgets.DoubleLabel('<b>Categoria do Registro</b>')
        self._cancelation_date_lbl           = widgets.DoubleLabel('<b>Data de Cancelamento</b>')
        self._cancelation_reason_lbl         = widgets.DoubleLabel('<b>Motivo do Cancelamento</b>')
        self._home_country_lbl               = widgets.DoubleLabel('<b>País de Origem</b>')
        self._securities_custody_country_lbl = widgets.DoubleLabel('<b>País de Custódia dos Valores Mobiliários</b>')
        self._issuer_status_lbl              = widgets.DoubleLabel('<b>Situação do Emissor</b>')
        self._fiscal_year_closing_date       = widgets.DoubleLabel('<b>Data de Encerramento de Exercício</b>')
        self._webpage_lbl                    = widgets.DoubleLabel('<b>Página da Web</b>')

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

    def setCompany(self, co: models.PublicCompany):
        self._cnpj_lbl.setLowerText(str(cvm.datatypes.tax_id.CNPJ(co.cnpj)))
        self._cvm_code_lbl.setLowerText(str(co.cvm_code))

        def labelSince(text, date):
            if date is None:
                return text
            else:
                return text + ' (desde ' + str(date) + ')'

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