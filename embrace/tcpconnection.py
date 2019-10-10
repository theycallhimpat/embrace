# vim: expandtab:tabstop=4:shiftwidth=4
"""

"""
import asyncio
import concurrent.futures
from typing import Generator, Optional

from embrace import endpoint
from embrace.messagehandler import Message

CONNECTION_FAILURE_TIMEOUT_SECONDS = 1.0

class TCPConnection(endpoint.EndPoint):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop]) -> None:
        endpoint.EndPoint.__init__(self, loop=loop)
        self.connected = False
        self.writer: Optional[asyncio.StreamWriter] = None

    async def application_loop(self) -> None:
        """ TODO """
        while True:
            await asyncio.sleep(2.0)
            if self.connected:
                self.enqueue_message(Message(b"TEST"))

    async def transmit_loop(self) -> None:
        """Take messages from the transmit queue and send to the socket"""
        while True:
            try:
                message = await self.tx_queue.get()
            except RuntimeError:
                break

            if self.writer:
                try:
                    await self.transmit_data(self.writer, message.data)
                    self.on_message_transmit(message)
                except Exception as ex:
                    print("*****  Failed to transmit data: {}".format(ex))

    async def transmit_data(self, writer: asyncio.StreamWriter, data: bytes) -> None:
        """If connected, add a message to the transmit queue and yield until it has been transmitted."""
        if self.connected:
            print("TX: {}".format(data.hex()))
            writer.write(data)
            await writer.drain()
        else:
            print("**** Unable to transmit, server is not connected")

    def enqueue_message(self, message: Message) -> None:
        """ Add a message to the transmit queue."""
        asyncio.run_coroutine_threadsafe(self.tx_queue.put(message), self.event_loop)
        print("Queuing: {}".format(message.data.hex()))

    async def receive_loop(self, reader: asyncio.StreamReader) -> None:
        """While the connection to the server is open, receive data and add it to the receive queue. """
        while not reader.at_eof():
            try:
                data = await reader.read(4096)
            except Exception as ex:
                print("***** Caught exception reading from socket {}".format(ex))
                break

            if not data:
                # if data is empty
                continue

            await self.rx_queue.put(Message(data))
            print("RX: {}: {}".format(data, data.hex()))

    def on_connect(self) -> None:
        self.connected = True

    def on_disconnect(self) -> None:
        self.connected = False
    
    def on_bytes_receive(self, data: bytes) -> None:
        pass

    def on_message_transmit(self, message: Message) -> None:
        pass

class TCPClient(TCPConnection):
    """ Manages a TCP connection to a single server"""

    def __init__(self, ip_address: str, port: int, loop: Optional[asyncio.AbstractEventLoop]=None) -> None:
        TCPConnection.__init__(self, loop=loop)
        self.ip_address = ip_address
        self.port = port

    def connect(self) -> None:
        self.event_loop.create_task(self.connect_loop())

    async def connect_loop(self) -> None:
        """Loop forever, invoking handle_single_connection, catching all Exceptions and sleeping between attempts."""
        while True:
            try:
                await self.handle_single_connection()
            except ConnectionRefusedError as ex:
                print("Connection refused: {}".format(ex))
            except OSError as ex:
                print("Connection error: {}".format(ex))
            except Exception as ex:
                print("***** Unknown exception: {}".format(ex))

            if self.connected:
                self.connected = False

            await asyncio.sleep(CONNECTION_FAILURE_TIMEOUT_SECONDS)

    async def handle_single_connection(self) -> None:
        """Attempt to establish a connection with the server, then spawns new
        coroutines for handling socket communication: 
        - a receiver that receives data, and passes it upstream
        - a transmitter than send data on
        As all of these coroutines loop until the connection is terminated, this
        coroutine yields until any of them exit, then cleans up and exits
        itself."""

        print("Opening connection...")
        # exceptions handled in calling function
        reader, writer = await asyncio.open_connection(
            self.ip_address, self.port, loop=self.event_loop
        )
        self.writer = writer
        self.connected = True
        self.on_connect()
        print("Connected")
        if not self.tx_queue.empty():
            print("found items in tx queue; flushing")
            while not self.tx_queue.empty():
                self.tx_queue.get_nowait()

        # futures = [self.receive_loop(reader), self.transmit_loop(), self.application_loop()]
        futures = [self.receive_loop(reader), self.transmit_loop()]
        _, pending = await asyncio.wait(
            futures, return_when=asyncio.FIRST_COMPLETED
        )
        for fut in pending:
            fut.cancel()

        print("Closed connection")
        self.on_disconnect()
        writer.close()


class TCPServer(TCPConnection):
    """ Manages a TCP connection from a client """

    def __init__(self, ip_address: str, port: int, loop: Optional[asyncio.AbstractEventLoop]=None) -> None:
        TCPConnection.__init__(self, loop=loop)
        self.ip_address = ip_address
        self.port = port

    def serve(self) -> None:
        server_coro = asyncio.start_server(
            self.handle_single_session, self.ip_address, self.port, loop=self.event_loop
        )
        self.event_loop.create_task(server_coro)

    async def handle_single_session(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Coroutine for communicating with a newly connected client and spawns coroutines:
        - TODO
        This coroutine yields until any coroutines return cleans up and then exits itself."""

        print("Server: Connected")
        if self.connected:
            raise Exception("Already Connected")
        else:
            self.connected = True
            self.writer = writer

        futures = [
            self.receive_loop(reader),
            self.transmit_loop(),
            self.application_loop(),
        ]
        _, pending = await asyncio.wait(
            futures, return_when=asyncio.FIRST_COMPLETED
        )
        for fut in pending:
            fut.cancel()

        print("Server: Closed connection")
        self.connected = False
        self.writer = None
        writer.close()