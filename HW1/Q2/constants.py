import re

HOST = "127.0.0.1"
PORT = 5050
ENCODING = "ascii"

USER_ID_REQ = "USER_ID_REQ"
ACCOUNT_CREATE_SUCCESS = "ACCOUNT_CREATE_SUCCESS"
ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST = "ACCOUNT_ALREADY_EXIST"
CONNECTED_TO_ALREADY_EXIST_ACCOUNT = "CONNECTED_TO_ALREADY_EXIST_ACCOUNT"
CHANNEL_CREATED = "CHANNEL_CREATED"
GROUP_CREATED = "GROUP_CREATED"

CHANNEL_JOIN = "CHANNEL_JOIN"
GROUP_JOIN = "GROUP_JOIN"

GROUP_EXISTS = "GROUP_EXISTS"
CHANNEL_EXISTS = "CHANNEL_EXISTS"

CHANNEL_ALREADY_JOINED = "CHANNEL_ALREADY_JOINED"
GROUP_ALREADY_JOINED = "GROUP_ALREADY_JOINED"

NO_SUCH_GROUP = "NO_SUCH_GROUP"
NO_SUCH_CHANNEL = "NO_SUCH_CHANNEL"
NO_SUCH_USER = "NO_SUCH_USER"

CHANNEL_WRITE_INVALID_PERMISSION = "CHANNEL_WRITE_INVALID"

CHANNEL_MESSAGE_SUCCESS = "CHANNEL_MESSAGE_SUCCESS"

PRIVATE_MESSAGE_SUCCESS = "PRIVATE_MESSAGE_SUCCESS"
GROUP_MESSAGE_SUCCESS = "GROUP_MESSAGE_SUCCESS"

NOT_SUBSCRIBED_TO_CHANNEL = "NOT_SUBSCRIBED_TO_CHANNEL"
NOT_SUBSCRIBED_TO_GROUP = "NOT_SUBSCRIBED_TO_GROUP"
GROUP_WRITE_INVALID_PERMISSION = "GROUP_WRITE_INVALID_PERMISSION"

SEND_ALL_MESSAGE_PROTOCOL = "SEND_ALL_MESSAGE_PROTOCOL"

NO_SUCH_GROUP_OR_USER = "NO_SUCH_GROUP_OR_USER"
NO_PV_BETWEEN_THESE_USERS = "NO_PV_BETWEEN_THESE_USERS"

COMMANDS = {
    USER_ID_REQ: "85119eb367183645faaee4a424bbd86f749b1d4247697c2703ac447f4458902b",
    ACCOUNT_CREATE_SUCCESS: "6cc99eaf5d8f16a415acc95d469206ee87a66d9e7df3c2225a47d170c93c413b",
    ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST: "b020c5b3be4386521931600941abb47484fa506b5c3ebc1927f6513f02874561",
    CONNECTED_TO_ALREADY_EXIST_ACCOUNT: "6aa76e875a9952d0106b353a72affee94b111b07fe93d1e1a975121255562bce",
    CHANNEL_CREATED: "bcc3557a0d357554a01509ae9890780f76f148e7226ee0a4294267155b2ec51f",
    GROUP_CREATED: "a2c1fead20bb0e39e7887236d3b883682e2e06d25f8df27f01d6470ad043d43d",
    CHANNEL_JOIN: "5b80d5057b912f2ac52b3dbed60e1a2d0c93bd9def147b8536c1f6c83136af0c",
    GROUP_JOIN: "9d742670eee4a4fa1ff1fbfc85e83f31a51bde430fcd461c83588684b6c95e05",
    GROUP_EXISTS: "a00e3c392aa4cf74b18379d90caf9a4c7e112fa51045263260e49b06f0f2b4a4",
    CHANNEL_EXISTS: "c93aab01a7a08755d82015e9915b7d953635f9b001b28555d02ad314331c4cd6",
    CHANNEL_ALREADY_JOINED: "07eb5e1cb6c2e8d8219a0345828261aea1d5be1b065674c856a51aa85ca18574",
    GROUP_ALREADY_JOINED: "bdc6bfa69dfeac91f0689ddfa46d154dc9348b6edb1168e5fba37838473d2679",
    NO_SUCH_GROUP: "39f0ddff5461b28c16b866199e32f48bc30de5a52415db554bf6159ba22d382a",
    NO_SUCH_CHANNEL: "00ad0a2ae78661e42d320e2064dfc6c526610b9bbe3aefd065f7864b5975ddf3",
    CHANNEL_WRITE_INVALID_PERMISSION: "e95d976b767288ac23d9f0dfd9c421a0a8f73410134201a944eaa2b6578bc87b",
    CHANNEL_MESSAGE_SUCCESS: "8a2068b9a0929f28b8a34ff149cfb17df4d1d48b0a24592a55301a22d2aeccd5",
    NOT_SUBSCRIBED_TO_CHANNEL: "b21c2f6e8f367ac2c4efb601601a4cf170394e52606ea48f0134f998e5e052d9",
    SEND_ALL_MESSAGE_PROTOCOL: "d1e629d7d53dac8889393204c9fd740c6d5de3aa4bcb8fadbffc1915681c5cd8",
    NO_SUCH_GROUP_OR_USER: "6cfbad1137b4e2304f0abececc830508d190e881c3789c31e4c18edeed3ad834",
    GROUP_MESSAGE_SUCCESS: "a4461edd93b6f653cfe53198181a5a28c7d016fbbcc2fc69bfb955dbad5c0342",
    GROUP_WRITE_INVALID_PERMISSION: "af2e38eb4e4aac447860da4761ea2e2d7c5726a852bb1b1f181c8a0a05afdb4e",
    PRIVATE_MESSAGE_SUCCESS: "210bda5839a853c7d2e4c221372899efbbedd8bba86028099ecef52250cb01da",
    NOT_SUBSCRIBED_TO_GROUP: "a963492f666abc39186a7450e6d797064af1d1b43461ee3421e3a5d52844bc31",
    NO_SUCH_USER: "d0b2d7b070df1757da99523ad44e96022b8e569199335a9e47f735f3c67ec6e6",
    NO_PV_BETWEEN_THESE_USERS: "80181abc49e466d3ffe02c15f05d68dc85855ba65bb66a1757b7799c1bd2e20e"

}

