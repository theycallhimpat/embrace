import sys
sys.path.append('..')

from embrace import udpconnection

if __name__ == "__main__":
    u1 = udpconnection.UDPConnection(("127.0.0.1", 4444), ("127.0.0.1", 5555))
    u1.start()
    u2 = udpconnection.UDPConnection(("127.0.0.1", 5555), ("127.0.0.1", 4444))
    u2.start()
    while True:
        import time
        time.sleep(1)
        print(".")