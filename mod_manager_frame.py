import json, os, wx, requests, sys, re, shutil, subprocess
from py7zr import unpack_7zarchive
import wx.lib.agw.ultimatelistctrl as wxu

import helper_functions

#-----------------------------------------------------------------------------------------------------------------------

class ModFileDrop(wx.FileDropTarget):

    def __init__(self, window, mod_manager):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.mod_manager = mod_manager

    def OnDropFiles(self, x, y, filenames):

        for filename in filenames:
            # If the file is a compressed file, extract all the .paks and add them to the Pak directory.
            if filename.endswith(".zip") or filename.endswith(".7z") or filename.endswith(".rar"):

                # Make temp folder.
                if not os.path.isdir("temp"):
                    os.mkdir("temp")

                shutil.unpack_archive(filename, "temp")

                # Get all files in folders and subfolders.
                file_list = list()
                for (dir, dir_names, file_names) in os.walk("temp"):
                    file_list += [os.path.join(dir, file) for file in file_names]

                # For each file, if it's a .pak file, move it the Paks folder.
                for file in file_list:
                    if file.endswith(".pak"):
                        if os.path.isfile(self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1]):
                            os.remove(self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1])
                        os.rename(file, self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1])

                # Delete everything in temp folder.
                for file in os.scandir("temp"):
                    os.remove(file)


            # If the file is a .pak file, add it to the Pak directory.
            if filename.endswith(".pak"):
                if os.path.isfile(self.mod_manager.main.game_directory + "\\" + filename.split("\\")[-1]):
                    os.remove(self.mod_manager.main.game_directory + "\\" + filename.split("\\")[-1])
                os.rename(filename, self.mod_manager.main.game_directory + "\\" + filename.split("\\")[-1])

            # If we are a folder get all .pak files in directories and subdirectories and then addd them to the Paks directory.
            if "." not in filename:
                file_list = list()
                for (dir, dir_names, file_names) in os.walk("filename"):
                    file_list += [os.path.join(dir, file) for file in file_names]

                # For each file, if it's a .pak file, move it the Paks folder.
                for file in file_list:
                    if file.endswith(".pak"):
                        if os.path.isfile(self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1]):
                            os.remove(self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1])
                        os.rename(file, self.mod_manager.main.game_directory + "\\" + file.split("\\")[-1])

        self.mod_manager.refresh_mods()
        self.mod_manager.refresh_mods()
        return True

#-----------------------------------------------------------------------------------------------------------------------

