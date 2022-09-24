import cvm
from PyQt5 import QtCore

__all__ = [
    'registrationCategoryToString',
    'registrationStatusToString',
]

RegistrationCategory = cvm.datatypes.RegistrationCategory
RegistrationStatus   = cvm.datatypes.RegistrationStatus
translate            = QtCore.QCoreApplication.translate

def registrationCategoryToString(registration_category: RegistrationCategory) -> str:
    if registration_category == RegistrationCategory.A:
        return translate('cvm.RegistrationCategory', 'Category A')
    
    if registration_category == RegistrationCategory.B:
        return translate('cvm.RegistrationCategory', 'Category B')

    if registration_category == RegistrationCategory.UNKNOWN:
        return translate('cvm.RegistrationCategory', 'Unknown')

    return ''

def registrationStatusToString(registration_status: RegistrationStatus) -> str:
    if registration_status == RegistrationStatus.ACTIVE:
        return translate('cvm.RegistrationStatus', 'Active')
    
    if registration_status == RegistrationStatus.UNDER_ANALYSIS:
        return translate('cvm.RegistrationStatus', 'Under analysis')
    
    if registration_status == RegistrationStatus.NOT_GRANTED:
        return translate('cvm.RegistrationStatus', 'Not granted')
    
    if registration_status == RegistrationStatus.SUSPENDED:
        return translate('cvm.RegistrationStatus', 'Suspended')
    
    if registration_status == RegistrationStatus.CANCELED:
        return translate('cvm.RegistrationStatus', 'Canceled')

    return ''