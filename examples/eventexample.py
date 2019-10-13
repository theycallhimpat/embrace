import sys

sys.path.append("..")
import threading

from embrace.eventhandler import AsyncEventHandler, ReceiveEvent


def threadfunc(e: AsyncEventHandler, time_in_secs: float) -> None:
    import time

    time.sleep(time_in_secs)
    e.add_event_threadsafe(ReceiveEvent(b"BANG"))


if __name__ == "__main__":
    e = AsyncEventHandler()

    print("+++ Expecting message within 2 seconds ...")
    threading.Thread(target=threadfunc, args=(e, 1.5)).start()
    print(e.wait_for_next_event(2.0))

    print("+++ Expecting message within 1 second (WILL FAIL) ...")
    threading.Thread(target=threadfunc, args=(e, 1.5)).start()
    print(e.wait_for_next_event(1.0))
