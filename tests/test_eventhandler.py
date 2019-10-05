import unittest

from .context import embrace
from embrace import eventhandler


class DummyTestSuite(unittest.TestCase):
    def test_dummy(self):
        assert eventhandler.dummy(2, 3) == 5


if __name__ == "__main__":
    unittest.main()
