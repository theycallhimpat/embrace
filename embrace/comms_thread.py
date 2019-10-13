import asyncio
import threading

__comms_thread_running = False
__comms_event_loop = asyncio.new_event_loop()

# TODO: turn debugging off by default
__comms_event_loop.set_debug(True)


def event_loop() -> asyncio.AbstractEventLoop:
    return __comms_event_loop


def __thread_func() -> None:
    print("Running comms event loop")
    __comms_event_loop.run_forever()


def init() -> None:
    global __comms_thread_running
    if not __comms_thread_running:
        print("Running comms thread")
        thread = threading.Thread(target=__thread_func)
        thread.daemon = True
        thread.start()
        __comms_thread_running = True
