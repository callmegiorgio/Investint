import cvm
from PyQt5 import QtCore

__all__ = [
    'industryToString'
]

Industry  = cvm.datatypes.Industry
translate = QtCore.QCoreApplication.translate

def industryToString(industry: cvm.datatypes.Industry) -> str:
    if industry == Industry.MISCELLANEOUS_SERVICES:
        return translate('cvm.Industry', 'Miscellaneous Services')
        
    if industry == Industry.EAP:
        return translate('cvm.Industry', 'Ent. Adm. Participation')
        
    if industry == Industry.OTHER_INDUSTRIAL_ACTIVITIES:
        return translate('cvm.Industry', 'Other Industrial Activities')
        
    if industry == Industry.GENERAL_SERVICES:
        return translate('cvm.Industry', 'General Services')

    # FIXME: do ch
    if industry >= Industry.EAP_OIL_AND_GAS and industry <= Industry.EAP_NO_CORE_BUSINESS:
        eap_prefix = translate('cvm.Industry', 'Ent. Adm. Part.') + ' - '

        if industry == Industry.EAP_NO_CORE_BUSINESS:
            return eap_prefix + translate('cvm.Industry', 'No Core Business')
        else:
            industry_code = industry.value - 2000
    else:
        industry_code = industry.value
        eap_prefix    = ''

    if industry_code == Industry.OIL_AND_GAS.value:
        return eap_prefix + translate('cvm.Industry', 'Oil and Gas')

    if industry_code == Industry.PETROCHEMICAL_AND_RUBBER.value:
        return eap_prefix + translate('cvm.Industry', 'Petrochemical and Rubber')

    if industry_code == Industry.MINERAL_EXTRACTION.value:
        return eap_prefix + translate('cvm.Industry', 'Mineral Extraction')
            
    if industry_code == Industry.PULP_AND_PAPER.value:
        return eap_prefix + translate('cvm.Industry', 'Pulp and Paper')

    if industry_code == Industry.TEXTILE_AND_CLOTHING.value:
        return eap_prefix + translate('cvm.Industry', 'Textile and Clothing')

    if industry_code == Industry.METALLURGY_AND_STEELMAKING.value:
        return eap_prefix + translate('cvm.Industry', 'Metallurgy and Steelmaking')
        
    if industry_code == Industry.MACHINERY_EQUIPMENT_VEHICLE_AND_PARTS.value:
        return eap_prefix + translate('cvm.Industry', 'Machinery, Equipment, Vehicle, and Parts')

    if industry_code == Industry.PHARMACEUTICAL_AND_HYGIENE.value:
        return eap_prefix + translate('cvm.Industry', 'Pharmaceutical and Hygiene')

    if industry_code == Industry.BEVERAGES_AND_TOBACCO.value:
        return eap_prefix + translate('cvm.Industry', 'Beverages and Tobacco')

    if industry_code == Industry.PRINTERS_AND_PUBLISHERS.value:
        return eap_prefix + translate('cvm.Industry', 'Printers and Publishers')

    if industry_code == Industry.CIVIL_CONSTRUCTION_BUILDING_AND_DECORATION_MATERIALS.value:
        return eap_prefix + translate('cvm.Industry', 'Civil Construction, Building Materials, and Decoration')

    if industry_code == Industry.ELETRICITY.value:
        return eap_prefix + translate('cvm.Industry', 'Eletricity')

    if industry_code == Industry.TELECOMMUNICATIONS.value:
        return eap_prefix + translate('cvm.Industry', 'Telecommunications')

    if industry_code == Industry.TRANSPORT_AND_LOGISTICS_SERVICES.value:
        return eap_prefix + translate('cvm.Industry', 'Transport and Logistics Services')

    if industry_code == Industry.COMMUNICATION_AND_INFORMATION_TECHNOLOGY.value:
        return eap_prefix + translate('cvm.Industry', 'Communication and Information Technology')

    if industry_code == Industry.SANITATION_WATER_AND_GAS_SERVICES.value:
        return eap_prefix + translate('cvm.Industry', 'Sanitation, Water, and Gas Services')

    if industry_code == Industry.MEDICAL_SERVICES.value:
        return eap_prefix + translate('cvm.Industry', 'Medical Services')

    if industry_code == Industry.HOSTING_AND_TOURISM.value:
        return eap_prefix + translate('cvm.Industry', 'Hosting and Tourism')

    if industry_code == Industry.WHOLESAIL_AND_RETAIL_COMMERCE.value:
        return eap_prefix + translate('cvm.Industry', 'Wholesail and Retail Commerce')

    if industry_code == Industry.FOREIGN_COMMERCE.value:
        return eap_prefix + translate('cvm.Industry', 'Foreign Commerce')

    if industry_code == Industry.AGRICULTURE.value:
        return eap_prefix + translate('cvm.Industry', 'Agriculture')

    if industry_code == Industry.FOOD.value:
        return eap_prefix + translate('cvm.Industry', 'Food')

    if industry_code == Industry.COOPERATIVES.value:
        return eap_prefix + translate('cvm.Industry', 'Cooperatives')

    if industry_code == Industry.BANKS.value:
        return eap_prefix + translate('cvm.Industry', 'Banks')

    if industry_code == Industry.INSURANCE_AND_BROKERAGE_COMPANIES.value:
        return eap_prefix + translate('cvm.Industry', 'Insurance and Brokerage Companies')

    if industry_code == Industry.LEASING.value:
        return eap_prefix + translate('cvm.Industry', 'Leasing')

    if industry_code == Industry.PRIVATE_PENSION.value:
        return eap_prefix + translate('cvm.Industry', 'Private Pension')

    if industry_code == Industry.FINANCIAL_INTERMEDIATION.value:
        return eap_prefix + translate('cvm.Industry', 'Financial Intermediation')

    if industry_code == Industry.FACTORING.value:
        return eap_prefix + translate('cvm.Industry', 'Factoring')

    if industry_code == Industry.REAL_ESTATE_CREDIT.value:
        return eap_prefix + translate('cvm.Industry', 'Real Estate Credit')

    if industry_code == Industry.REFORESTATION.value:
        return eap_prefix + translate('cvm.Industry', 'Reforestation')

    if industry_code == Industry.FISHING.value:
        return eap_prefix + translate('cvm.Industry', 'Fishing')

    if industry_code == Industry.PACKAGING.value:
        return eap_prefix + translate('cvm.Industry', 'Packaging')

    if industry_code == Industry.EDUCATION.value:
        return eap_prefix + translate('cvm.Industry', 'Education')

    if industry_code == Industry.SECURITIZATION_OF_RECEIVABLES.value:
        return eap_prefix + translate('cvm.Industry', 'Securitization of Receivables')

    if industry_code == Industry.TOYS_AND_RECREATIONAL.value:
        return eap_prefix + translate('cvm.Industry', 'Toys and Recreational')

    if industry_code == Industry.STOCK_EXCHANGES.value:
        return eap_prefix + translate('cvm.Industry', 'Stock Exchanges')
    
    return ''