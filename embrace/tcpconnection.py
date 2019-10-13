# vim: expandtab:tabstop=4:shiftwidth=4
"""

"""
import asyncio
import concurrent.futures
from typing import Generator, Optional

from embrace import endpoint, eventhandler
from embrace.messagehandler import Message

CONNECTION_FAILURE_TIMEOUT_SECONDS = 1.0


class TCPConnection(endpoint.EndPoint):
    def __init__(self) -> None:
        endpoint.EndPoint.__init__(self)
        self.__connected = False
        self.writer: Optional[asyncio.StreamWriter] = None

    @property
    def connected(self) -> bool:
        """ return true if the socket is connected"""
        return self.__connected

    def assert_connected(self) -> None:
        assert self.connected

    def assert_disconnected(self) -> None:
        assert not self.connected

    async def application_loop(self) -> None:
        """ TODO """
        while True:
            await asyncio.sleep(1.0)

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
        asyncio.run_coroutine_threadsafe(
            self.tx_queue.put(message), self.comms_event_loop
        )
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

            self.on_bytes_receive(data)
            # await self.rx_queue.put(Message(data))
            print("RX: {}: {}".format(data, data.hex()))

    def on_connect(self) -> None:
        self.add_event_threadsafe(eventhandler.ConnectionEvent())
        self.__connected = True

    def on_disconnect(self) -> None:
        self.add_event_threadsafe(eventhandler.DisconnectionEvent())
        self.__connected = False

    def on_connect_fail(self) -> None:
        self.add_event_threadsafe(eventhandler.ConnectionFailedEvent())
        self.__connected = False

    def on_bytes_receive(self, data: bytes) -> None:
        self.add_event_threadsafe(eventhandler.ReceiveEvent(data))

    def on_message_transmit(self, message: Message) -> None:
        pass


class TCPClient(TCPConnection):
    """ Manages a TCP connection to a single server"""

    def __init__(self, ip_address: str, port: int) -> None:
        TCPConnection.__init__(self)
        self.ip_address = ip_address
        self.port = port

    def start_connection(self) -> None:
        asyncio.run_coroutine_threadsafe(self.connect_loop(), self.comms_event_loop)

    def connect(self, timeout: float) -> None:
        self.start_connection()
        self.assert_event(eventhandler.EventType.CONNECT, timeout=timeout)

    async def connect_loop(self) -> None:
        """Loop forever, invoking handle_single_connection, catching all Exceptions and sleeping between attempts."""
        while True:
            try:
                await self.handle_single_connection()
            except ConnectionRefusedError as ex:
                print("Connection refused: {}".format(ex))
                self.on_connect_fail()
            except OSError as ex:
                print("Connection error: {}".format(ex))
                self.on_connect_fail()
            except Exception as ex:
                print("***** Unknown exception: {}".format(ex))
                self.on_connect_fail()

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
            self.ip_address, self.port, loop=self.comms_event_loop
        )
        self.writer = writer
        self.on_connect()
        print("Connected")
        if not self.tx_queue.empty():
            print("found items in tx queue; flushing")
            while not self.tx_queue.empty():
                self.tx_queue.get_nowait()

        futures = [
            self.receive_loop(reader),
            self.transmit_loop(),
            # self.application_loop(),
        ]
        _, pending = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
        for fut in pending:
            fut.cancel()

        print("Closed connection")
        self.on_disconnect()
        writer.close()


class TCPServer(TCPConnection):
    """ Manages a TCP connection from a client """

    def __init__(self, ip_address: str, port: int) -> None:
        TCPConnection.__init__(self)
        self.ip_address = ip_address
        self.port = port

    def serve(self) -> None:
        server_coro = asyncio.start_server(
            self.handle_single_session,
            self.ip_address,
            self.port,
            loop=self.comms_event_loop,
        )
        # self.comms_event_loop.create_task(server_coro)
        asyncio.run_coroutine_threadsafe(server_coro, self.comms_event_loop)

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
            self.on_connect()
            self.writer = writer

        # TODO: this is quite similar to handle_single_connection in TCPClient

        futures = [
            self.receive_loop(reader),
            self.transmit_loop(),
            # self.application_loop(),
        ]
        _, pending = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
        for fut in pending:
            fut.cancel()

        print("Server: Closed connection")
        self.on_disconnect()
        self.writer = None
        writer.close()
