import unittest

from .context import embrace
from embrace import eventhandler


class DummyTestSuite(unittest.TestCase):
    def test_dummy(self) -> None:
        assert eventhandler.dummy(2, 3) == 5


class TestEvent(unittest.TestCase):
    def test_empty(self) -> None:
        event = eventhandler.Event()


class TestEventHandler(unittest.TestCase):
    def test_empty(self) -> None:
        handler = eventhandler.EventHandler()
        self.assertFalse(handler.has_event())

    def test_add_event(self) -> None:
        handler = eventhandler.EventHandler()
        event = eventhandler.Event()
        handler.add_event(event)
        self.assertTrue(handler.has_event())


if __name__ == "__main__":
    unittest.main()
