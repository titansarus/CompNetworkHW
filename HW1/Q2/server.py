import socket
import threading

from HW1.Q2.Model.Message import Message
from HW1.Q2.Model.Account import Account
from HW1.Q2.Model.Channel import Channel
from HW1.Q2.Model.Group import Group
from HW1.Q2.constants import *

clients_lock = threading.Lock()
accounts_lock = threading.Lock()
channels_lock = threading.Lock()
groups_lock = threading.Lock()
private_message_lock = threading.Lock()

clients: dict[str, socket.socket] = {}
accounts: list[Account] = []
channels: list[Channel] = []
groups: list[Group] = []

private_messages: dict[tuple[str, str], list[Message]] = {}


# Send Command / Error / Success Message to Client
def send_command(conn: socket.socket, cmd: str):
    conn.send(COMMANDS[cmd].encode(ENCODING))


# Send all messages that are stored in 'messages' list to the client
def send_all_message(conn: socket.socket, messages: list[Message]):
    all_msg = ""
    for msg in messages:
        all_msg += (str(msg) + "\n")
    # Because messages can be very long, at first their size is sent to the client.
    # So client will be aware of how many bytes it should expect to get.
    send_len = len(all_msg) + 2
    send_length_msg = COMMANDS[SEND_ALL_MESSAGE_PROTOCOL] + " " + str(send_len)
    conn.send(send_length_msg.encode(ENCODING))
    conn.send(all_msg.encode(ENCODING))


# Uniqueness check for main entities. Return True if Unique.
def is_unique_channel(id):
    return not any([x for x in channels if x.id == id])


def is_unique_group(id):
    return not any([x for x in groups if x.id == id])


def is_unique_account(id):
    return not any([x for x in accounts if x.user_id == id])


def is_unique_client(id):
    return id not in clients


def handle_client(conn: socket.socket, addr):
    print(f"[CONNECTED] {addr}")
    account_id = make_or_find_account(conn)
    try:
        while True:
            data = conn.recv(1024).decode(ENCODING)
            # In each of these function, a regex match is checked. So only one of the will be executed.
            create_group(account_id, conn, data)
            create_channel(account_id, conn, data)
            join_group(account_id, conn, data)
            join_channel(account_id, conn, data)
            send_channel_message(account_id, conn, data)
            view_channel_message(account_id, conn, data)
            send_group_or_pv_message(account_id, conn, data)
            view_group_message(account_id, conn, data)
            view_private_message(account_id, conn, data)
    except:
        with clients_lock:
            clients.pop(account_id)
    conn.close()


def view_private_message(account_id, conn, data):
    result = VIEW_PV_REGEX.match(data)
    if result:
        acc_id = result.group(1)
        accs = [x for x in accounts if x.user_id == acc_id]
        if len(accs) > 0:
            acc = accs[0]
            key = tuple(sorted((account_id, acc.user_id)))
            if key in private_messages:
                send_all_message(conn, private_messages[key])
            else:
                send_command(conn, NO_PV_BETWEEN_THESE_USERS)

        else:
            send_command(conn, NO_SUCH_USER)


def view_group_message(account_id, conn, data):
    result = VIEW_GROUP_REGEX.match(data)
    if result:
        group_id = result.group(1)
        grps = [x for x in groups if x.id == group_id]
        if len(grps) > 0:
            group = grps[0]
            if account_id in group.members:
                send_all_message(conn, group.messages)
            else:
                send_command(conn, NOT_SUBSCRIBED_TO_GROUP)

        else:
            send_command(conn, NO_SUCH_CHANNEL)


def send_group_or_pv_message(account_id, conn, data):
    result = SEND_PV_OR_GROUP_REGEX.match(data)
    if result:
        group_or_user_id = result.group(1)
        msg_str = result.group(2)
        msg = Message(account_id, msg_str)
        grps = [x for x in groups if x.id == group_or_user_id]
        accs = [x for x in accounts if x.user_id == group_or_user_id]
        if len(grps) > 0:
            grp = grps[0]
            if account_id in grp.members:
                grp.messages.append(msg)
                send_command(conn, GROUP_MESSAGE_SUCCESS)
            else:
                send_command(conn, GROUP_WRITE_INVALID_PERMISSION)
        elif len(accs) > 0:
            acc = accs[0]
            key = tuple(sorted((account_id, acc.user_id)))
            if key not in private_messages.keys():
                private_messages[key] = []
            private_messages[key].append(msg)
            send_command(conn, PRIVATE_MESSAGE_SUCCESS)
        else:
            send_command(conn, NO_SUCH_GROUP_OR_USER)


