import unittest
from PyQt5            import QtCore
from investint.models import BreakdownTableModel

class TestBreakdownTableModel(unittest.TestCase):
    def testRowCount(self):
        model = BreakdownTableModel(['a', 'b', 'c'])

        self.assertEqual(model.rowCount(), 3)

    def testVerticalHeaderData(self):
        model = BreakdownTableModel(['a', 'b', 'c'])

        Vertical = QtCore.Qt.Orientation.Vertical
        
        self.assertEqual(model.headerData(0, Vertical), 'a')
        self.assertEqual(model.headerData(1, Vertical), 'b')
        self.assertEqual(model.headerData(2, Vertical), 'c')

    def testRowName(self):
        model = BreakdownTableModel(['a', 'b', 'c'])

        self.assertEqual(model.rowName(0), 'a')
        self.assertEqual(model.rowName(1), 'b')
        self.assertEqual(model.rowName(2), 'c')

    def testRowFromName(self):
        model = BreakdownTableModel(['a', 'b', 'c'])

        self.assertEqual(model.rowFromName('a'), 0)
        self.assertEqual(model.rowFromName('b'), 1)
        self.assertEqual(model.rowFromName('c'), 2)
    
    def testHorizontalHeaderData(self):
        model = BreakdownTableModel(['a', 'b', 'c'])
        model.append(2010, {})
        model.append(2011, {})

        Horizontal = QtCore.Qt.Orientation.Horizontal

        self.assertEqual(model.headerData(0, Horizontal), '2010')
        self.assertEqual(model.headerData(1, Horizontal), '2011')

    def testColumnName(self):
        model = BreakdownTableModel(['a', 'b', 'c'])
        model.append(2010, {})
        model.append(2011, {})

        self.assertEqual(model.columnName(0), '2010')
        self.assertEqual(model.columnName(1), '2011')

    def testColumnData(self):
        model = BreakdownTableModel(['a', 'b', 'c'])
        model.append(2010, {})
        model.append(2011, {})
        
        self.assertEqual(model.columnData(0), 2010)
        self.assertEqual(model.columnData(1), 2011)

    def testColumnFromData(self):
        model = BreakdownTableModel(['a', 'b', 'c'])
        model.append(2010, {})
        model.append(2011, {})
        
        self.assertEqual(model.columnFromData(2010), 0)
        self.assertEqual(model.columnFromData(2011), 1)

    def testNumber(self):
        model = BreakdownTableModel(['a', 'b', 'c'])
        model.append(2010, {'c': 30, 'b': 20, 'a': 10})
        model.append(2011, {'b': 50, 'a': 40, 'c': 60})

        self.assertEqual(model.number('a', 0), 10)
        self.assertEqual(model.number('b', 0), 20)
        self.assertEqual(model.number('c', 0), 30)

        self.assertEqual(model.number('a', 1), 40)
        self.assertEqual(model.number('b', 1), 50)
        self.assertEqual(model.number('c', 1), 60)

    def testHorizontalAnalysis(self):
        model = BreakdownTableModel(['a', 'b', 'c'])
        model.setHorizontalAnalysisEnabled(True)
        model.append(2010, {'c': 30, 'b': 20, 'a': 10})
        model.append(2011, {'b': 50, 'a': 40, 'c': 60})
        
        self.assertEqual(model.number('a', 0), 10)
        self.assertEqual(model.number('a', 1), 3)
        self.assertEqual(model.number('a', 2), 40)

        self.assertEqual(model.number('b', 0), 20)
        self.assertEqual(model.number('b', 1), 1.5)
        self.assertEqual(model.number('b', 2), 50)

        self.assertEqual(model.number('c', 0), 30)
        self.assertEqual(model.number('c', 1), 1)
        self.assertEqual(model.number('c', 2), 60)
    
    def testHorizontalAnalysisData(self):
        model = BreakdownTableModel(['a', 'b', 'c'])
        model.setHorizontalAnalysisEnabled(True)
        model.append(2010, {'c': 30, 'b': 20, 'a': 10})
        model.append(2011, {'b': 50, 'a': 40, 'c': 60})
        
        self.assertEqual(model.data(model.index(model.rowFromName('a'), 1)), '300.00%')
        self.assertEqual(model.data(model.index(model.rowFromName('b'), 1)), '150.00%')
        self.assertEqual(model.data(model.index(model.rowFromName('c'), 1)), '100.00%')