class ModManager(wx.Frame):

    def __init__(self, main, *args, **kw):
        super(ModManager, self).__init__(size=(740, 500),*args, **kw)
        shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)

        self.main = main
        self.current_version = 2.0

        # Panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#333")

        # Set Font
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        right_panel_vert_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_horz = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel)
        rightPanel = wx.Panel(panel)

        self.mod_selector = wxu.UltimateListCtrl(rightPanel, agwStyle = wx.LC_REPORT | wxu.ULC_NO_HEADER | wxu.ULC_NO_HIGHLIGHT | wxu.ULC_SINGLE_SEL)

        self.mod_selector.SetForegroundColour("#FFF")
        self.mod_selector.SetBackgroundColour("#333")
        self.mod_selector.SetTextColour("#FFF")

        self.mod_selector.InsertColumn(0, 'Mod', width=200)
        self.mod_selector.InsertColumn(1, 'Size')
        self.mod_selector.InsertColumn(2, 'Full Name', width=240)

        self.mod_selector.SetDropTarget(ModFileDrop(rightPanel, self))


        self.profile_selector = wxu.UltimateListCtrl(rightPanel, agwStyle = wx.LC_REPORT | wxu.ULC_NO_HEADER | wxu.ULC_SINGLE_SEL)

        self.profile_selector.SetForegroundColour("#FFF")
        self.profile_selector.SetBackgroundColour("#333")
        self.profile_selector.SetTextColour("#FFF")

        self.profile_selector.InsertColumn(0, 'Profile')
        self.profile_selector.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnProfileClick)

        #
        # Left Panel
        #

        left_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        #
        # Mod Settings
        #
        mod_settings_sizer = wx.BoxSizer(wx.VERTICAL)

        # Select All Mods Button
        select_all_mod = wx.Button(leftPanel, label='Select All')
        select_all_mod.SetBackgroundColour("#333")
        select_all_mod.SetForegroundColour("#FFF")

        # Deselect All Mods Button
        deselect_all_mod = wx.Button(leftPanel, label='Deselect All')
        deselect_all_mod.SetBackgroundColour("#333")
        deselect_all_mod.SetForegroundColour("#FFF")

        # Refresh Mods Button
        refresh_mod = wx.Button(leftPanel, label='Refresh')
        refresh_mod.SetBackgroundColour("#333")
        refresh_mod.SetForegroundColour("#FFF")

        # Apply Mod Changes Button
        apply_mod = wx.Button(leftPanel, label='Apply Changes')
        apply_mod.SetBackgroundColour("#333")
        apply_mod.SetForegroundColour("#FFF")

        # Change Game Path button.
        game_path_button = wx.Button(leftPanel, label='Change Game Path')
        game_path_button.SetBackgroundColour("#333")
        game_path_button.SetForegroundColour("#FFF")

        # Run Ready or Not Button
        run_ready_or_not = wx.Button(leftPanel, label='Run Ready or Not')
        run_ready_or_not.SetBackgroundColour("#333")
        run_ready_or_not.SetForegroundColour("#FFF")

        # Bind all buttons to functions.
        select_all_mod.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        deselect_all_mod.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        refresh_mod.Bind(wx.EVT_BUTTON, self.OnRefresh)
        apply_mod.Bind(wx.EVT_BUTTON, self.OnApply)
        game_path_button.Bind(wx.EVT_BUTTON, self.OnChangeGamePath)
        run_ready_or_not.Bind(wx.EVT_BUTTON, self.OnRunReadyOrNot)

        # Add all buttons to sizer.
        mod_settings_sizer.Add(select_all_mod, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(deselect_all_mod, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(refresh_mod, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(apply_mod, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add((-1, 25))
        mod_settings_sizer.Add(game_path_button, flag=wx.ALIGN_CENTER)
        mod_settings_sizer.Add(run_ready_or_not, flag=wx.ALIGN_CENTER)

        left_panel_sizer.Add(mod_settings_sizer, proportion=1)

        leftPanel.SetSizer(left_panel_sizer)

        #
        # Right Panel
        #
        right_panel_vert_sizer.Add(self.mod_selector, 4, wx.EXPAND | wx.TOP, 3)
        right_panel_vert_sizer.Add((-1, 10))

        self.profiles_text = wx.StaticText(rightPanel, label="Profiles")
        self.profiles_text.SetForegroundColour("#FFF")
        right_panel_vert_sizer.Add(self.profiles_text)
        right_panel_vert_sizer.Add(self.profile_selector, 4, wx.EXPAND | wx.BOTTOM, 3)

        #
        # Profile Buttons
        #
        profile_options = wx.BoxSizer(wx.HORIZONTAL)

        # Load Profile Button
        self.load_profile = wx.Button(rightPanel, label="Load Profile")
        self.load_profile.SetBackgroundColour("#333")
        self.load_profile.SetForegroundColour("#FFF")

        # Save Profile Button
        self.save_profile = wx.Button(rightPanel, label="Save Profile")
        self.save_profile.SetBackgroundColour("#333")
        self.save_profile.SetForegroundColour("#FFF")

        # Delete Profile Button
        self.delete_profile = wx.Button(rightPanel, label="Delete Profile")
        self.delete_profile.SetBackgroundColour("#333")
        self.delete_profile.SetForegroundColour("#FFF")

        # Profile Name Input
        self.profile_textctrl = wx.TextCtrl(rightPanel)
        self.profile_textctrl.SetForegroundColour("#FFF")
        self.profile_textctrl.SetBackgroundColour("#333")

        # Bind buttons to functions.
        self.load_profile.Bind(wx.EVT_BUTTON, self.OnLoadProfile)
        self.save_profile.Bind(wx.EVT_BUTTON, self.OnSaveProfile)
        self.delete_profile.Bind(wx.EVT_BUTTON, self.OnDeleteProfile)

        # Add all items to sizer.
        profile_options.Add(self.load_profile)
        profile_options.Add(self.save_profile)
        profile_options.Add(self.delete_profile)
        profile_options.Add(self.profile_textctrl, proportion=1)

        right_panel_vert_sizer.Add(profile_options, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5)

        #
        # Version Warning
        #
        warning_pane = wx.BoxSizer(wx.HORIZONTAL)

        response = None
        try:
            # Send a response to the page with the version number.
            response = requests.get('https://unofficial-modding-guide.com/tools.html')
        except:
            ...

        # If we got a reponse back.
        if response is not None and str(response.reason) == "OK":
            # Get the version from the striped HTML.
            version = float(str(response.content).split("Quantum Mod Manager")[1][2:5])
            # If out version is lower, show update button.
            if version > self.current_version:
                self.newest_version = version
                self.warning_message = wx.StaticText(rightPanel, label = "Version Outdated: https://unofficial-modding-guide.com/downloads/QuantumModManager.exe")
                self.warning_message.SetForegroundColour("#FFF")

                self.warning_button = wx.Button(rightPanel, label="Download")
                self.warning_button.SetForegroundColour("#FFF")
                self.warning_button.SetBackgroundColour("#333")

                self.warning_button.Bind(wx.EVT_BUTTON, self.OnDownloadLatest)

                warning_pane.Add(self.warning_message, flag=wx.TOP, border=7)
                warning_pane.Add(self.warning_button, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, border=5)

        right_panel_vert_sizer.Add(warning_pane, flag=wx.EXPAND)

        rightPanel.SetSizer(right_panel_vert_sizer)

        # Add left and right panels to main sizer
        outer_horz.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        outer_horz.Add(rightPanel, 1, wx.EXPAND)
        outer_horz.Add((3, -1))

        # Add main sizer to main panel
        panel.SetSizer(outer_horz)

        # Final window changes
        self.SetTitle('Quantum Mod Manager v' + str(self.current_version))
        self.Centre()

        # If the game directory is not set.
        if self.main.game_directory is None or self.main.game_directory == "":
            possible_path = helper_functions.get_steam_dir()

            # If we couldn't auto find the steam directory, open up a prompt to search for it.
            if possible_path is None:
                self.OnChangeGamePath(None)
            # If we did a find a directory, apply and save changes.
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


    #
    # Refresh Mods List
    #
    def refresh_mods(self):
        mods_list = []

        mods = helper_functions.get_mods(self.main);

        for mod in mods:

            # Check for duplicates.
            if os.path.isdir(mod.replace(".old", "")) and os.path.isdir(mod.replace(".old", "") + ".old"):
                # Remove likely older version.
                os.remove(mod.replace(".old", "") + ".old")

                # Check if we are on the older version, if so, skip. Eventually, we should read metadata to ensure which
                # file is older / younger.
                if mod == mod.replace(".old", "") + ".old":
                    continue


            name = mod.split("\\")[-1] # Get file name with extension.
            name = name.split("-", maxsplit=1)[-1] # Get file name without pakchunk99
            name = name.split(".")[0] # Remove extenstion
            name = name.replace("_P", "") # Remove patch file modifier.
            name = name.replace("Mods", "") # Remove mods.
            name = name.replace("_", "") # Remove left over _'s
            name = name.replace("-", "") # Remove left over -'s
            name = name.replace(" ", "") # Prepare for camelcase regex.

            # Regex to separate camelcase and re-add to string.
            name_list = re.findall(r'[A-Z,0-9](?:[a-z]+|[A-Z,0-9]*(?=[A-Z,0-9]|$))', name)
            final_name = ""
            for item in name_list:
                final_name += item + " "
            final_name.strip(" ")

            # Remove .old extension.
            path = mod.replace(".old", "")
            mods_list.append((final_name, str(round(os.path.getsize(mod) / 1000000, 2)) + " MB", path.split("\\")[-1]))

        # Remove all the items from the list so we can add them back.
        self.mod_selector.DeleteAllItems()

        idx = 0
        for i in mods_list:
            # Create new item row with a selection box
            index = self.mod_selector.InsertStringItem(idx, str(i[0]), it_kind=1)
            self.mod_selector.SetStringItem(index, 1, str(i[1]))
            self.mod_selector.SetStringItem(index, 2, str(i[2]))

            # If the file is enabled.
            if helper_functions.is_file_enabled(i[2], self.main):
                item = self.mod_selector.GetItem(index, 0)
                #item.SetBackgroundColour(wx.Colour("#333"))
                #item.SetTextColour(wx.Colour("#FFF"))
                item.Check(True)
                self.mod_selector.SetItem(item)
            idx += 1


    #
    # Refresh profile list.
    #
    def refresh_profiles(self):
        self.profile_selector.DeleteAllItems()
        idx = 0
        for i in helper_functions.get_profiles():
            index = self.profile_selector.InsertStringItem(idx, i)
            idx += 1


    def run_downloaded_version(self):
        subprocess.run([f"QuantumModManager v{self.newest_version}.exe", f"{sys.argv[0]}"])


    #
    # Interact Events
    #
    def OnSelectAll(self, event):

        num = self.mod_selector.GetItemCount()
        for i in range(num):
            item = self.mod_selector.GetItem(i, 0)
            item.Check(True)
            self.mod_selector.SetItem(item)


    def OnDeselectAll(self, event):

        num = self.mod_selector.GetItemCount()
        for i in range(num):
            item = self.mod_selector.GetItem(i, 0)
            item.Check(False)
            self.mod_selector.SetItem(item)


    def OnApply(self, event):

        num = self.mod_selector.GetItemCount()

        for i in range(num):
            if self.mod_selector.IsItemChecked(i):
                helper_functions.enable_mod(self.mod_selector.GetItem(i, col=2).GetText(), self.main)
            else:
                helper_functions.disable_mod(self.mod_selector.GetItem(i, col=2).GetText(), self.main)


    def OnLoadProfile(self, event):
        profile_name = self.profile_textctrl.GetValue()
        if profile_name == "":
            return

        self.refresh_mods()

        file = open("Profiles\\" + profile_name + ".json", "r")
        enabled_mods = json.load(file).keys()

        for i in range(self.mod_selector.GetItemCount()):
            if self.mod_selector.GetItem(i, col=2).GetText() in enabled_mods:

                item = self.mod_selector.GetItem(i, 0)
                item.Check(True)
                self.mod_selector.SetItem(item)
            else:
                item = self.mod_selector.GetItem(i, 0)
                item.Check(False)
                self.mod_selector.SetItem(item)

        file.close()


    def OnSaveProfile(self, event):
        profile_name = self.profile_textctrl.GetValue()
        if profile_name == "":
            return

        file = open("Profiles\\" + profile_name + ".json", "w")
        mods_dict = {}
        for i in range(self.mod_selector.GetItemCount()):
            if self.mod_selector.IsItemChecked(i):
                mods_dict[self.mod_selector.GetItem(i, col=2).GetText()] = True
        json.dump(mods_dict, file)
        file.close()

        self.refresh_profiles()


    def OnDeleteProfile(self, event):
        profile_name = self.profile_textctrl.GetValue()
        if profile_name == "":
            return
        os.remove("Profiles\\" + profile_name + ".json")
        self.refresh_profiles()


    def OnProfileClick(self, event):
        self.profile_textctrl.SetValue(event.GetText())


    def OnChangeGamePath(self, event):
        dialog = wx.DirDialog(None, "Select Paks Folder", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.main.game_directory = dialog.GetPath()

            json_data = {}
            json_data["game_directory"] = self.main.game_directory
            json.dump(json_data, open("Settings.ini", "w"))

        dialog.Destroy()
        self.refresh_mods()


    def OnRefresh(self, event):
        self.refresh_mods()


    def OnRunReadyOrNot(self, event):
        ron_path_split = self.main.game_directory.split("\\")
        ron_path = ""
        for item in ron_path_split:
            ron_path += item + "\\"
            if item == "ReadyOrNot":
                break
        ron_path += "\\Binaries\\Win64\\ReadyOrNot-Win64-Shipping.exe"
        os.startfile(ron_path)


    def OnDownloadLatest(self, event):

        # Download file.
        url = 'http://unofficial-modding-guide.com/downloads/QuantumModManager.exe'
        r = requests.get(url, stream=True)
        with open(f"QuantumModManager v{self.newest_version}.exe", "wb") as exe:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    exe.write(chunk)

        sys.exit()





