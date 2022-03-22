import json, os, wx, win32api
import GlobalVariables
from ModManagerFrame import ModManager




main_frame = None

def main():
    # Read or Create Config
    if os.path.isfile("Settings.ini"):
        json_data = json.load(open("Settings.ini", "r"))
        GlobalVariables.game_directory = json_data["game_directory"]
    else:
        json_data = {}
        json_data["game_directory"] = ""
        json.dump(json_data, open("Settings.ini", "w"))

    main_app = wx.App()

    main.main_frame = ModManager(None)
    main.main_frame.Show()

    main_app.MainLoop()

if __name__ == '__main__':
    main()