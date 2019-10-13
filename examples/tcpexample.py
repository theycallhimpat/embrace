import sys

sys.path.append("..")

import time
from embrace import tcpconnection
from embrace.messagehandler import Message
from embrace.eventhandler import EventType


class EchoServer(tcpconnection.TCPServer):
    def on_bytes_receive(self, data: bytes) -> None:
        print("YAAAAAAAAAAAAAAAAAAAAAA: {}".format(data))
        self.enqueue_message(Message(data))


if __name__ == "__main__":
    # server = tcpconnection.TCPServer("0.0.0.0", 4444)
    server = EchoServer("0.0.0.0", 4444)
    server.serve()
    server.assert_has_no_events()
    time.sleep(0.5)

    client = tcpconnection.TCPClient("127.0.0.1", 4444)
    client.assert_has_no_events()
    client.connect(timeout=5)

    # e = client.wait_for_next_event(5)
    # client.assert_event(EventType.DISCONNECT, 5)
    # client.assert_event(EventType.CONNECT, 5)
    while True:
        time.sleep(1)
        print(".")
        client.enqueue_message(Message(b"TEST"))
