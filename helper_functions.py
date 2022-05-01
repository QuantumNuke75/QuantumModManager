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

#
# Sets a pak's load order.
#
def set_pak_load_order(main, name, category, num):

    if num < 0:
        num = 0

    if num > 99:
        num = 99

    dir = None
    if category == "None":
        if os.path.isfile(main.game_directory + "\\" + name):
            dir = main.game_directory + "\\" + name
        elif os.path.isfile(main.game_directory + "\\" + name + ".old"):
            dir = main.game_directory + "\\" + name + ".old"
    else:
        if os.path.isfile(main.game_directory + "\\" + category + "\\" + name):
            dir = main.game_directory + "\\" + category + "\\" + name
        elif os.path.isfile(main.game_directory + "\\" + category + "\\" + name + ".old"):
            dir = main.game_directory + "\\" + category + "\\" + name + ".old"

    if "pakchunk" in dir:
        split_dir = dir.split("pakchunk", 1)

        num_to_remove = 0
        for i in range(len(split_dir[1])):
            try:
                int(split_dir[1][i])
                num_to_remove += 1
            except:
                break

        split_dir[1] = split_dir[1][num_to_remove:]
        os.rename(dir, split_dir[0] + "pakchunk" + str(num) + split_dir[1])

    else:
        split_dir = dir.rsplit("\\", 1)
        os.rename(dir, split_dir[0] + "\\" + "pakchunk" + str(num) + split_dir[1])

#
# Gets a pak's load order.
#
def get_pak_load_order(name):
    try:
        return int("".join(filter(str.isdigit, name.replace("pakchunk", "")[0:3])))
    except:
        return 98


#
# Read the game path from bytes.
#
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

#
# Reads data from a pak file.
#
def read_file(stream):
    try:
        # With pak version 11.
        uasset_files = []
        stream.seek(-225, 2)
        footer_offset = stream.tell()
        footer = stream.read(225)
        key, index, magic, version, offset, size, hash, comp = st_unpack('< 20s c II QQ 20s 160s',footer)

        stream.seek(offset, 0)
        mount_point = read_path(stream, "utf-8")

        entry_count = st_unpack('<I', stream.read(4))[0]

        path_hash_seed = st_unpack('<Q', stream.read(8))[0]

        has_path_hash_index = st_unpack('<I', stream.read(4))[0]

        if has_path_hash_index != 0:
            has_path_index_offset = st_unpack('<Q', stream.read(8))[0]

            has_path_index_size = st_unpack('<Q', stream.read(8))[0]

            has_path_index_hash = st_unpack('<20s', stream.read(20))[0]

        has_full_directory_index = st_unpack('<I', stream.read(4))[0]

        if has_full_directory_index != 0:
            full_directory_index_offset = st_unpack('<Q', stream.read(8))[0]

            full_directory_index_size = st_unpack('<Q', stream.read(8))[0]

            full_directory_index_hash = st_unpack('<20s', stream.read(20))[0]

        encoded_entry_info_size = st_unpack('<I', stream.read(4))[0]

        encoded_entry_info  = st_unpack(f'<{encoded_entry_info_size}s', stream.read(encoded_entry_info_size))[0]

        file_count = st_unpack('<I', stream.read(4))[0]

        ######## INDEX RECORD ########
        directory_count = st_unpack('<I', stream.read(4))[0]


        stream.seek(full_directory_index_offset)

        total_items = st_unpack('<I', stream.read(4))[0]

        file_num = 0

        for i in range(directory_count):
            directory_name_size = st_unpack('<I', stream.read(4))[0]

            directory_name = st_unpack(f'<{directory_name_size}s', stream.read(directory_name_size))[0]

            file_count = st_unpack('<I', stream.read(4))[0]

            if file_num >= directory_count:
                break


            for j in range(file_count):
                file_name_size = st_unpack('<I', stream.read(4))[0]

                file_name = st_unpack(f'<{file_name_size}s', stream.read(file_name_size))[0]

                encoded_entry_offset = st_unpack('<I', stream.read(4))[0]
                file_num += 1

                if ".uasset" in file_name.decode("utf-8") or ".ini" in file_name.decode("utf-8"):
                    uasset_files.append(mount_point + directory_name.decode("utf-8").replace("\x00", "") + file_name.decode("utf-8").replace("\x00", ""))
    except Exception as e:
        ...

    return uasset_files

