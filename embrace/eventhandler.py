def dummy(x: int, y: int) -> int:
    return x + y

class Event:
    pass

class EventHandler:
    def __init__(self):
        pass

    def has_event(self) -> bool:
        return False

    def add_event(self, event: Event) -> None:
        pass
