import os

def init_users_file(token):
    f = open(f'data/{token}/users.txt', mode='w', encoding="utf-8")
    f.close()


def append_users_file(token, email, password):
    f = open(f'data/{token}/users.txt', mode='a', encoding="utf-8")
    f.write(email + " " + password + '\n')
    f.close()


def get_users_file(token):
    with open(f'data/{token}/users.txt', 'r', encoding="utf-8") as file:
        strings = file.readlines()
        usernames = []
        passwords = []
        for string in strings:
            splited_string = string.strip().split(" ")
            if len(splited_string) == 2:
                usrname, passwd = splited_string
            else:
                usrname = splited_string[0]
                passwd = ""
            usernames.append(usrname)
            passwords.append(passwd)
    return usernames, passwords


def init_selections_file(token, num_keys):
    f = open(f'data/{token}/selections.txt', mode='w')
    f.write(f"Number of candidates:{num_keys:5d}\n")
    f.close()


def append_selections_file(token):
    f = open(f'data/{token}/selections.txt', mode='r+')
    f.seek(21)
    size = int(f.read(5))
    f.seek(0, 2)  # back of file
    f.write("x" * size + '\n')
    f.close()


def edit_selections_file(token, usr_index, key_index):
    f = open(f'data/{token}/selections.txt', mode='r+')
    f.seek(21)
    size = int(f.read(5))
    f.seek(28 + (size + 2) * usr_index + key_index)
    char = f.read(1)
    f.seek(28 + (size + 2) * usr_index + key_index)
    if char == 'o':
        f.write('x')
    else:
        f.write('o')
    f.close()


def get_available(token, keys, usernames):
    with open(f'data/{token}/selections.txt', mode='r+') as csvfile:
        csvfile.seek(21)
        size = int(csvfile.read(5))
        csvfile.seek(28)

        options = ['' for _ in range(len(keys))]
        chars = csvfile.read(size+1)[:size]
        usr_index = 0
        while len(chars):
            for i, char in enumerate(chars):
                if char == "o":
                    options[i] += f",{usernames[usr_index]},"
            chars = csvfile.read(size+1)[:size]
            usr_index += 1

        temp = {}
        for i in range(len(keys)):
            temp[keys[i]] = options[i]
        options = temp
    return options


def init_config_file(token, eventTitle, keys, voteCat, customCandidates):
    with open(f'data/{token}/config.txt', mode='w', encoding="utf-8") as file:
        file.write('eventTitle\n')
        file.write(f'{eventTitle}\n')
        file.write('candidates\n')
        file.write(f'{",".join(keys)}\n')
        if voteCat != "":
            file.write(f'{voteCat}\n')
            file.write(f'{",".join(customCandidates)}\n')



def get_config_file(token):
    with open(f'data/{token}/config.txt', 'r', encoding="utf-8") as file:
        lines = file.readlines()
        eventTitle = lines[1].strip()
        keys = lines[3].strip().split(',')
        if len(lines) > 4:
            voteCat = lines[4].strip()
            customCandidates = lines[5].strip().split(',')
        else:
            voteCat = ""
            customCandidates = []

    return eventTitle, keys, voteCat, customCandidates




def init_custom_selections_file(token, num_keys):
    f = open(f'data/{token}/custom_selections.txt', mode='w')
    f.write(f"Number of candidates:{num_keys:5d}\n")
    f.close()


def append_custom_selections_file(token):
    if not os.path.exists(f'data/{token}/custom_selections.txt'):
        return
    f = open(f'data/{token}/custom_selections.txt', mode='r+')
    f.seek(21)
    size = int(f.read(5))
    f.seek(0, 2)  # back of file
    f.write("x" * size + '\n')
    f.close()


def edit_custom_selections_file(token, usr_index, key_index):
    f = open(f'data/{token}/custom_selections.txt', mode='r+')
    f.seek(21)
    size = int(f.read(5))
    f.seek(28 + (size + 2) * usr_index + key_index)
    char = f.read(1)
    f.seek(28 + (size + 2) * usr_index + key_index)
    if char == 'o':
        f.write('x')
    else:
        f.write('o')
    f.close()


def get_custom_available(token, keys, usernames):
    with open(f'data/{token}/custom_selections.txt', mode='r+') as csvfile:
        csvfile.seek(21)
        size = int(csvfile.read(5))
        csvfile.seek(28)

        options = ['' for _ in range(len(keys))]
        chars = csvfile.read(size+1)[:size]
        usr_index = 0
        while len(chars):
            for i, char in enumerate(chars):
                if char == "o":
                    options[i] += f",{usernames[usr_index]},"
            chars = csvfile.read(size+1)[:size]
            usr_index += 1

        temp = {}
        for i in range(len(keys)):
            temp[keys[i]] = options[i]
        options = temp
    return options
