import socket
import threading

HOST = "127.0.0.1"
PORT = 5052
ENCODING = "ascii"


def handle_send(sock: socket.socket):
    try:
        while True:
            num1 = input()
            sock.send(num1.encode(ENCODING))
    except:
        sock.close()


def handle_receive(sock: socket.socket):
    try:
        while True:
            print(sock.recv(1024).decode(ENCODING))
    except:
        sock.close()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    t_send = threading.Thread(target=handle_send, args=(s,))
    t_receive = threading.Thread(target=handle_receive, args=(s,))
    t_send.start()
    t_receive.start()
