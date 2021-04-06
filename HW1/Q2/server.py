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


def id_exist_in_list(id, array):
    for x in array:
        if x.id == id:
            return True
    return  False


def client_exists(id):
    return id in clients


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
            view_channel_message(account_id, conn, data)
            send_group_or_pv_message(account_id, conn, data)
            view_group_message(account_id, conn, data)
            view_private_message(account_id, conn, data)
    except:
        with clients_lock:
            clients.pop(account_id)
    conn.close()


def send_group_or_pv_message(account_id, conn, data):
    result = SEND_PV_OR_GROUP_REGEX.match(data)
    if result:
        group_user_channel_id = result.group(1)
        msg_str = result.group(2)
        msg = Message(account_id, msg_str)
        if id_exist_in_list(group_user_channel_id, groups):
            send_group_msg(account_id, conn, group_user_channel_id, msg)
        elif id_exist_in_list(group_user_channel_id, accounts):
            send_private_message(account_id, conn, group_user_channel_id, msg)
        elif id_exist_in_list(group_user_channel_id, channels):
            send_channel_message(account_id, conn, group_user_channel_id, msg)
        else:
            send_command(conn, NO_SUCH_GROUP_OR_USER_OR_CHANNEL)


def send_channel_message(account_id, conn, channel_id, msg):
    channel = [x for x in channels if x.id == channel_id][0]
    if account_id == channel.owner_id:
        channel.messages.append(msg)
        send_command(conn, CHANNEL_MESSAGE_SUCCESS)
    else:
        send_command(conn, CHANNEL_WRITE_INVALID_PERMISSION)


def send_private_message(account_id, conn, another_account_id, msg):
    acc = [x for x in accounts if x.id == another_account_id][0]
    key = tuple(sorted((account_id, acc.id)))
    if key not in private_messages.keys():
        private_messages[key] = []
    private_messages[key].append(msg)
    send_command(conn, PRIVATE_MESSAGE_SUCCESS)


def send_group_msg(account_id, conn, group_id, msg):
    grp = [x for x in groups if x.id == group_id][0]
    if account_id in grp.members:
        grp.messages.append(msg)
        send_command(conn, GROUP_MESSAGE_SUCCESS)
    else:
        send_command(conn, GROUP_WRITE_INVALID_PERMISSION)


def view_util(account_id, conn, data, regex_pattern, arr, not_sub_cmd, not_exist_cmd):
    result = regex_pattern.match(data)
    if result:
        id = result.group(1)
        if id_exist_in_list(id, arr):
            ele = [x for x in arr if x.id == id][0]
            if account_id in ele.members:
                send_all_message(conn, ele.messages)
            else:
                send_command(conn, not_sub_cmd)

        else:
            send_command(conn, not_exist_cmd)


def view_group_message(account_id, conn, data):
    view_util(account_id, conn, data, VIEW_GROUP_REGEX, groups, NOT_SUBSCRIBED_TO_GROUP, NO_SUCH_GROUP)


def view_channel_message(account_id, conn, data):
    view_util(account_id, conn, data, VIEW_CHANNEL_REGEX, channels, NOT_SUBSCRIBED_TO_CHANNEL, NO_SUCH_CHANNEL)


def view_private_message(account_id, conn, data):
    result = VIEW_PV_REGEX.match(data)
    if result:
        acc_id = result.group(1)
        if id_exist_in_list(acc_id, accounts):
            acc = [x for x in accounts if x.id == acc_id][0]
            key = tuple(sorted((account_id, acc.id)))
            if key in private_messages:
                send_all_message(conn, private_messages[key])
            else:
                send_command(conn, NO_PV_BETWEEN_THESE_USERS)
        else:
            send_command(conn, NO_SUCH_USER)


def join_util(account_id, conn, data, regex_pattern, arr, already_join_cmd, success_cmd, not_exist_cmd):
    result = regex_pattern.match(data)
    if result:
        id = result.group(1)
        if id_exist_in_list(id, arr):
            ele = [x for x in arr if x.id == id][0]
            if account_id in ele.members:
                send_command(conn, already_join_cmd)
            else:
                ele.members.append(account_id)
                send_command(conn, success_cmd)
        else:
            send_command(conn, not_exist_cmd)


def join_channel(account_id, conn, data):
    join_util(account_id, conn, data, JOIN_CHANNEL_REGEX, channels, CHANNEL_ALREADY_JOINED, CHANNEL_JOIN,
              NO_SUCH_CHANNEL)


def join_group(account_id, conn, data):
    join_util(account_id, conn, data, JOIN_GROUP_REGEX, groups, GROUP_ALREADY_JOINED, GROUP_JOIN, NO_SUCH_GROUP)


def create_channel(account_id, conn, data):
    result = CREATE_CHANNEL_REGEX.match(data)
    if result:
        channel_id = result.group(1)
        if not id_exist_in_list(channel_id, accounts) and not id_exist_in_list(channel_id, groups) \
                and not id_exist_in_list(channel_id, channels):
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
        if not id_exist_in_list(group_id, accounts) and not id_exist_in_list(group_id, groups) and not id_exist_in_list(
                group_id, channels):
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
        if not client_exists(account_id) and not id_exist_in_list(account_id, channels) and not id_exist_in_list(
                account_id, groups):
            need_to_repeat = False
        else:
            send_command(conn, ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST)

    # Check if account exist or need to be created.
    account_exist = False
    if id_exist_in_list(account_id, accounts):
        account = [x for x in accounts if x.id == account_id][0]
        account_exist = True
    else:
        account = Account(account_id)
    with clients_lock:
        clients[account.id] = conn

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