USER_MSG = {
    USER_ID_REQ: "Please Enter an Id:",
    ACCOUNT_CREATE_SUCCESS: "Account Created Successfully",
    ACCOUNT_GROUP_CHANNEL_ALREADY_EXIST: "An account/group/channel with this id already exists!",
    CONNECTED_TO_ALREADY_EXIST_ACCOUNT: "Connected to an already existing account!",
    CHANNEL_CREATED: "Channel Created Successfully",
    GROUP_CREATED: "Group Created Successfully",
    CHANNEL_JOIN: "Joined Channel Successfully",
    GROUP_JOIN: "Joined Group Successfully",
    GROUP_EXISTS: "Group Already Exists",
    CHANNEL_EXISTS: "Channel Already Exists",
    CHANNEL_ALREADY_JOINED: "You've joined this channel before",
    GROUP_ALREADY_JOINED: "You've joined this group before",
    NO_SUCH_GROUP: "No group exists with that id.",
    NO_SUCH_CHANNEL: "No Channel Exists with that id",
    CHANNEL_WRITE_INVALID_PERMISSION: "You don't have permission to write to this channel",
    CHANNEL_MESSAGE_SUCCESS: "Channel Message posted successfully",
    NOT_SUBSCRIBED_TO_CHANNEL: "You are not subscribed to this channel",
    NO_SUCH_GROUP_OR_USER: "No Group or User with this id found",
    GROUP_MESSAGE_SUCCESS: "Group Message posted successfully",
    GROUP_WRITE_INVALID_PERMISSION: "You don't have permission to write to this group (maybe because you are not subscribed)!",
    PRIVATE_MESSAGE_SUCCESS: "Private Message Sent Successfully",
    NOT_SUBSCRIBED_TO_GROUP: "You are not subscribed to this group",
    NO_SUCH_USER: "No such user exist",
    NO_PV_BETWEEN_THESE_USERS: "No private Message between these two users"
}

CREATE_GROUP_REGEX = re.compile(r"^create group (\w+)$")
CREATE_CHANNEL_REGEX = re.compile(r"^create channel (\w+)$")
JOIN_GROUP_REGEX = re.compile(r"^join group (\w+)$")
JOIN_CHANNEL_REGEX = re.compile(r"^join channel (\w+)$")
SEND_PV_OR_GROUP_REGEX = re.compile(r"^send message to (\w+) '([^']+)'$")
SEND_CHANNEL_REGEX = re.compile(r"^send channel message to (\w+) '([^']+)'$")
VIEW_CHANNEL_REGEX = re.compile(r"^view channel (\w+)$")
VIEW_GROUP_REGEX = re.compile(r"^view group (\w+)$")
VIEW_PV_REGEX = re.compile(r"^view pv (\w+)$")
