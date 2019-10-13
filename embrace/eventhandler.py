# vim: expandtab:tabstop=4:shiftwidth=4
""" Event Handler classes used to efficiently wait for an event to occur """

import asyncio
from enum import IntEnum
from typing import Optional
import time


class EventType(IntEnum):
    CONNECT = 1
    DISCONNECT = 2
    CONNECT_FAIL = 3
    RECEIVE = 4
    # TODO: doesn't distinguish between bytes or message received?
    # TODO: transmit event?
    # TODO: error event e.g. for protocol errors? Sounds good


class Event:
    """ A single Event """

    def __init__(self, event_id: EventType) -> None:
        self.__event_id = event_id

    @property
    def event_id(self) -> EventType:
        """ return an identifier for the type of the event """
        return self.__event_id


class ConnectionEvent(Event):
    """ A single Event for when a connection occurs """

    def __init__(self) -> None:
        Event.__init__(self, EventType.CONNECT)


class DisconnectionEvent(Event):
    """ A single Event for when a disconnection occurs """

    def __init__(self) -> None:
        Event.__init__(self, EventType.DISCONNECT)


class ConnectionFailedEvent(Event):
    """ A single Event for when a connection attempt fails """

    def __init__(self) -> None:
        Event.__init__(self, EventType.CONNECT_FAIL)


class ReceiveEvent(Event):
    """ A single Event for a received data """

    def __init__(self, data: bytes) -> None:
        Event.__init__(self, EventType.RECEIVE)
        self.__data = data

    @property
    def data(self) -> bytes:
        """ return the received data"""
        return self.__data


class TimeoutException(Exception):
    """ Exception raised when a timeout occurs """

    pass


class BaseEventHandler:
    pass


class AsyncEventHandler(BaseEventHandler):
    """ Event sink, used by test agents to wait for events """

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop
        # TODO: disable debugging by default
        self.loop.set_debug(True)
        self.queue: "asyncio.Queue[Event]" = asyncio.Queue()

    def has_event(self) -> bool:
        """ return True if at least one Event is queued """
        return not self.queue.empty()

    def num_queued_events(self) -> int:
        """ return the number of queued Events """
        return self.queue.qsize()

    def add_event_unsafe(self, event: Event) -> None:
        """ adds an event to the back of the queue in a thread-unsafe manner
            which is not suitable for use from other threads"""
        self.queue.put_nowait(event)

    def add_event_threadsafe(self, event: Event) -> None:
        """ adds an event to the back of the queue, but which can be called by
            code running in a separate thread """
        # TODO: mypy complains about using add_event and it might be because it's not
        # a coroutine. But investigate further
        # asyncio.run_coroutine_threadsafe(self.add_event(event), self.loop)
        asyncio.run_coroutine_threadsafe(self.queue.put(event), self.loop)

    async def async_wait_for_next_event(self, timeout: float) -> Event:
        """ async waits for the next event to occur.
            If no event occurs within the timeout, raise TimeoutException.
            Otherwise return the Event """
        task = asyncio.ensure_future(self.queue.get())
        try:
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutException(
                "Timed out after {} seconds waiting for next event".format(timeout)
            ) from None
        return task.result()

    def wait_for_next_event(self, timeout: float) -> Event:
        """ blocking / synchronous wait for the next event to occur.
            If no event occurs within the timeout, raise TimeoutException.
            Otherwise return the Event """
        result = self.loop.run_until_complete(self.async_wait_for_next_event(timeout))
        return result

    def assert_event(self, event_id: EventType, timeout: float) -> Event:
        event = self.wait_for_next_event(timeout=timeout)
        assert event.event_id == event_id, "Expected a {} event, but found {}".format(
            event_id.name, event.event_id.name
        )
        return event

    def assert_has_no_events(self) -> None:
        assert not self.has_event(), "Expected no events, but found {}".format(
            self.num_queued_events
        )

    def assert_has_no_event(self) -> None:
        self.assert_has_no_events()

    def assert_has_event(self) -> None:
        assert self.has_event(), "Expected an event, but found none"

    def assert_has_events(self) -> None:
        return self.assert_has_event()

    def assert_receive(self, data: bytes, timeout: float) -> ReceiveEvent:
        event = self.assert_event(EventType.RECEIVE, timeout=timeout)
        assert isinstance(event, ReceiveEvent)
        assert event.data == data, "Expected received data {}, but found {}".format(
            data, event.data
        )
        return event

    # def assert_no_events_occur
    # def to_string
    # clear
