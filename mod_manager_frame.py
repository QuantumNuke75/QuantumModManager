import json, os, wx, requests, sys, re, shutil, subprocess, datetime
from py7zr import unpack_7zarchive
import wx.lib.agw.ultimatelistctrl as wxu

import helper_functions

#-----------------------------------------------------------------------------------------------------------------------

import CustomUltimateListCtrl

main_color = "#252525"
highlight_color = "#252525"
text_color = "#FFF"


class UltimateHeaderRenderer(object):

    def __init__(self, parent):
        self._hover = False
        self._pressed = False


    def DrawHeaderButton(self, dc, rect, flags):
        self._hover = False
        self._pressed = False

        color = highlight_color

        if flags & wx.CONTROL_DISABLED:
            color = wx.Colour(wx.WHITE)

        elif flags & wx.CONTROL_SELECTED:
            color = wx.Colour(wx.BLUE)

        if flags & wx.CONTROL_PRESSED:
            self._pressed = True
            #color = cutils.AdjustColour(color, -50)

        elif flags & wx.CONTROL_CURRENT:
            self._hover = True
            #color = cutils.AdjustColour(color, -50)

        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect)

        dc.SetBrush(wx.Brush(wx.Colour(255,255,255), wx.SOLID))
        dc.DrawRectangle(wx.Rect(rect.GetPosition()[0],rect.GetPosition()[1]+rect.GetHeight()-2,rect.GetWidth(),2))

        dc.SetBackgroundMode(wx.TRANSPARENT)


    def GetForegroundColour(self):
        return wx.Colour(255,255,255)


    def GetBackgroundColour(self):
        return wx.Colour(0,0,0)

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
        self.current_version = 2.3

        self.current_item = None
        self.previous_item = None

        # Panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(main_color))

        # Set Font
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        right_panel_vert_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_horz = wx.BoxSizer(wx.HORIZONTAL)

        left_panel = wx.Panel(panel)
        right_panel = wx.Panel(panel)

        #self.mod_selector = wxu.UltimateListCtrl(right_panel, agwStyle = wx.LC_REPORT | wxu.ULC_NO_HIGHLIGHT | wxu.ULC_SINGLE_SEL)
        self.mod_selector = CustomUltimateListCtrl.UltimateListCtrl(right_panel,
                                                 agwStyle=wx.LC_REPORT | wxu.ULC_NO_HIGHLIGHT | wxu.ULC_SINGLE_SEL)
        self.mod_selector.Bind(wx.EVT_MOTION, self.OnMouseOver)
        self.mod_selector.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        self.mod_selector.SetForegroundColour(wx.Colour(text_color))
        self.mod_selector.SetBackgroundColour(wx.Colour(main_color))
        self.mod_selector.SetTextColour(wx.Colour(text_color))

        self.mod_selector.InsertColumn(0, 'Mod', width=200)
        self.mod_selector.InsertColumn(1, 'Size')
        self.mod_selector.InsertColumn(2, 'Full Name', width=240)
        self.mod_selector.InsertColumn(3, 'Created')

        self.mod_selector.SetHeaderCustomRenderer(UltimateHeaderRenderer(self.mod_selector))
        self.mod_selector.SetDropTarget(ModFileDrop(right_panel, self))


        self.profile_selector = wxu.UltimateListCtrl(right_panel, agwStyle = wx.LC_REPORT | wxu.ULC_NO_HEADER | wxu.ULC_SINGLE_SEL)

        self.profile_selector.SetForegroundColour(wx.Colour(text_color))
        self.profile_selector.SetBackgroundColour(wx.Colour(main_color))
        self.profile_selector.SetTextColour(wx.Colour(text_color))

        self.profile_selector.InsertColumn(0, 'Profile')
        self.profile_selector.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnProfileClick)

        #
        # Left Panel
        #

        left_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # QMM Font
        qmm_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        qmm_font.SetPointSize(16)

        text = wx.StaticText(left_panel, label="", style=wx.ALIGN_CENTER)
        left_panel_sizer.Add(text,1,wx.BOTTOM)




        # self.info_button = wx.Button(left_panel, label="Information")
        # self.info_button.Bind(wx.EVT_BUTTON, self.OnInfo)
        # self.info_button.SetForegroundColour(wx.Colour(text_color))
        # self.info_button.SetBackgroundColour(wx.Colour(main_color))
        #
        # left_panel_sizer.Add(self.info_button, flag=wx.EXPAND)

        #left_panel_sizer.Add(game_path_button, flag=wx.ALIGN_CENTER)
        #left_panel_sizer.Add(run_ready_or_not, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=5)

        left_panel.SetSizer(left_panel_sizer)



        #
        # Right Panel
        #

        right_panel_vert_sizer.Add((-1,10))

        header_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        header_font.SetPointSize(12)
        mods_text = wx.StaticText(right_panel, label="Mods")
        mods_text.SetForegroundColour(wx.Colour(text_color))
        mods_text.SetFont(header_font.Bold())
        right_panel_vert_sizer.Add(mods_text)

        # Add mod selector.
        right_panel_vert_sizer.Add(self.mod_selector, 4, wx.EXPAND | wx.TOP, 3)

        #
        # Mod Settings
        #
        mod_settings_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Select All Mods Button
        select_all_mod = wx.Button(right_panel, label='Select All')
        select_all_mod.SetBackgroundColour(wx.Colour(main_color))
        select_all_mod.SetForegroundColour(wx.Colour(text_color))

        # Deselect All Mods Button
        deselect_all_mod = wx.Button(right_panel, label='Deselect All')
        deselect_all_mod.SetBackgroundColour(wx.Colour(main_color))
        deselect_all_mod.SetForegroundColour(wx.Colour(text_color))

        # Refresh Mods Button
        refresh_mod = wx.Button(right_panel, label='Refresh')
        refresh_mod.SetBackgroundColour(wx.Colour(main_color))
        refresh_mod.SetForegroundColour(wx.Colour(text_color))

        # Apply Mod Changes Button
        apply_mod = wx.Button(right_panel, label='Apply Changes')
        apply_mod.SetBackgroundColour(wx.Colour(main_color))
        apply_mod.SetForegroundColour(wx.Colour(text_color))


        # Bind all buttons to functions.
        select_all_mod.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        deselect_all_mod.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        refresh_mod.Bind(wx.EVT_BUTTON, self.OnRefresh)
        apply_mod.Bind(wx.EVT_BUTTON, self.OnApply)

        # Add all buttons to sizer.
        mod_settings_sizer.Add(select_all_mod, flag=wx.ALIGN_CENTER, proportion=1)
        mod_settings_sizer.Add(deselect_all_mod, flag=wx.ALIGN_CENTER, proportion=1)
        mod_settings_sizer.Add(refresh_mod, flag=wx.ALIGN_CENTER, proportion=1)
        mod_settings_sizer.Add(apply_mod, flag=wx.ALIGN_CENTER, proportion=1)

        right_panel_vert_sizer.Add(mod_settings_sizer)

        right_panel_vert_sizer.Add((-1, 10))

        profiles_text = wx.StaticText(right_panel, label="Profiles")
        profiles_text.SetForegroundColour(wx.Colour(text_color))
        profiles_text.SetFont(header_font.Bold())
        right_panel_vert_sizer.Add(profiles_text)
        right_panel_vert_sizer.Add(self.profile_selector, 4, wx.EXPAND | wx.BOTTOM, 3)

        #
        # Profile Buttons
        #
        profile_options = wx.BoxSizer(wx.HORIZONTAL)

        # Load Profile Button
        load_profile = wx.Button(right_panel, label="Load Profile")
        load_profile.SetBackgroundColour(wx.Colour(main_color))
        load_profile.SetForegroundColour(wx.Colour(text_color))

        # Save Profile Button
        save_profile = wx.Button(right_panel, label="Save Profile")
        save_profile.SetBackgroundColour(wx.Colour(main_color))
        save_profile.SetForegroundColour(wx.Colour(text_color))

        # Delete Profile Button
        delete_profile = wx.Button(right_panel, label="Delete Profile")
        delete_profile.SetBackgroundColour(wx.Colour(main_color))
        delete_profile.SetForegroundColour(wx.Colour(text_color))

        # Profile Name Input
        self.profile_textctrl = wx.TextCtrl(right_panel)
        self.profile_textctrl.SetForegroundColour(wx.Colour(text_color))
        self.profile_textctrl.SetBackgroundColour(wx.Colour(main_color))

        # Bind buttons to functions.
        load_profile.Bind(wx.EVT_BUTTON, self.OnLoadProfile)
        save_profile.Bind(wx.EVT_BUTTON, self.OnSaveProfile)
        delete_profile.Bind(wx.EVT_BUTTON, self.OnDeleteProfile)

        # Add all items to sizer.
        profile_options.Add(load_profile)
        profile_options.Add(save_profile)
        profile_options.Add(delete_profile)
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
                warning_message = wx.StaticText(right_panel, label = "Version Outdated: https://unofficial-modding-guide.com/downloads/QuantumModManager.exe")
                warning_message.SetForegroundColour(wx.Colour(text_color))

                warning_button = wx.Button(right_panel, label="Download")
                warning_button.SetForegroundColour(wx.Colour(text_color))
                warning_button.SetBackgroundColour(wx.Colour(main_color))

                warning_button.Bind(wx.EVT_BUTTON, self.OnDownloadLatest)

                warning_pane.Add(warning_message, flag=wx.TOP, border=7)
                warning_pane.Add(warning_button, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, border=5)

        right_panel_vert_sizer.Add(warning_pane, flag=wx.EXPAND)

        bottom_buttons = wx.BoxSizer(wx.HORIZONTAL)
        # Change Game Path button.
        game_path_button = wx.Button(right_panel, label='Change Game Path')
        game_path_button.SetBackgroundColour(wx.Colour(main_color))
        game_path_button.SetForegroundColour(wx.Colour(text_color))

        # Run Ready or Not Button
        run_ready_or_not = wx.Button(right_panel, label='Run Ready or Not')
        run_ready_or_not.SetBackgroundColour(wx.Colour(main_color))
        run_ready_or_not.SetForegroundColour(wx.Colour(text_color))

        game_path_button.Bind(wx.EVT_BUTTON, self.OnChangeGamePath)
        run_ready_or_not.Bind(wx.EVT_BUTTON, self.OnRunReadyOrNot)

        bottom_buttons.Add(game_path_button)
        bottom_buttons.Add(run_ready_or_not)

        right_panel_vert_sizer.Add(bottom_buttons)

        right_panel.SetSizer(right_panel_vert_sizer)

        # Add left and right panels to main sizer
        outer_horz.Add(left_panel, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        outer_horz.Add(right_panel, 1, wx.EXPAND | wx.RIGHT, 5)
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

        if self.main.game_directory is None:
            quit()

        # Refresh all mods and profiles.
        self.refresh_mods()
        self.refresh_profiles()

        #wx.lib.inspection.InspectionTool().Show()


    #
    # Refresh Mods List
    #
    def refresh_mods(self):
        mods_list = []

        mods = helper_functions.get_mods(self.main)

        for mod in mods:

            # Check for duplicates.
            if os.path.isfile(mod.replace(".old", "")) and os.path.isfile(mod.replace(".old", "") + ".old"):
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

        # Sorts mod by alphabetized.
        mods_list = sorted(mods_list)

        idx = 0
        for i in mods_list:
            # Create new item row with a selection box
            index = self.mod_selector.InsertStringItem(idx, str(i[0]), it_kind=1)
            self.mod_selector.SetStringItem(index, 1, str(i[1]))
            self.mod_selector.SetStringItem(index, 2, str(i[2]))
            name = str(i[2]) if os.path.isfile(self.main.game_directory + "\\" + str(i[2])) else str(i[2]) + ".old"
            time = os.path.getctime(self.main.game_directory + "\\" + name)
            self.mod_selector.SetStringItem(index, 3, str(datetime.datetime.fromtimestamp(time).strftime('%d-%m-%Y')))

            # If the file is enabled.
            if helper_functions.is_file_enabled(i[2], self.main):
                item = self.mod_selector.GetItem(index, 0)
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
    def OnMouseLeave(self, event):
        if self.current_item is not None:
            self.mod_selector.SetItemBackgroundColour(self.current_item, wx.Colour(wx.Colour(main_color)))


    def OnMouseOver(self, event):
        x = event.GetX()
        y = event.GetY()

        item, flags = self.mod_selector.HitTest((x, y))
        if item < 0:
            if self.previous_item is not None:
                self.mod_selector.SetItemBackgroundColour(self.previous_item, wx.Colour(wx.Colour(main_color)))
            if self.current_item is not None:
                self.mod_selector.SetItemBackgroundColour(self.current_item, wx.Colour(wx.Colour(main_color)))
            return

        if item is self.previous_item:
            return

        self.previous_item = self.current_item
        self.current_item = item

        if self.previous_item is not None:
            self.mod_selector.SetItemBackgroundColour(self.previous_item, wx.Colour(wx.Colour(main_color)))
        self.mod_selector.SetItemBackgroundColour(item, wx.Colour("#3246A8"))


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





