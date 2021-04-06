import socket
import threading

from HW1.Q2.constants import *


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

            # Account
            elif msg == COMMANDS[ACCOUNT_CREATE_SUCCESS]:
                print(USER_MSG[ACCOUNT_CREATE_SUCCESS])
            elif msg == COMMANDS[ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST]:
                print(USER_MSG[ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST])
            elif msg == COMMANDS[CONNECTED_TO_ALREADY_EXIST_ACCOUNT]:
                print(USER_MSG[CONNECTED_TO_ALREADY_EXIST_ACCOUNT])

            # Channel or Group Create
            elif msg == COMMANDS[CHANNEL_CREATED]:
                print(USER_MSG[CHANNEL_CREATED])
            elif msg == COMMANDS[GROUP_CREATED]:
                print(USER_MSG[GROUP_CREATED])

            # Channel or Group join
            elif msg == COMMANDS[CHANNEL_JOIN]:
                print(USER_MSG[CHANNEL_JOIN])
            elif msg == COMMANDS[GROUP_JOIN]:
                print(USER_MSG[GROUP_JOIN])

            # Channel or Group already joined
            elif msg == COMMANDS[GROUP_ALREADY_JOINED]:
                print(USER_MSG[GROUP_ALREADY_JOINED])
            elif msg == COMMANDS[CHANNEL_ALREADY_JOINED]:
                print(USER_MSG[CHANNEL_ALREADY_JOINED])


            # Channel or Group not exists
            elif msg == COMMANDS[NO_SUCH_GROUP]:
                print(USER_MSG[NO_SUCH_GROUP])
            elif msg == COMMANDS[NO_SUCH_CHANNEL]:
                print(USER_MSG[NO_SUCH_CHANNEL])

            # Channel Messages
            elif msg == COMMANDS[CHANNEL_WRITE_INVALID_PERMISSION]:
                print(USER_MSG[CHANNEL_WRITE_INVALID_PERMISSION])
            elif msg == COMMANDS[CHANNEL_MESSAGE_SUCCESS]:
                print(USER_MSG[CHANNEL_MESSAGE_SUCCESS])
            elif msg == COMMANDS[NOT_SUBSCRIBED_TO_CHANNEL]:
                print(USER_MSG[NOT_SUBSCRIBED_TO_CHANNEL])

            # Group Messages
            elif msg == COMMANDS[GROUP_MESSAGE_SUCCESS]:
                print(USER_MSG[GROUP_MESSAGE_SUCCESS])
            elif msg == COMMANDS[GROUP_WRITE_INVALID_PERMISSION]:
                print(USER_MSG[GROUP_WRITE_INVALID_PERMISSION])
            elif msg == COMMANDS[NOT_SUBSCRIBED_TO_GROUP]:
                print(USER_MSG[NOT_SUBSCRIBED_TO_GROUP])

            # PV Messages
            elif msg == COMMANDS[PRIVATE_MESSAGE_SUCCESS]:
                print(USER_MSG[PRIVATE_MESSAGE_SUCCESS])
            elif msg == COMMANDS[NO_PV_BETWEEN_THESE_USERS]:
                print(USER_MSG[NO_PV_BETWEEN_THESE_USERS])


            elif msg == COMMANDS[NO_SUCH_GROUP_OR_USER_OR_CHANNEL]:
                print(USER_MSG[NO_SUCH_GROUP_OR_USER_OR_CHANNEL])


            elif msg == COMMANDS[NO_SUCH_USER]:
                print(USER_MSG[NO_SUCH_USER])



            # Show all messages. At first, we get how many bytes we need to receive then we receive whole message.
            elif msg.startswith(COMMANDS[SEND_ALL_MESSAGE_PROTOCOL]):
                length = int(msg.split()[1])
                full_msg = sock.recv(length)
                print(full_msg.decode(ENCODING))

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
