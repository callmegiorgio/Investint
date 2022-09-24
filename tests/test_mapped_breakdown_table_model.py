import dataclasses
import unittest
from investint.models import MappedBreakdownTableModel

@dataclasses.dataclass
class A:
    i: int
    b: bool
    f: float

class TestMappedBreakdownTableModel(unittest.TestCase):
    def testRowName(self):
        model = MappedBreakdownTableModel({
            'i': 'Int',
            'b': 'Bool',
            'f': 'Float'
        })

        a = A(i=10, b=True, f=3.14)

        model.append(None, dataclasses.asdict(a))
        
        self.assertEqual(model.rowName(0), 'Int')
        self.assertEqual(model.rowName(1), 'Bool')
        self.assertEqual(model.rowName(2), 'Float')