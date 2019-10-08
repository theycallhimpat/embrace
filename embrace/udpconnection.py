# vim: expandtab:tabstop=4:shiftwidth=4
"""
"""
import asyncio


class UDPConnection:
    """ wrapper class to manage asyncio UDP comms with TX and RX queues """

    def __init__(self, loop, local_addr, remote_addr):
        self.loop = loop
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        self.rx_queue = asyncio.Queue(loop=loop)
        self.tx_queue = asyncio.Queue(loop=loop)
        self.connected = False
        self.transport = None

        loop.create_task(self.transmit_loop())
        loop.create_task(self.application_loop())

        connect = loop.create_datagram_endpoint(
            lambda: self, local_addr=self.local_addr, remote_addr=self.remote_addr
        )
        loop.create_task(connect)

    @asyncio.coroutine
    def application_loop(self):
        """ TODO """
        while True:
            yield from asyncio.sleep(2.0)
            if self.connected:
                yield from self.enqueue_message(b"TEST")

    def connection_made(self, transport):
        """ called when the connection is established.
        Note: required for create_datagram_endpoint """
        self.transport = transport
        self.connected = True

    @asyncio.coroutine
    def enqueue_message(self, message):
        """ Add a message to the transmit queue."""
        yield from self.tx_queue.put(message)
        print("Queuing: {}".format(message.hex()))

    @asyncio.coroutine
    def transmit_loop(self):
        """ coroutine that waits for messages in the transmit queue and transmits
        them via the UDP socket """

        while True:
            try:
                message = yield from self.tx_queue.get()
            except RuntimeError:
                break

            if self.connected:
                print(self.remote_addr, "TX: {}".format(message.hex()))
                try:
                    self.transport.sendto(message)
                except Exception as ex:
                    print(self.remote_addr, "***** failed to send msg: {}".format(ex))

    def datagram_received(self, data, addr):
        """ called when a UDP message is received.
        Note: required for create_datagram_endpoint """
        print(addr, "RX: {}".format(data.hex()))
        self.loop.create_task(self.rx_queue.put(data))

    def error_received(self, exc):
        """ called when an error occurs
        Note: required for create_datagram_endpoint """
        print(self.remote_addr, "ERROR: {}".format(exc))

    def connection_lost(self, exc):
        """ called when the connection is lost
        Note: required for create_datagram_endpoint """
        # pylint: disable=unused-argument
        self.transport = None


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    u1 = UDPConnection(loop, ("127.0.0.1", 4444), ("127.0.0.1", 5555))
    u2 = UDPConnection(loop, ("127.0.0.1", 5555), ("127.0.0.1", 4444))
    print("doing it")
    loop.run_forever()
