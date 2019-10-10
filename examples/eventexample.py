import sys
sys.path.append('..')

from embrace import eventhandler

if __name__ == "__main__":
    e = eventhandler.EventHandler()
    import threading
    def threadfunc(e, time_in_secs):
        import time
        time.sleep(time_in_secs)
        e.add_event('BANG!')
    threading.Thread(target=threadfunc, args=(e,1.5)).start()
    print(e.wait_for_next_event(2.0))
    threading.Thread(target=threadfunc, args=(e,2.5)).start()
    print(e.wait_for_next_event(2.0))