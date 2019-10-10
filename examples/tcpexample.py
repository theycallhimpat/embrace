import sys
sys.path.append('..')

from embrace import tcpconnection

if __name__ == "__main__":
    client = tcpconnection.TCPClient("127.0.0.1", 4444)
    client.connect()
    server = tcpconnection.TCPServer("0.0.0.0", 4444)
    server.serve()
    while True:
        import time
        time.sleep(1)
        print(".")