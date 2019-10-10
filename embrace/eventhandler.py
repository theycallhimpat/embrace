# vim: expandtab:tabstop=4:shiftwidth=4
""" Event Handler classes used to efficiently wait for an event to occur """

import asyncio
from typing import Optional


class Event:
    """ A single Event """

    def __init__(self, event_id: int) -> None:
        self._event_id = event_id

    @property
    def event_id(self) -> int:
        """ return an identifier for the type of the event """
        return self._event_id


class MessageEvent:
    """ A single Event for a received Message """

    def __init__(self, event_id: int, message: bytes) -> None:
        self._event_id = event_id
        self._message = message

class TimeoutException(Exception):
    """ Exception raised when a timeout occurs """

    pass


class EventHandler:
    """ Event sink, used by test agents to wait for events """

    def __init__(self, loop:Optional[asyncio.AbstractEventLoop]=None) -> None:
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.queue: "asyncio.Queue[Event]" = asyncio.Queue()

    def has_event(self) -> bool:
        """ return True if at least one Event is queued """
        return not self.queue.empty()

    def add_event(self, event: Event) -> None:
        """ adds an event to the back of the queue """
        self.queue.put_nowait(event)

    def add_event_threadsafe(self, event: Event) -> None:
        """ adds an event to the back of the queue, but which can be called by 
            code running in a separate thread """
        # TODO: mypy complains about using add_event and it might be because it's not
        # a coroutine. But investigate further
        #asyncio.run_coroutine_threadsafe(self.add_event(event), self.loop)
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

    # def assert_has_no_events
    # def assert_has_events
    # def assert_no_events_occur
    # def num_events
    # def to_string
    # clear
