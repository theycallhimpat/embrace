""" Event Handler classes used to efficiently wait for an event to occur """

import asyncio


class Event:
    """ A single Event """

    def __init__(self, event_id: int) -> None:
        self._event_id = event_id

    @property
    def event_id(self) -> int:
        """ return an identifier for the type of the event """
        return self._event_id


class TimeoutException(Exception):
    """ Exception raised when a timeout occurs """

    pass


class EventHandler:
    """ Event sink, used by test agents to wait for events """

    def __init__(self) -> None:
        self.queue: asyncio.Queue[Event] = asyncio.Queue()

    def has_event(self) -> bool:
        """ return True if at least one Event is queued """
        return not self.queue.empty()

    def add_event(self, event: Event) -> None:
        """ adds an event to the back of the queue """
        self.queue.put_nowait(event)

    async def async_wait_for_next_event(self, timeout: float) -> Event:
        """ async waits for the next event to occur.
            If no event occurs within the timeout, raise TimeoutException.
            Otherwise return the Event """
        task = asyncio.create_task(self.queue.get())
        try:
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutException(
                "Timed out waiting for next event after {} seconds".format(timeout)
            )
        return task.result()

    def wait_for_next_event(self, timeout: float) -> Event:
        """ blocking / synchronous wait for the next event to occur.
            If no event occurs within the timeout, raise TimeoutException.
            Otherwise return the Event """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.async_wait_for_next_event(timeout))
        return result
