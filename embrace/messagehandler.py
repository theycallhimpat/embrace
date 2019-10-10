# vim: expandtab:tabstop=4:shiftwidth=4

class Message:
    def __init__(self, data: bytes) -> None:
        self.data = data

class MessageHandler:
    def bytes_received(self, data: bytes) -> None:
        self.message_received(Message(data))

    def message_received(self, message: Message) -> None:
        self.handle_message(message)

    def handle_message(self, message: Message) -> None:
        pass