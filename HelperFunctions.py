import os

import win32api

import GlobalVariables


def is_file_enabled(path):
    if os.path.isfile(GlobalVariables.game_directory + "\\" +path):
        return True
    elif os.path.isfile(GlobalVariables.game_directory + "\\" +path + ".old"):
        return False
    else:
        return False


def enable_mod(path):
    if os.path.isfile(GlobalVariables.game_directory + "\\" + path + ".old"):
        os.rename(GlobalVariables.game_directory + "\\" + path + ".old", GlobalVariables.game_directory + "\\" + path)


def disable_mod(path):
    if os.path.isfile(GlobalVariables.game_directory + "\\" + path):
        os.rename(GlobalVariables.game_directory + "\\" + path, GlobalVariables.game_directory + "\\" + path + ".old")


def get_mods():
    temp = []
    with os.scandir(GlobalVariables.game_directory) as dirs:
        for dir in dirs:
            if dir.name != "pakchunk0-WindowsNoEditor.pak" and dir.name != "pakchunk0-WindowsNoEditor_0_P.pak":
                temp.append(dir.path)

    return [x for x in temp if ".pak" in x]


def get_profiles():
    path = r"Profiles"
    temp = []
    with os.scandir(path) as dirs:
        for dir in dirs:
            if ".json" in dir.name:
                temp.append(dir.name.split(".")[0])
    return temp


def refresh_mods():

    GlobalVariables.mods_list.clear()
    mods = get_mods();

    for mod in mods:
        name = mod.split("\\")[-1].split("-")[1].split(".")[0].replace("_P", "").replace("Mods_", "").replace("_", " ")
        path = mod.replace(".old", "")
        GlobalVariables.mods_list.append( (name, str(round(os.path.getsize(mod)/1000000, 2)) + " MB", path.split("\\")[-1]) )

    GlobalVariables.mod_selector.DeleteAllItems()

    idx = 0
    for i in GlobalVariables.mods_list:

        index = GlobalVariables.mod_selector.InsertItem(idx, i[0])
        GlobalVariables.mod_selector.SetItem(index, 1, str(i[1]))
        GlobalVariables.mod_selector.SetItem(index, 2, str(i[2]))

        # If the file is enabled.
        if is_file_enabled(i[2]):
            GlobalVariables.mod_selector.CheckItem(index)
        idx += 1


def refresh_profiles():
    GlobalVariables.profile_selector.DeleteAllItems()
    idx = 0
    for i in get_profiles():
        index = GlobalVariables.profile_selector.InsertItem(idx, i)
        idx += 1






def select_new_game_path():
    ...


def get_steam_dir():
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        for drive in drives:
            for file in os.scandir(drive):
                if os.path.isdir(file.path) and "$" not in file.path:
                    find_folder(file.path)


def find_folder(path, depth=0):
        if GlobalVariables.possible_game_path is not None:
            return

        try:
            for file in os.scandir(path):
                if os.path.isdir(file.path) and "$" not in file.path:
                    if file.name == "Steam":
                        if os.path.isdir(file.path + "\\steamapps\\common\\Ready or Not\\ReadyOrNot"):
                            GlobalVariables.possible_game_path = file.path + "\\steamapps\\common\\Ready or Not\\ReadyOrNot\\Content\\Paks"
                            return
                    if depth >= 3:
                        return
                    find_folder(file.path, depth + 1)
        except:
            return