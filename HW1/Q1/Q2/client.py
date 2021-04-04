import socket
import threading

from HW1.Q1.Q2.constants import *


def handle_send(sock: socket.socket):
    try:
        while True:
            message = input()
            sock.send(message.encode(ENCODING))
    except:
        sock.close()


def handle_receive(sock: socket.socket):
    try:
        while True:
            msg = sock.recv(1024).decode(ENCODING)
            if msg == COMMANDS[USER_ID_REQ]:
                print(USER_MSG[USER_ID_REQ])
            elif msg == COMMANDS[ACCOUNT_CREATE_SUCCESS]:
                print(USER_MSG[ACCOUNT_CREATE_SUCCESS])
            elif msg == COMMANDS[ACCOUNT_ALREADY_EXIST]:
                print(USER_MSG[ACCOUNT_ALREADY_EXIST])
            elif msg == COMMANDS[CONNECTED_TO_ALREADY_EXIST_ACCOUNT]:
                print(USER_MSG[CONNECTED_TO_ALREADY_EXIST_ACCOUNT])
            else:
                print(msg)

    except:
        sock.close()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    t_send = threading.Thread(target=handle_send, args=(s,))
    t_receive = threading.Thread(target=handle_receive, args=(s,))
    t_send.start()
    t_receive.start()
