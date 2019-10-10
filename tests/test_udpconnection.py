""" unit tests for embrace/udpconnection.py """
import sys
sys.path.append('..')

import unittest

from embrace import udpconnection

# pylint: disable=missing-docstring,invalid-name,

class TestUDPConnection(unittest.TestCase):
    def test_empty(self) -> None:
        u1 = udpconnection.UDPConnection(("127.0.0.1", 30071), ("127.0.0.1", 56664))
        u2 = udpconnection.UDPConnection(("127.0.0.1", 56664), ("127.0.0.1", 30071))

if __name__ == "__main__":
    unittest.main()