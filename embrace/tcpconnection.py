# vim: expandtab:tabstop=4:shiftwidth=4
"""

"""
import asyncio
import concurrent.futures

CONNECTION_FAILURE_TIMEOUT_SECONDS = 1.0


class TCPConnection:
    def __init__(self, loop):
        self.loop = loop
        self.rx_queue = asyncio.Queue(loop=loop)
        self.tx_queue = asyncio.Queue(loop=loop)
        self.connected = False
        self.writer = None

    @asyncio.coroutine
    def application_loop(self):
        """ TODO """
        while True:
            yield from asyncio.sleep(2.0)
            if self.connected:
                yield from self.enqueue_message(b"TEST")

    @asyncio.coroutine
    def transmit_loop(self):
        """Take messages from the transmit queue and send to the socket"""
        while True:
            try:
                message = yield from self.tx_queue.get()
            except RuntimeError:
                break

            try:
                yield from self.transmit_data(self.writer, message)
            except Exception as ex:
                print("*****  Failed to transmit data: {}".format(ex))

    @asyncio.coroutine
    def transmit_data(self, writer, data):
        """If connected, add a message to the transmit queue and yield until it has been transmitted."""
        if self.connected:
            print("TX: {}".format(data.hex()))
            writer.write(data)
            yield from writer.drain()
        else:
            print("**** Unable to transmit, server is not connected")

    @asyncio.coroutine
    def enqueue_message(self, message):
        """ Add a message to the transmit queue."""
        yield from self.tx_queue.put(message)
        print("Queuing: {}".format(message.hex()))

    @asyncio.coroutine
    def receive_loop(self, reader):
        """While the connection to the server is open, receive data and add it to the receive queue. """
        while not reader.at_eof():
            try:
                data = yield from reader.read(4096)
            except Exception as ex:
                print("***** Caught exception reading from socket {}".format(ex))
                break

            if not data:
                # if data is empty
                continue
            yield from self.rx_queue.put(data)
            print("RX: {}: {}".format(data, data.hex()))


class TCPClient(TCPConnection):
    """ Manages a TCP connection to a single server"""

    def __init__(self, loop, ip_address, port):
        super(TCPClient, self).__init__(loop=loop)
        self.ip_address = ip_address
        self.port = port

        self.loop.create_task(self.connect_loop())

    @asyncio.coroutine
    def connect_loop(self):
        """Loop forever, invoking handle_single_connection, catching all Exceptions and sleeping between attempts."""
        while True:
            try:
                yield from self.handle_single_connection()
            except ConnectionRefusedError as ex:
                print("Connection refused: {}".format(ex))
            except OSError as ex:
                print("Connection error: {}".format(ex))
            except Exception as ex:
                print("***** Unknown exception: {}".format(ex))

            if self.connected:
                self.connected = False

            yield from asyncio.sleep(CONNECTION_FAILURE_TIMEOUT_SECONDS)

    @asyncio.coroutine
    def handle_single_connection(self):
        """Attempt to establish a connection with the server, then spawns new
        coroutines for handling socket communication: 
        - a receiver that receives data, and passes it upstream
        - a transmitter than send data on
        As all of these coroutines loop until the connection is terminated, this
        coroutine yields until any of them exit, then cleans up and exits
        itself."""

        print("Opening connection...")
        # exceptions handled in calling function
        reader, writer = yield from asyncio.open_connection(
            self.ip_address, self.port, loop=self.loop
        )
        self.writer = writer
        self.connected = True
        print("Connected")
        if not self.tx_queue.empty():
            print("found items in tx queue; flushing")
            while not self.tx_queue.empty():
                self.tx_queue.get_nowait()

        # futures = [self.receive_loop(reader), self.transmit_loop(), self.application_loop()]
        futures = [self.receive_loop(reader), self.transmit_loop()]
        _, pending = yield from asyncio.wait(
            futures, return_when=asyncio.FIRST_COMPLETED
        )
        for fut in pending:
            fut.cancel()

        print("Closed connection")
        writer.close()


class TCPServer(TCPConnection):
    """ Manages a TCP connection from a client """

    def __init__(self, loop, ip_address, port):
        super(TCPServer, self).__init__(loop=loop)
        self.ip_address = ip_address
        self.port = port

        server_coro = asyncio.start_server(
            self.handle_single_session, self.ip_address, self.port, loop=self.loop
        )
        self.loop.create_task(server_coro)

    @asyncio.coroutine
    def handle_single_session(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
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
        _, pending = yield from asyncio.wait(
            futures, return_when=asyncio.FIRST_COMPLETED
        )
        for fut in pending:
            fut.cancel()

        print("Server: Closed connection")
        self.connected = False
        self.writer = None
        writer.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    client = TCPClient(loop, "127.0.0.1", 4444)
    server = TCPServer(loop, "0.0.0.0", 4444)
    loop.run_forever()
