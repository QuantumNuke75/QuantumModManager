import json, os, wx, requests, webbrowser
import wx.grid

import helper_functions


class CheckListCtrl(wx.ListCtrl):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.EnableCheckBoxes(True)

class NoCheckListCtrl(wx.ListCtrl):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.EnableCheckBoxes(False)

class ModFileDrop(wx.FileDropTarget):

    def __init__(self, window, mod_manager):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.mod_manager = mod_manager

    def OnDropFiles(self, x, y, filenames):

        for filename in filenames:
            # # If the file is a compressed file, extract all the .paks and add them to the Pak directory.
            # if filename.endswith(".zip") or filename.endswith(".7z") or filename.endswith(".rar"):
            #
            #     # Make temp folder.
            #     if not os.path.isdir("temp"):
            #         os.mkdir("temp")
            #     patoolib.extract_archive(filename, outdir="temp")
            #
            #     # Get all files in folders and subfolders.
            #     file_list = list()
            #     for (dir, dir_names, file_names) in os.walk("temp"):
            #         file_list += [os.path.join(dir, file) for file in file_names]
            #
            #     # For each file, if it's a .pak file, move it the Paks folder.
            #     for file in file_list:
            #         if file.endswith(".pak"):
            #             if os.path.isfile(self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1]):
            #                 os.remove(self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1])
            #             os.rename(file, self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1])
            #
            #     # Delete everything in temp folder.
            #     for file in os.scandir("temp"):
            #         os.remove(file)
            #

            # If the file is a .pak file, add it to the Pak directory.
            if filename.endswith(".pak"):
                if os.path.isfile(self.mod_manager.main.game_directory + "\\" + filename.split("\\")[-1]):
                    os.remove(self.mod_manager.main.game_directory + "\\" + filename.split("\\")[-1])
                os.rename(filename, self.mod_manager.main.game_directory + "\\" + filename.split("\\")[-1])

        self.mod_manager.refresh_mods()

        return True


