# vim: expandtab:tabstop=4:shiftwidth=4
"""
"""
import asyncio
from typing import Tuple, Optional

from embrace import endpoint
from embrace.messagehandler import Message


class UDPConnection(endpoint.EndPoint, asyncio.BaseProtocol):
    """ wrapper class to manage asyncio UDP comms with TX and RX queues """

    def __init__(self, local_addr: Tuple[str, int], remote_addr: Tuple[str, int]):
        endpoint.EndPoint.__init__(self)
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        self.transport: Optional[asyncio.DatagramTransport] = None

    def start(self) -> None:
        asyncio.run_coroutine_threadsafe(self.transmit_loop(), self.comms_event_loop)
        asyncio.run_coroutine_threadsafe(self.application_loop(), self.comms_event_loop)

        connect = self.comms_event_loop.create_datagram_endpoint(
            lambda: self, local_addr=self.local_addr, remote_addr=self.remote_addr
        )
        asyncio.run_coroutine_threadsafe(connect, self.comms_event_loop)

    async def application_loop(self) -> None:
        """ TODO """
        while True:
            await asyncio.sleep(2.0)
            await self.enqueue_message(Message(b"TEST"))

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """ called when the connection is established.
        Note: required for create_datagram_endpoint """
        self.transport = transport  # type: ignore

    async def enqueue_message(self, message: Message) -> None:
        """ Add a message to the transmit queue."""
        await self.tx_queue.put(message)
        print("Queuing: {}".format(message.data.hex()))

    async def transmit_loop(self) -> None:
        """ coroutine that waits for messages in the transmit queue and transmits
        them via the UDP socket """

        while True:
            try:
                message = await self.tx_queue.get()
            except RuntimeError:
                break

            if self.transport:
                print(self.remote_addr, "TX: {}".format(message.data.hex()))
                try:
                    self.transport.sendto(message.data)
                except Exception as ex:
                    print(self.remote_addr, "***** failed to send msg: {}".format(ex))

    def datagram_received(self, data: bytes, addr: str) -> None:
        """ called when a UDP message is received.
        Note: required for create_datagram_endpoint """
        print(addr, "RX: {}".format(data.hex()))
        # TODO: integrate into EventHandler
        self.comms_event_loop.create_task(self.rx_queue.put(Message(data)))

    def error_received(self, exc: Exception) -> None:
        """ called when an error occurs
        Note: required for create_datagram_endpoint """
        print(self.remote_addr, "ERROR: {}".format(exc))

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """ called when the connection is lost
        Note: required for create_datagram_endpoint """
        # pylint: disable=unused-argument
        self.transport = None
