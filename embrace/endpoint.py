# vim: expandtab:tabstop=4:shiftwidth=4
"""
TODO
"""
import asyncio 
from typing import Optional

from embrace import comms_thread
from embrace.messagehandler import Message

#class EndPoint(eventhandler.EventHandler, messagehandler.MessageHandler):
class EndPoint():
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop]) -> None:
        if loop is None:
            loop = comms_thread.event_loop()
        self.__loop = loop
        self.rx_queue: 'asyncio.Queue[Message]' = asyncio.Queue(loop=self.event_loop)
        self.tx_queue: 'asyncio.Queue[Message]' = asyncio.Queue(loop=self.event_loop)
        comms_thread.init()

    @property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        """ return the asyncio event loop used for communications """
        return self.__loop