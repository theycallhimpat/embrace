""" unit tests for embrace/eventhandler.py """
import sys

sys.path.append("..")

import unittest
import threading

from embrace.eventhandler import AsyncEventHandler
from embrace.eventhandler import (
    Event,
    EventType,
    ConnectionEvent,
    DisconnectionEvent,
    ConnectionFailedEvent,
    ReceiveEvent,
)
from embrace.eventhandler import TimeoutException

# pylint: disable=missing-docstring,invalid-name,


class TestEvent(unittest.TestCase):
    def test_init(self) -> None:
        event = Event(event_id=EventType.CONNECT)
        self.assertEqual(EventType.CONNECT, event.event_id)


class TestAsyncEventHandler(unittest.TestCase):
    def test_empty(self) -> None:
        handler = AsyncEventHandler()
        self.assertFalse(handler.has_event())
        self.assertEqual(0, handler.num_queued_events())

    def test_add_event_unsafe(self) -> None:
        handler = AsyncEventHandler()
        event = ConnectionEvent()
        handler.add_event_unsafe(event)
        self.assertTrue(handler.has_event())
        self.assertEqual(1, handler.num_queued_events())

    def test_wait_for_next_event(self) -> None:
        handler = AsyncEventHandler()
        handler.add_event_unsafe(ConnectionEvent())
        event = handler.wait_for_next_event(timeout=0.005)
        self.assertEqual(1, event.event_id)
        self.assertEqual(0, handler.num_queued_events())
        self.assertFalse(handler.has_event())

        with self.assertRaisesRegex(
            TimeoutException, "Timed out after 0.005 seconds waiting for next event"
        ):
            handler.wait_for_next_event(timeout=0.005)

    def test_wait_for_next_event_from_thread(self) -> None:
        handler = AsyncEventHandler()
        threading.Thread(
            target=handler.add_event_threadsafe, args=(ReceiveEvent(b"a"),)
        ).start()
        event = handler.wait_for_next_event(timeout=0.025)
        assert isinstance(event, ReceiveEvent)
        self.assertEqual(EventType.RECEIVE, event.event_id)
        self.assertEqual(b"a", event.data)

        self.assertEqual(0, handler.num_queued_events())
        self.assertFalse(handler.has_event())

        threading.Thread(
            target=handler.add_event_threadsafe, args=(ReceiveEvent(b"123"),)
        ).start()
        handler.assert_receive(b"123", timeout=0.025)

        self.assertEqual(0, handler.num_queued_events())
        self.assertFalse(handler.has_event())


if __name__ == "__main__":
    unittest.main()
