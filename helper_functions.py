import os, winreg, io
from struct import unpack as st_unpack

#
# Checks whether a mod is enabled or disabled.
#
def is_file_enabled(path, category, main):

    new_category = "" if category == "None" else "\\" + category

    if os.path.isfile(main.game_directory + new_category + "\\" +path):
        return True
    elif os.path.isfile(main.game_directory + new_category + "\\" +path + ".old"):
        return False
    else:
        return False


#
# Enables a mod at a given path.
#
def enable_mod(path, category, main):
    if category == "None":
        if os.path.isfile(main.game_directory + "\\" + path + ".old"):
            os.rename(main.game_directory + "\\" + path + ".old", main.game_directory + "\\" + path)
    else:
        if os.path.isfile(main.game_directory + "\\" + category + "\\" + path + ".old"):
            os.rename(main.game_directory + "\\" + category + "\\" + path + ".old", main.game_directory + "\\" + category + "\\" + path)


#
# Disables a mod at a given path.
#
def disable_mod(path, category, main):
    if category == "None":
        if os.path.isfile(main.game_directory + "\\" + path):
            os.rename(main.game_directory + "\\" + path, main.game_directory + "\\" + path + ".old")
    else:
        if os.path.isfile(main.game_directory + "\\" + category + "\\" + path):
            os.rename(main.game_directory + "\\" + category + "\\" + path, main.game_directory + "\\" + category + "\\" + path + ".old")


#
# Deletes a mod at a given path.
#
def delete_mod(path, category, main):
    if category == "None":
        if os.path.isfile(main.game_directory + "\\" + path):
            os.remove(main.game_directory + "\\" + path)
        elif os.path.isfile(main.game_directory + "\\" + path + ".old"):
            os.remove(main.game_directory + "\\" + path + ".old")
    else:
        if os.path.isfile(main.game_directory + "\\" + category + "\\" + path):
            os.remove(main.game_directory + "\\" + category + "\\" + path)
        elif os.path.isfile(main.game_directory + "\\" + category + "\\" + path + ".old"):
            os.remove(main.game_directory + "\\" + category + "\\" + path + ".old")


#
# Gets all the mods within the game directory.
#
def get_mods(main):
    temp = []
    with os.scandir(main.game_directory) as dirs:
        for dir in dirs:
            if dir.name != "pakchunk0-WindowsNoEditor.pak" and dir.name != "pakchunk0-WindowsNoEditor_0_P.pak":
                temp.append(dir.path)
            if os.path.isdir(dir.path):
                for item in os.scandir(dir.path):
                    temp.append(item.path)

    return [x for x in temp if ".pak" in x]


#
# Gets all the profiles in the `Profiles` directory.
#
def get_profiles():
    path = r"Profiles"
    temp = []

    if not os.path.exists("Profiles"):
        os.mkdir("Profiles")

    with os.scandir(path) as dirs:
        for dir in dirs:
            if ".json" in dir.name:
                temp.append(dir.name.split(".")[0])
    return temp


#
# Get the Pak directory of Ready or Not.
#
def get_steam_dir():
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path = winreg.QueryValueEx(hkey, "InstallPath")
        except:
            return None

        lib_fold_file = open(steam_path[0] + "\\steamapps\\libraryfolders.vdf", "r")
        possible_paths = []
        for line in lib_fold_file.readlines():
            if "path" in line:
                possible_paths.append(line.replace("\n", "").split('"')[3])
        for path in possible_paths:
            if os.path.isdir(path + "\\steamapps\\common\\Ready or Not\\ReadyOrNot"):
                return path + "\\steamapps\\common\\Ready or Not\\ReadyOrNot\\Content\\Paks"
        return None

def read_path(stream: io.BufferedReader, encoding: str = 'utf-16') -> str:
    try:
        path_len, = st_unpack('<i',stream.read(4))
        if path_len < 0:
            # in at least some format versions, this indicates a UTF-16 path
            path_len = -2 * path_len
            encoding = 'iso-8859-1'
        return stream.read(path_len).decode(encoding).rstrip('\0').replace('/',os.path.sep)
    except:
        return

def read_index(stream):

    stream.seek(-226, 2)
    footer_offset = stream.tell()
    footer = stream.read(226)
    #magic, version, index_offset, index_size, index_sha1 = st_unpack('<iiqq20s',footer)
    #unpacked = st_unpack('<IIQQ20s',footer)
    key, index, magic, version, offset, size, hash, comp = st_unpack('< 20s h ii qq 20s 160s',footer)

    stream.seek(offset, 0)
    mount_point = read_path(stream, "utf-8")
    entry_count = st_unpack('<I', stream.read(4))[0]

    uncleaned_file_names = []

    for i in range(entry_count):
        if stream.tell() > footer_offset:
            break

        filename = read_path(stream, "iso-8859-1")
        if ".uasset" in filename:
            uncleaned_file_names.append(filename.replace("\x00", ""))

    return uncleaned_file_names


def get_completely_clean_name(string):
    allowed_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_./"
    index = len(string)-1
    try:
        while string[index] in allowed_list:
            index -= 1
        return string[index+1:] + ".uasset"
    except:
        return string[1:] + ".uasset"

