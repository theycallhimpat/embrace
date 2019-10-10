""" unit tests for embrace/tcpconnection.py """
import sys
sys.path.append('..')

import unittest

from embrace import tcpconnection

# pylint: disable=missing-docstring,invalid-name,

class TestTCPConnection(unittest.TestCase):
    def test_basic(self) -> None:
        server = tcpconnection.TCPServer("127.0.0.1", 48371)
        client = tcpconnection.TCPClient("127.0.0.1", 48371) 

if __name__ == "__main__":
    unittest.main()
