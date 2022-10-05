from unittest       import TestCase
from PyQt5.QtCore   import QLocale
from investint.core import BalanceFormatter

class TestBalanceFormatter(TestCase):
    def setUp(self) -> None:
        self.en_us = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)

    def setLocale(self, formatter: BalanceFormatter) -> None:
        formatter.setLocale(self.en_us)

    def testThousand(self) -> None:
        fmt = BalanceFormatter(thousands=1)

        self.setLocale(fmt)
        self.assertEquals(fmt.format(1000,    precision=2), '1.00K')
        self.assertEquals(fmt.format(2000000, precision=2), '2,000.00K')

    def testMillion(self) -> None:
        fmt = BalanceFormatter(thousands=2)

        self.setLocale(fmt)
        self.assertEquals(fmt.format(1000000,    precision=2), '1.00M')
        self.assertEquals(fmt.format(2000000000, precision=2), '2,000.00M')

    def testBillion(self) -> None:
        fmt = BalanceFormatter(thousands=3)

        self.setLocale(fmt)
        self.assertEquals(fmt.format(1000000000, precision=2), '1.00B')
        self.assertEquals(fmt.format(100000000,  precision=2), '0.10B')

    def testSmallest(self) -> None:
        fmt = BalanceFormatter.smallest([1, 2000])

        self.setLocale(fmt)
        self.assertEquals(fmt.format(1),    '1')
        self.assertEquals(fmt.format(2000), '2,000')

    def testGreatest(self) -> None:
        fmt = BalanceFormatter.greatest([1, 2000])

        self.setLocale(fmt)
        self.assertEquals(fmt.format(1),    '0K')
        self.assertEquals(fmt.format(2000), '2K')

    def testBest(self) -> None:
        fmt = BalanceFormatter.best([1, 2000])

        self.setLocale(fmt)
        self.assertEquals(fmt.format(1),    '0K')
        self.assertEquals(fmt.format(2000), '2K')

    def testDynamic(self) -> None:
        fmt = BalanceFormatter()

        self.setLocale(fmt)
        self.assertEquals(fmt.format(1),    '1')
        self.assertEquals(fmt.format(2000), '2K')