import json
import os

import wx

import GlobalVariables
import HelperFunctions


class CheckListCtrl(wx.ListCtrl):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
                wx.SUNKEN_BORDER)
        self.EnableCheckBoxes(True)

class NoCheckListCtrl(wx.ListCtrl):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
                wx.SUNKEN_BORDER)
        self.EnableCheckBoxes(False)


class ModManager(wx.Frame):

    def __init__(self, *args, **kw):
        super(ModManager, self).__init__(size=(700, 500),*args, **kw)

        panel = wx.Panel(self)

        # Set Font
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        vbox = wx.BoxSizer(wx.VERTICAL)
        outer_horz = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel)
        rightPanel = wx.Panel(panel)

        #self.log = wx.TextCtrl(rightPanel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        GlobalVariables.mod_selector = CheckListCtrl(rightPanel)
        GlobalVariables.mod_selector.InsertColumn(0, 'Mod', width=140)
        GlobalVariables.mod_selector.InsertColumn(1, 'Size')
        GlobalVariables.mod_selector.InsertColumn(2, 'Full Name')


        GlobalVariables.profile_selector = NoCheckListCtrl(rightPanel)
        GlobalVariables.profile_selector.InsertColumn(0, 'Profile')
        GlobalVariables.profile_selector.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ProfileClick)

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



        # Profile Settings
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
        vbox.Add(GlobalVariables.mod_selector, 4, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))

        vbox.Add(wx.StaticText(rightPanel, label="Profiles"))
        vbox.Add(GlobalVariables.profile_selector, 4, wx.EXPAND | wx.BOTTOM, 3)

        #
        # Profile Buttons
        #
        profile_options = wx.BoxSizer(wx.HORIZONTAL)
        self.load_profile = wx.Button(rightPanel, label="Load Profile")
        self.save_profile = wx.Button(rightPanel, label="Save Profile")
        self.delete_profile = wx.Button(rightPanel, label="Delete Profile")
        GlobalVariables.profile_textctrl = wx.TextCtrl(rightPanel)
        self.load_profile.Bind(wx.EVT_BUTTON, self.LoadProfile)
        self.save_profile.Bind(wx.EVT_BUTTON, self.SaveProfile)
        self.delete_profile.Bind(wx.EVT_BUTTON, self.DeleteProfile)

        profile_options.Add(self.load_profile)
        profile_options.Add(self.save_profile)
        profile_options.Add(self.delete_profile)
        profile_options.Add(GlobalVariables.profile_textctrl, proportion=1)


        vbox.Add(profile_options, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5)

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

        if GlobalVariables.game_directory == "":
            self.ChangeGamePath(None)

        if GlobalVariables.game_directory == "":
            quit()

        HelperFunctions.refresh_mods()
        HelperFunctions.refresh_profiles()


    def OnSelectAll(self, event):

        num = GlobalVariables.mod_selector.GetItemCount()
        for i in range(num):
            GlobalVariables.mod_selector.CheckItem(i)


    def OnDeselectAll(self, event):

        num = GlobalVariables.mod_selector.GetItemCount()
        for i in range(num):
            GlobalVariables.mod_selector.CheckItem(i, False)


    def OnApply(self, event):

        num = GlobalVariables.mod_selector.GetItemCount()

        for i in range(num):

            if GlobalVariables.mod_selector.IsItemChecked(i):
                HelperFunctions.enable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))
            else:
                HelperFunctions.disable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))


    def LoadProfile(self, event):
        profile_name = GlobalVariables.profile_textctrl.GetValue()
        if profile_name == "":
            return

        HelperFunctions.refresh_mods()

        file = open("Profiles\\" + profile_name + ".json", "r")
        enabled_mods = json.load(file).keys()

        for i in range(GlobalVariables.mod_selector.GetItemCount()):
            if GlobalVariables.mod_selector.GetItemText(i, 2) in enabled_mods:
                GlobalVariables.mod_selector.CheckItem(i, True)
                #enable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))
            else:
                GlobalVariables.mod_selector.CheckItem(i, False)
                #disable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))

        file.close()


    def SaveProfile(self, event):
        profile_name = GlobalVariables.profile_textctrl.GetValue()
        if profile_name == "":
            return

        file = open("Profiles\\" + profile_name + ".json", "w")
        mods_dict = {}
        for i in range(GlobalVariables.mod_selector.GetItemCount()):
            if GlobalVariables.mod_selector.IsItemChecked(i):
                mods_dict[GlobalVariables.mod_selector.GetItemText(i, 2)] = True
        json.dump(mods_dict, file)
        file.close()

        HelperFunctions.refresh_profiles()

    def DeleteProfile(self, event):
        profile_name = GlobalVariables.profile_textctrl.GetValue()
        if profile_name == "":
            return
        os.remove("Profiles\\" + profile_name + ".json")
        HelperFunctions.refresh_profiles()

    def ProfileClick(self, event):
        GlobalVariables.profile_textctrl.SetValue(event.GetText())


    def ChangeGamePath(self, event):
        dialog = wx.DirDialog(None, "Select Paks Folder",
                              style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            print(type(dialog.GetPath()))
            GlobalVariables.game_directory = dialog.GetPath()

            json_data = {}
            json_data["game_directory"] = GlobalVariables.game_directory
            json.dump(json_data, open("Settings.ini", "w"))

        dialog.Destroy()


    def OnRefresh(self, event):
        HelperFunctions.refresh_mods()


    def RunReadyOrNot(self, event):
        ron_path_split = GlobalVariables.game_directory.split("\\")
        print(ron_path_split)
        ron_path = ""
        for item in ron_path_split:
            ron_path += item + "\\"
            if item == "ReadyOrNot":
                break
        ron_path += "\\Binaries\\Win64\\ReadyOrNot-Win64-Shipping.exe"
        print(ron_path)
        os.startfile(ron_path)


    def AutoFindPath(self, event):
        HelperFunctions.get_steam_dir()
        if GlobalVariables.possible_game_path is not None:
            GlobalVariables.game_directory = GlobalVariables.possible_game_path
            json_data = {}
            json_data["game_directory"] = GlobalVariables.game_directory
            json.dump(json_data, open("Settings.ini", "w"))