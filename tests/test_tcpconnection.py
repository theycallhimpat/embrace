""" unit tests for embrace/tcpconnection.py """
import sys

sys.path.append("..")

import unittest
import time

from embrace import tcpconnection
from embrace.eventhandler import EventType
from embrace.messagehandler import Message

# pylint: disable=missing-docstring,invalid-name,


class TestTCPConnection(unittest.TestCase):
    def test_connect_fail(self) -> None:
        client = tcpconnection.TCPClient("127.0.0.1", 48370)
        with self.assertRaisesRegex(
            AssertionError, "Expected a CONNECT event, but found CONNECT_FAIL"
        ):
            client.connect(timeout=2.5)

    def test_connect_and_exchange(self) -> None:
        server = tcpconnection.TCPServer("127.0.0.1", 48371)
        server.serve()
        time.sleep(0.025)
        server.assert_has_no_event()
        server.assert_disconnected()

        client = tcpconnection.TCPClient("127.0.0.1", 48371)
        client.assert_has_no_events()
        client.assert_disconnected()
        client.connect(timeout=0.1)

        server.assert_event(EventType.CONNECT, timeout=0.1)

        client.assert_connected()
        server.assert_connected()

        client.enqueue_message(Message(b"TEST"))
        server.assert_receive(b"TEST", timeout=0.1)

        client.assert_has_no_events()
        server.assert_has_no_event()

        server.enqueue_message(Message(b"BANG!"))
        client.assert_receive(b"BANG!", timeout=0.1)


if __name__ == "__main__":
    unittest.main()