def view_channel_message(account_id, conn, data):
    result = VIEW_CHANNEL_REGEX.match(data)
    if result:
        channel_id = result.group(1)
        chs = [x for x in channels if x.id == channel_id]
        if len(chs) > 0:
            channel = chs[0]
            if account_id in channel.members:
                send_all_message(conn, channel.messages)
            else:
                send_command(conn, NOT_SUBSCRIBED_TO_CHANNEL)

        else:
            send_command(conn, NO_SUCH_CHANNEL)


def send_channel_message(account_id, conn, data):
    result = SEND_CHANNEL_REGEX.match(data)
    if result:
        channel_id = result.group(1)
        chs = [x for x in channels if x.id == channel_id]
        if len(chs) > 0:
            channel = chs[0]
            msg_str = result.group(2)
            if account_id == channel.owner_id:
                msg = Message(account_id, msg_str)
                channel.messages.append(msg)
                send_command(conn, CHANNEL_MESSAGE_SUCCESS)
            else:
                send_command(conn, CHANNEL_WRITE_INVALID_PERMISSION)

        else:
            send_command(conn, NO_SUCH_CHANNEL)


def join_channel(account_id, conn, data):
    result = JOIN_CHANNEL_REGEX.match(data)
    if result:
        channel_id = result.group(1)
        chs = [x for x in channels if x.id == channel_id]
        if len(chs) > 0:
            if account_id in chs[0].members:
                send_command(conn, CHANNEL_ALREADY_JOINED)
            else:
                chs[0].members.append(account_id)
                send_command(conn, CHANNEL_JOIN)
        else:
            send_command(conn, NO_SUCH_CHANNEL)


def join_group(account_id, conn, data):
    result = JOIN_GROUP_REGEX.match(data)
    if result:
        group_id = result.group(1)
        grs = [x for x in groups if x.id == group_id]
        if len(grs) > 0:
            if account_id in grs[0].members:
                send_command(conn, GROUP_ALREADY_JOINED)
            else:
                grs[0].members.append(account_id)
                send_command(conn, GROUP_JOIN)
        else:
            send_command(conn, NO_SUCH_GROUP)


def create_channel(account_id, conn, data):
    result = CREATE_CHANNEL_REGEX.match(data)
    if result:
        channel_id = result.group(1)
        if is_unique_account(channel_id) and is_unique_group(channel_id) and is_unique_channel(channel_id):
            channel = Channel(channel_id, account_id)
            with channels_lock:
                channels.append(channel)
            send_command(conn, CHANNEL_CREATED)
        else:
            send_command(conn, ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST)


def create_group(account_id, conn, data):
    result = CREATE_GROUP_REGEX.match(data)
    if result:
        group_id = result.group(1)
        if is_unique_account(group_id) and is_unique_group(group_id) and is_unique_channel(group_id):
            group = Group(group_id, account_id)
            with groups_lock:
                groups.append(group)
            send_command(conn, GROUP_CREATED)
        else:
            send_command(conn, ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST)


# This function checks if an online user with that id exists or not. If it exists, request the client to enter another
# id It an account exist but it is not online, match them. Else create a new user.
# Also note that it also check uniqueness between channel and group ids.
def make_or_find_account(conn):
    need_to_repeat = True
    account_id = ""
    while need_to_repeat:
        send_command(conn, USER_ID_REQ)
        data = conn.recv(1024)
        if not data:
            conn.close()
        account_id = data.decode(ENCODING)
        # Uniqueness
        if is_unique_client(account_id) and is_unique_channel(account_id) and is_unique_group(account_id):
            need_to_repeat = False
        else:
            send_command(conn, ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST)

    # Check if account exist or need to be created.
    account_exist = False
    if not is_unique_account(account_id):
        account = [x for x in accounts if x.user_id == account_id][0]
        account_exist = True
    else:
        account = Account(account_id)
    with clients_lock:
        clients[account.user_id] = conn

    # If account doesn't exist, append it to 'accounts' list.
    if not account_exist:
        with accounts_lock:
            accounts.append(account)
    if not account_exist:
        send_command(conn, ACCOUNT_CREATE_SUCCESS)
    else:
        send_command(conn, CONNECTED_TO_ALREADY_EXIST_ACCOUNT)
    return account_id


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
