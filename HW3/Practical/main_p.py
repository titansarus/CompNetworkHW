from models_p import AS, LinkedAS, Link, ROLES

links_2 = [
    {
        "first": {"as_number": "0", "role": ROLES.PROVIDER},
        "second": {"as_number": "1", "role": ROLES.COSTUMER}
    },
    {
        "first": {"as_number": "1", "role": ROLES.PEER},
        "second": {"as_number": "2", "role": ROLES.PEER}
    },
    {
        "first": {"as_number": "1", "role": ROLES.PEER},
        "second": {"as_number": "3", "role": ROLES.PEER}
    },
    {
        "first": {"as_number": "2", "role": ROLES.PEER},
        "second": {"as_number": "3", "role": ROLES.PEER}
    },
    {
        "first": {"as_number": "2", "role": ROLES.COSTUMER},
        "second": {"as_number": "4", "role": ROLES.PROVIDER}
    },
    {
        "first": {"as_number": "2", "role": ROLES.COSTUMER},
        "second": {"as_number": "5", "role": ROLES.PROVIDER}
    },
    {
        "first": {"as_number": "3", "role": ROLES.COSTUMER},
        "second": {"as_number": "4", "role": ROLES.PROVIDER}
    },
    {
        "first": {"as_number": "4", "role": ROLES.COSTUMER},
        "second": {"as_number": "5", "role": ROLES.PROVIDER}
    },
]
AS_MAP_2 = {
    "0": {
        "ips": [
            "6.0.0.0/8",
        ]
    },
    "1": {
        "ips": [
            "1.0.0.0/8",
        ]
    },
    "2": {
        "ips": [
            "2.0.0.0/8",
            "22.0.0.0/8",
            "222.0.0.0/8",
        ]
    },
    "3": {
        "ips": [
            "3.0.0.0/8",
            "33.0.0.0/8",
        ]
    },
    "4": {
        "ips": [
            "4.0.0.0/8",
        ]
    },
    "5": {
        "ips": [
            "5.0.0.0/8",
        ]
    },
}

commands_2_1 = [
    "AS 0:auto advertise on",
    "AS 1:auto advertise on",
    "AS 2:auto advertise on",
    "AS 3:auto advertise on",
    "AS 4:auto advertise on",
    "AS 5:auto advertise on",
    "AS 4:advertise self",
    "AS 0:advertise self",
    "AS 1:advertise self",
    "AS 2:advertise self",
    "AS 3:advertise self",
    "AS 5:advertise self",
    "AS 0:get route 33.0.0.0/8",
    "AS 0:hijack 5.0.0.0/8",
    "AS 3:withdrawn 33.0.0.0/8",
    "AS 0:get route 33.0.0.0/8",
]

commands_2_2 = [
    "AS 0:auto advertise on",
    "AS 1:auto advertise on",
    "AS 2:auto advertise on",
    "AS 3:auto advertise on",
    "AS 4:auto advertise on",
    "AS 5:auto advertise on",
    "AS 4:advertise self",
    "AS 0:advertise self",
    "AS 1:advertise self",
    "AS 2:advertise self",
    "AS 3:advertise self",
    "AS 5:advertise self",
    "AS 0:get route 5.0.0.0/8",
    "AS 2:get route 5.0.0.0/8",
    "link delete 2 5",
    "AS 0:get route 5.0.0.0/8",
    "AS 2:get route 5.0.0.0/8",
    "link create 2 5 COSTUMER PROVIDER",
    "AS 0:get route 5.0.0.0/8",
    "AS 2:get route 5.0.0.0/8",
]

commands_2_3 = [
    "AS 0:auto advertise on",
    "AS 1:auto advertise on",
    "AS 3:auto advertise on",
    "AS 4:auto advertise on",
    "AS 5:auto advertise on",
    "AS 4:advertise self",
    "AS 0:advertise self",
    "AS 1:advertise self",
    "AS 2:advertise self",
    "AS 3:advertise self",
    "AS 5:advertise self",
    "AS 0:get route 5.0.0.0/8",
    "AS 2:get route 5.0.0.0/8",
    "AS 2:advertise all",
    "AS 0:get route 5.0.0.0/8",
    "AS 2:get route 5.0.0.0/8",
]

def run(AS_MAP, links, commands):
    AS_dictionary = dict()
    for as_number in AS_MAP.keys():
        AS_dictionary[int(as_number)] = AS(int(as_number), owned_ips=AS_MAP.get(as_number).get("ips"))

    for link in links:
        first_as_number = int(link.get("first").get("as_number"))
        first_role = link.get("first").get("role")
        second_as_number = int(link.get("second").get("as_number"))
        second_role = link.get("second").get("role")
        create_link(AS_dictionary, first_as_number, first_role, second_as_number, second_role)
    print("Initializing finished.")

    for command in commands:
        if command.startswith("link delete"):
            first_as_number, second_as_number = command.split()[2:]
            AS_dictionary[int(first_as_number)].command_handler("link delete " + second_as_number)
            AS_dictionary[int(second_as_number)].command_handler("link delete " + first_as_number)
        elif command.startswith("link create"):
            first_as_number, second_as_number, first_role, second_role = command.split()[2:]
            create_link(AS_dictionary, int(first_as_number), ROLES[first_role], int(second_as_number),
                        ROLES[second_role])
            AS_dictionary[int(first_as_number)].command_handler("link create " + second_as_number)
            AS_dictionary[int(second_as_number)].command_handler("link create " + first_as_number)
            pass
        else:
            as_number = int(command.split(":")[0].split()[1])
            ASa = AS_dictionary[as_number]
            ASa.command_handler(command.split(":")[1])


def create_link(AS_dictionary, first_as_number, first_role, second_as_number, second_role):
    first_as = AS_dictionary[first_as_number]
    second_as = AS_dictionary[second_as_number]
    l = Link(first_as, second_as)
    first_as.add_link(LinkedAS(second_as_number, first_as_number, l, first_role))
    second_as.add_link(LinkedAS(first_as_number, second_as_number, l, second_role))


print("test 1")
run(AS_MAP_2, links_2, commands_2_1)
print("\n\ntest 2")
run(AS_MAP_2, links_2, commands_2_2)
print("\n\ntest 3")
run(AS_MAP_2, links_2, commands_2_3)

