import socket
import threading

from HW1.Q1.Q2.Model.Account import Account
from HW1.Q1.Q2.Model.Channel import Channel
from HW1.Q1.Q2.Model.Group import Group
from HW1.Q1.Q2.constants import *

clients_lock = threading.Lock()
accounts_lock = threading.Lock()
channels_lock = threading.Lock()
groups_lock = threading.Lock()

clients: dict[str, socket.socket] = {}
accounts: list[Account] = []
channels: list[Channel] = []
groups: list[Group] = []


def send_command(conn: socket.socket, cmd: str):
    conn.send(COMMANDS[cmd].encode(ENCODING))



def handle_client(conn: socket.socket, addr):
    print(f"[CONNECTED] {addr}")
    need_to_repeat = True
    account_id = ""
    while need_to_repeat:
        send_command(conn, USER_ID_REQ)
        data = conn.recv(1024)
        if not data:
            conn.close()
        account_id = data.decode(ENCODING)
        if account_id not in clients:
            need_to_repeat = False
        else:
            send_command(conn, ACCOUNT_ALREADY_EXIST)

    account_exist = False
    if any([x for x in accounts if x.user_id == account_id]):
        account = [x for x in accounts if x.user_id == account_id][0]
        account_exist = True
    else:
        account = Account(account_id)

    with clients_lock:
        clients[account.user_id] = conn
        if not account_exist:
            with accounts_lock:
                accounts.append(account)

    if not account_exist:
        send_command(conn, ACCOUNT_CREATE_SUCCESS)
    else:
        send_command(conn,CONNECTED_TO_ALREADY_EXIST_ACCOUNT)
    try:
        while True:
            data = conn.recv(1024)
    except:
        with clients_lock:
            clients.pop(account_id)
        conn.close()


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
