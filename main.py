import json, os, wx
from mod_manager_frame import ModManager

class Main:

    def __init__(self):

        # Read or Create Config
        if os.path.isfile("Settings.ini"):
            json_data = json.load(open("Settings.ini", "r"))
            self.game_directory = json_data["game_directory"]
        else:
            json_data = {}
            json_data["game_directory"] = None
            self.game_directory = None
            json.dump(json_data, open("Settings.ini", "w"))

        main_app = wx.App()

        self.main_frame = ModManager(None, wx.ID_ANY, "")
        main_app.SetTopWindow(self.main_frame)
        self.main_frame.set_main(self)
        self.main_frame.Show()
        self.main_frame.Center()

        main_app.MainLoop()

Main()