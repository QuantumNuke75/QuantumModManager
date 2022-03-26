import os
import win32api


#
# Checks whether a mod is enabled or disabled.
#
def is_file_enabled(path, main):
    if os.path.isfile(main.game_directory + "\\" +path):
        return True
    elif os.path.isfile(main.game_directory + "\\" +path + ".old"):
        return False
    else:
        return False


#
# Enables a mod at a given path.
#
def enable_mod(path, main):
    if os.path.isfile(main.game_directory + "\\" + path + ".old"):
        os.rename(main.game_directory + "\\" + path + ".old", main.game_directory + "\\" + path)


#
# Disables a mod at a given path.
#
def disable_mod(path, main):
    if os.path.isfile(main.game_directory + "\\" + path):
        os.rename(main.game_directory + "\\" + path, main.game_directory + "\\" + path + ".old")


#
# Gets all the mods within the game directory.
#
def get_mods(main):
    temp = []
    with os.scandir(main.game_directory) as dirs:
        for dir in dirs:
            if dir.name != "pakchunk0-WindowsNoEditor.pak" and dir.name != "pakchunk0-WindowsNoEditor_0_P.pak":
                temp.append(dir.path)

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
        # Python suuuuucks...
        possible_game_path = [None]

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        for drive in drives:
            try:
                for file in os.scandir(drive):
                    if os.path.isdir(file.path) and "$" not in file.path:
                        find_folder(file.path,possible_game_path)
            except:
                continue
        return possible_game_path[0]


#
# Recursive function to find the Paks directory.
#
def find_folder(path, possible_game_path, depth=0):
        if possible_game_path[0] is not None:
            return

        try:
            for file in os.scandir(path):
                if os.path.isdir(file.path) and "$" not in file.path:
                    if file.name == "Steam" and os.path.isdir(file.path + "\\steamapps\\common\\Ready or Not\\ReadyOrNot"):
                        possible_game_path[0] = file.path + "\\steamapps\\common\\Ready or Not\\ReadyOrNot\\Content\\Paks"
                        return
                    if depth >= 3:
                        return
                    find_folder(file.path, possible_game_path, depth + 1)
        except:
            return