class ModManager(wx.Frame):

    def __init__(self, main, *args, **kw):
        super(ModManager, self).__init__(size=(740, 500),*args, **kw)

        self.main = main
        self.current_version = 1.5

        panel = wx.Panel(self)

        # Set Font
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        vbox = wx.BoxSizer(wx.VERTICAL)
        outer_horz = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel)
        rightPanel = wx.Panel(panel)

        #self.log = wx.TextCtrl(rightPanel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.mod_selector = CheckListCtrl(rightPanel)
        self.mod_selector.InsertColumn(0, 'Mod', width=140)
        self.mod_selector.InsertColumn(1, 'Size')
        self.mod_selector.InsertColumn(2, 'Full Name')

        self.mod_selector.SetDropTarget(ModFileDrop(rightPanel, self))


        self.profile_selector = NoCheckListCtrl(rightPanel)
        self.profile_selector.InsertColumn(0, 'Profile')
        self.profile_selector.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ProfileClick)

        #
        # Left Panel
        #

        left_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        #
        # Mod Settings
        #
        mod_settings_sizer = wx.BoxSizer(wx.VERTICAL)

        select_all_mod = wx.Button(leftPanel, label='Select All')
        deselect_all_mod = wx.Button(leftPanel, label='Deselect All')
        refresh_mod = wx.Button(leftPanel, label='Refresh')
        apply_mod = wx.Button(leftPanel, label='Apply Changes')
        game_path_button = wx.Button(leftPanel, label='Change Game Path')
        run_ready_or_not = wx.Button(leftPanel, label='Run Ready or Not')

        select_all_mod.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        deselect_all_mod.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        refresh_mod.Bind(wx.EVT_BUTTON, self.OnRefresh)
        apply_mod.Bind(wx.EVT_BUTTON, self.OnApply)
        game_path_button.Bind(wx.EVT_BUTTON, self.ChangeGamePath)
        run_ready_or_not.Bind(wx.EVT_BUTTON, self.RunReadyOrNot)


        mod_settings_sizer.Add(select_all_mod, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(deselect_all_mod, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(refresh_mod, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(apply_mod, flag=wx.ALIGN_CENTER)

        mod_settings_sizer.Add((-1, 25))

        mod_settings_sizer.Add(game_path_button, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(run_ready_or_not, flag=wx.ALIGN_CENTER)


        #
        # Profile Settings
        #
        panel_settings_sizer = wx.BoxSizer(wx.VERTICAL)

        # select_all_mod = wx.Button(leftPanel, label='Select All')
        # deselect_all_mod = wx.Button(leftPanel, label='Deselect All')
        # refresh_mod = wx.Button(leftPanel, label='Refresh')
        # apply_mod = wx.Button(leftPanel, label='Apply Changes')
        # game_path_button = wx.Button(leftPanel, label='Change Game Path')
        #
        # select_all_mod.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        # deselect_all_mod.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        # refresh_mod.Bind(wx.EVT_BUTTON, self.OnRefresh)
        # apply_mod.Bind(wx.EVT_BUTTON, self.OnApply)
        # game_path_button.Bind(wx.EVT_BUTTON, self.ChangeGamePath)
        #
        #
        # panel_settings_sizer.Add(select_all_mod, flag=wx.ALIGN_CENTER)
        # panel_settings_sizer.Add(deselect_all_mod, flag=wx.ALIGN_CENTER)
        # panel_settings_sizer.Add(refresh_mod, flag=wx.ALIGN_CENTER)
        # panel_settings_sizer.Add(game_path_button, flag=wx.ALIGN_CENTER)
        # panel_settings_sizer.Add(apply_mod, flag=wx.ALIGN_CENTER)


        left_panel_sizer.Add(mod_settings_sizer, proportion=1)
        left_panel_sizer.Add(panel_settings_sizer, proportion=1)

        leftPanel.SetSizer(left_panel_sizer)

        #
        # Right Panel
        #
        vbox.Add(self.mod_selector, 4, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))

        vbox.Add(wx.StaticText(rightPanel, label="Profiles"))
        vbox.Add(self.profile_selector, 4, wx.EXPAND | wx.BOTTOM, 3)

        #
        # Profile Buttons
        #
        profile_options = wx.BoxSizer(wx.HORIZONTAL)
        self.load_profile = wx.Button(rightPanel, label="Load Profile")
        self.save_profile = wx.Button(rightPanel, label="Save Profile")
        self.delete_profile = wx.Button(rightPanel, label="Delete Profile")
        self.profile_textctrl = wx.TextCtrl(rightPanel)
        self.load_profile.Bind(wx.EVT_BUTTON, self.LoadProfile)
        self.save_profile.Bind(wx.EVT_BUTTON, self.SaveProfile)
        self.delete_profile.Bind(wx.EVT_BUTTON, self.DeleteProfile)

        profile_options.Add(self.load_profile)
        profile_options.Add(self.save_profile)
        profile_options.Add(self.delete_profile)
        profile_options.Add(self.profile_textctrl, proportion=1)


        vbox.Add(profile_options, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5)

        #
        # Version Warning
        #
        warning_pane = wx.BoxSizer(wx.HORIZONTAL)
        response = None
        try:
            response = requests.get('https://unofficial-modding-guide.com/tools.html')
        except:
            ...
        if response is not None and str(response.reason) == "OK":
            version = float(str(response.content).split("Quantum Mod Manager")[1][2:5])
            if version > self.current_version:
                self.warning_message = wx.StaticText(rightPanel, label = "Version Outdated: https://unofficial-modding-guide.com/downloads/QuantumModManager.exe")
                self.warning_button = wx.Button(rightPanel, label="Download")

                self.warning_button.Bind(wx.EVT_BUTTON, self.OpenWebPage)

                warning_pane.Add(self.warning_message, flag=wx.TOP, border=7)
                warning_pane.Add(self.warning_button, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, border=5)

        vbox.Add(warning_pane, flag=wx.EXPAND)

        rightPanel.SetSizer(vbox)

        # Add left and right panels to main sizer
        outer_horz.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        outer_horz.Add(rightPanel, 1, wx.EXPAND)
        outer_horz.Add((3, -1))

        # Add main sizer to main panel
        panel.SetSizer(outer_horz)

        # Final window changes
        self.SetTitle('Quantum Mod Manager')
        self.Centre()

        # If the game directory is not set.
        if self.main.game_directory is None or self.main.game_directory == "":
            possible_path = helper_functions.get_steam_dir()

            if possible_path is None:
                self.ChangeGamePath(None)
            else:
                self.main.game_directory = possible_path
                json_data = {}
                json_data["game_directory"] = self.main.game_directory
                json.dump(json_data, open("Settings.ini", "w"))

        if self.main.game_directory == None:
            quit()

        # Refresh all mods and profiles.
        self.refresh_mods()
        self.refresh_profiles()


    def refresh_mods(self):
        mods_list = []

        mods_list.clear()
        mods = helper_functions.get_mods(self.main);

        for mod in mods:
            name = mod.split("\\")[-1].split("-")[1].split(".")[0].replace("_P", "").replace("Mods_", "").replace("_",
                                                                                                                  " ")
            path = mod.replace(".old", "")
            mods_list.append((name, str(round(os.path.getsize(mod) / 1000000, 2)) + " MB", path.split("\\")[-1]))

        self.mod_selector.DeleteAllItems()

        idx = 0
        for i in mods_list:

            index = self.mod_selector.InsertItem(idx, i[0])
            self.mod_selector.SetItem(index, 1, str(i[1]))
            self.mod_selector.SetItem(index, 2, str(i[2]))

            # If the file is enabled.
            if helper_functions.is_file_enabled(i[2], self.main):
                self.mod_selector.CheckItem(index)
            idx += 1

    def refresh_profiles(self):
        self.profile_selector.DeleteAllItems()
        idx = 0
        for i in helper_functions.get_profiles():
            index = self.profile_selector.InsertItem(idx, i)
            idx += 1


    #
    # Interact Events
    #
    def OnSelectAll(self, event):

        num = self.mod_selector.GetItemCount()
        for i in range(num):
            self.mod_selector.CheckItem(i)


    def OnDeselectAll(self, event):

        num = self.mod_selector.GetItemCount()
        for i in range(num):
            self.mod_selector.CheckItem(i, False)


    def OnApply(self, event):

        num = self.mod_selector.GetItemCount()

        for i in range(num):

            if self.mod_selector.IsItemChecked(i):
                helper_functions.enable_mod(self.mod_selector.GetItemText(i, 2), self.main)
            else:
                helper_functions.disable_mod(self.mod_selector.GetItemText(i, 2), self.main)


    def LoadProfile(self, event):
        profile_name = self.profile_textctrl.GetValue()
        if profile_name == "":
            return

        self.refresh_mods()

        file = open("Profiles\\" + profile_name + ".json", "r")
        enabled_mods = json.load(file).keys()

        for i in range(self.mod_selector.GetItemCount()):
            if self.mod_selector.GetItemText(i, 2) in enabled_mods:
                self.mod_selector.CheckItem(i, True)
                #enable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))
            else:
                self.mod_selector.CheckItem(i, False)
                #disable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))

        file.close()


    def SaveProfile(self, event):
        profile_name = self.profile_textctrl.GetValue()
        if profile_name == "":
            return

        file = open("Profiles\\" + profile_name + ".json", "w")
        mods_dict = {}
        for i in range(self.mod_selector.GetItemCount()):
            if self.mod_selector.IsItemChecked(i):
                mods_dict[self.mod_selector.GetItemText(i, 2)] = True
        json.dump(mods_dict, file)
        file.close()

        self.refresh_profiles()

    def DeleteProfile(self, event):
        profile_name = self.profile_textctrl.GetValue()
        if profile_name == "":
            return
        os.remove("Profiles\\" + profile_name + ".json")
        self.refresh_profiles()

    def ProfileClick(self, event):
        self.profile_textctrl.SetValue(event.GetText())


    def ChangeGamePath(self, event):
        dialog = wx.DirDialog(None, "Select Paks Folder",
                              style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            print(type(dialog.GetPath()))
            self.main.game_directory = dialog.GetPath()

            json_data = {}
            json_data["game_directory"] = self.main.game_directory
            json.dump(json_data, open("Settings.ini", "w"))

        dialog.Destroy()


    def OnRefresh(self, event):
        self.refresh_mods()


    def RunReadyOrNot(self, event):
        ron_path_split = self.main.game_directory.split("\\")
        print(ron_path_split)
        ron_path = ""
        for item in ron_path_split:
            ron_path += item + "\\"
            if item == "ReadyOrNot":
                break
        ron_path += "\\Binaries\\Win64\\ReadyOrNot-Win64-Shipping.exe"
        print(ron_path)
        os.startfile(ron_path)

    def OpenWebPage(self, event):
        webbrowser.open('http://unofficial-modding-guide.com/downloads/QuantumModManager.exe')

