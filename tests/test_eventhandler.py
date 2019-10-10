""" unit tests for embrace/eventhandler.py """
import sys
sys.path.append('..')

import unittest
import threading

from embrace import eventhandler

# pylint: disable=missing-docstring,invalid-name,


class TestEvent(unittest.TestCase):
    def test_init(self) -> None:
        event = eventhandler.Event(event_id=4)
        self.assertEqual(4, event.event_id)


class TestEventHandler(unittest.TestCase):
    def test_empty(self) -> None:
        handler = eventhandler.EventHandler()
        self.assertFalse(handler.has_event())

    def test_add_event(self) -> None:
        handler = eventhandler.EventHandler()
        event = eventhandler.Event(1)
        handler.add_event(event)
        self.assertTrue(handler.has_event())

    def test_wait_for_next_event(self) -> None:
        handler = eventhandler.EventHandler()
        handler.add_event(eventhandler.Event(1))
        event = handler.wait_for_next_event(timeout=0.005)
        self.assertEqual(1, event.event_id)

        with self.assertRaisesRegex(
            eventhandler.TimeoutException,
            "Timed out after 0.005 seconds waiting for next event",
        ):
            handler.wait_for_next_event(timeout=0.005)

    def test_wait_for_next_event_from_thread(self) -> None:
        handler = eventhandler.EventHandler()
        threading.Thread(target=handler.add_event_threadsafe, args=(eventhandler.Event(5),)).start()
        event = handler.wait_for_next_event(timeout=0.025)
        self.assertEqual(5, event.event_id)

if __name__ == "__main__":
    unittest.main()
