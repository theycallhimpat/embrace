""" unit tests for embrace/udpconnection.py """
import sys
import time

sys.path.append("..")

import unittest

from embrace import udpconnection
from embrace.messagehandler import Message

# pylint: disable=missing-docstring,invalid-name,


class TestUDPConnection(unittest.TestCase):
    def test_exchange(self) -> None:
        u1 = udpconnection.UDPConnection(("127.0.0.1", 30071), ("127.0.0.1", 56664))
        u1.start()
        u2 = udpconnection.UDPConnection(("127.0.0.1", 56664), ("127.0.0.1", 30071))
        u2.start()

        u1.assert_has_no_event()
        u2.assert_has_no_event()

        u1.enqueue_message(Message(b"TEST"))
        u2.assert_receive(b"TEST", timeout=0.1)
        u1.assert_has_no_event()
        u2.assert_has_no_event()

        u2.enqueue_message(Message(b"REPLY"))
        u1.assert_receive(b"REPLY", timeout=0.1)
        u1.assert_has_no_event()
        u2.assert_has_no_event()


if __name__ == "__main__":
    unittest.main()
