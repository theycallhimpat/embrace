# vim: expandtab:tabstop=4:shiftwidth=4
"""
TODO
"""
import asyncio
from typing import Optional

from embrace import comms_thread
from embrace.messagehandler import Message, MessageHandler
from embrace.eventhandler import AsyncEventHandler

# TODO: work out the correct inheritance hierachy to use.
# For example, do we even need MessageHandler?
class EndPoint(AsyncEventHandler, MessageHandler):
    def __init__(
        self, comms_event_loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        AsyncEventHandler.__init__(self)
        MessageHandler.__init__(self)

        if comms_event_loop is None:
            # by default, use an event loop in another thread
            comms_event_loop = comms_thread.event_loop()
        self.__comms_event_loop = comms_event_loop

        # TODO: rx_queue may not be needed
        self.rx_queue: "asyncio.Queue[Message]" = asyncio.Queue(
            loop=self.comms_event_loop
        )
        self.tx_queue: "asyncio.Queue[Message]" = asyncio.Queue(
            loop=self.comms_event_loop
        )

        comms_thread.init()

    @property
    def comms_event_loop(self) -> asyncio.AbstractEventLoop:
        """ return the asyncio event loop used for communications """
        return self.__comms_event_loop
