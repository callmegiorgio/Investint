import cvm
from PyQt5 import QtCore

__all__ = [
    'issuerStatusToString'
]

IssuerStatus = cvm.datatypes.IssuerStatus
translate    = QtCore.QCoreApplication.translate

def issuerStatusToString(issuer_status: IssuerStatus) -> str:
    if issuer_status == IssuerStatus.PRE_OPERATIONAL_PHASE:
        return translate('cvm.IssuerStatus', 'Pre-Operational Phase')

    if issuer_status == IssuerStatus.OPERATIONAL_PHASE:
        return translate('cvm.IssuerStatus', 'Operational Phase')

    if issuer_status == IssuerStatus.JUDICIAL_RECOVERY_OR_EQUIVALENT:
        return translate('cvm.IssuerStatus', 'Judicial Recovery or Equivalent')

    if issuer_status == IssuerStatus.EXTRAJUDICIAL_RECOVERY:
        return translate('cvm.IssuerStatus', 'Extrajudicial Recovery')

    if issuer_status == IssuerStatus.BANKRUPT:
        return translate('cvm.IssuerStatus', 'Bankrupt')

    if issuer_status == IssuerStatus.EXTRAJUDICIAL_LIQUIDATION:
        return translate('cvm.IssuerStatus', 'Extrajudicial Liquidation')

    if issuer_status == IssuerStatus.JUDICIAL_LIQUIDATION:
        return translate('cvm.IssuerStatus', 'Judicial Liquidation')

    if issuer_status == IssuerStatus.STALLED:
        return translate('cvm.IssuerStatus', 'Stalled')
    
    return ''