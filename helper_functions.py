import os
import win32api
import winreg, sys


#
# Checks whether a mod is enabled or disabled.
#
def is_file_enabled(path, category, main):

    category = "" if category is None else category

    if os.path.isfile(main.game_directory + "\\" + category + "\\" +path):
        return True
    elif os.path.isfile(main.game_directory + "\\" + category + "\\" +path + ".old"):
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
