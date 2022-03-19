import json, os, wx
import GlobalVariables


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
    return temp


def get_profiles():
    path = r"Profiles"
    temp = []
    with os.scandir(path) as dirs:
        for dir in dirs:
                temp.append(dir.name.split(".")[0])
    return temp


def refresh_mods():

    GlobalVariables.mods_list.clear()
    mods = get_mods();

    for mod in mods:
        name = mod.split("\\")[-1].split("-")[1].split(".")[0].replace("_P", "").replace("Mods_", "").replace("_", " ")
        path = mod.replace(".old", "")
        GlobalVariables.mods_list.append( (name, str(os.path.getsize(mod)/1000) + " MB", path.split("\\")[-1]) )

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
        vbox2 = wx.BoxSizer(wx.VERTICAL)

        selBtn = wx.Button(leftPanel, label='Select All')
        desBtn = wx.Button(leftPanel, label='Deselect All')
        appBtn = wx.Button(leftPanel, label='Apply Mod Changes')
        game_path_button = wx.Button(leftPanel, label='Change Game Path')

        selBtn.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        desBtn.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        appBtn.Bind(wx.EVT_BUTTON, self.OnApply)
        game_path_button.Bind(wx.EVT_BUTTON, self.ChangeGamePath)


        vbox2.Add(selBtn, flag=wx.ALIGN_CENTER)
        vbox2.Add(desBtn, flag=wx.ALIGN_CENTER)
        vbox2.Add(game_path_button, flag=wx.ALIGN_CENTER)
        vbox2.Add(appBtn, flag=wx.ALIGN_CENTER)

        leftPanel.SetSizer(vbox2)

        #
        # Right Panel
        #
        vbox.Add(GlobalVariables.mod_selector, 4, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        # vbox.Add(self.log, 1, wx.EXPAND)
        # vbox.Add((-1, 10))
        vbox.Add(wx.StaticText(rightPanel, label="Profiles"))
        vbox.Add(GlobalVariables.profile_selector, 4, wx.EXPAND | wx.BOTTOM, 3)

        #
        # Profile Buttons
        #
        profile_options = wx.BoxSizer(wx.HORIZONTAL)
        self.load_profile = wx.Button(rightPanel, label="Load Profile")
        self.save_profile = wx.Button(rightPanel, label="Save Profile")
        GlobalVariables.profile_textctrl = wx.TextCtrl(rightPanel)
        self.load_profile.Bind(wx.EVT_BUTTON, self.LoadProfile)
        self.save_profile.Bind(wx.EVT_BUTTON, self.SaveProfile)

        profile_options.Add(self.load_profile)
        profile_options.Add(self.save_profile)
        profile_options.Add(GlobalVariables.profile_textctrl, proportion=1)


        vbox.Add(profile_options, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5)

        rightPanel.SetSizer(vbox)

        # Add left and right panels to main sizer
        outer_horz.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        outer_horz.Add(rightPanel, 1, wx.EXPAND)
        outer_horz.Add((3, -1))

        # Add main sizer to main panel
        panel.SetSizer(outer_horz)

        # Final window changes
        self.SetTitle('Quantum Mod Manager')
        self.Centre()

        if GlobalVariables.game_directory == "":
            self.ChangeGamePath(None)

        refresh_mods()
        refresh_profiles()


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
                enable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))
            else:
                disable_mod(GlobalVariables.mod_selector.GetItemText(i, 2))


    def LoadProfile(self, event):
        profile_name = GlobalVariables.profile_textctrl.GetValue()
        if profile_name == "":
            return

        refresh_mods()

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

        refresh_profiles()


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

def main():

    # Read or Create Config
    if os.path.isfile("Settings.ini"):
        json_data = json.load(open("Settings.ini", "r"))
        GlobalVariables.game_directory = json_data["game_directory"]
    else:
        json_data = {}
        json_data["game_directory"] = ""
        json.dump(json_data, open("Settings.ini", "w"))

    app = wx.App()
    ex = ModManager(None)
    ex.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()