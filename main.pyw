import json
import os, wx, subprocess
import GlobalVariables
from pathlib import Path


class FileDropInput(wx.FileDropTarget):

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) != 1:
            return True

        GlobalVariables.input_path = str(Path(filenames[0]))
        GlobalVariables.file_input_textbox.SetValue(GlobalVariables.input_path)
        return True


class FileDropOutput(wx.FileDropTarget):

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) != 1:
            return True

        GlobalVariables.output_path = str(Path(filenames[0]))
        GlobalVariables.file_output_textbox.SetValue(GlobalVariables.output_path)
        return True

#
# For PAKing
#
def PAK():
    if not can_PAK():
        return

    unrealpak_path = Path("UnrealPaker\\Engine\\Binaries\\Win64\\UnrealPak.exe")
    base_file_name = GlobalVariables.input_path.split("\\")[-1].split(".")[0]
    file_list = Path("UnrealPaker\\Engine\\Binaries\\Win64\\filelist.txt")

    # Create filelist
    subprocess.Popen(
        f'@echo "{Path(GlobalVariables.output_path)}\\{base_file_name}\*.*" "../../../{GlobalVariables.game_name}/" > "{file_list}"',
        shell=True)

    cmd = f'"{unrealpak_path}" "{Path(GlobalVariables.output_path)}\\{base_file_name}.pak" -create="{os.path.abspath(file_list)}" -compress'

    # Create pak file
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout

    split_lines = output.read().decode().split("\n")
    for line in split_lines:
        if "Warning" in line:
            add_console_message(line + "\n", '#FFA500')
        elif "Error" in line:
            add_console_message(line + "\n", wx.RED)
        elif "executed" in line:
            add_console_message(line + "\n", wx.GREEN)
        else:
            add_console_message(line + "\n")

#
# For UNPAKing
#
def UNPAK():
    if not can_UNPAK():
        return

    unrealpak_path = Path("UnrealPaker\\Engine\\Binaries\\Win64\\UnrealPak.exe")
    base_file_name = GlobalVariables.input_path.split("\\")[-1].split(".")[0]

    cmd = f' "{unrealpak_path}" "{GlobalVariables.input_path}" -extract "{GlobalVariables.output_path}\\{base_file_name}"'

    # UNPAK file
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout

    split_lines = output.read().decode().split("\n")
    for line in split_lines:
        if "Warning" in line:
            add_console_message(line + "\n", '#FFA500')
        elif "Error" in line:
            add_console_message(line + "\n", wx.RED)
        elif "executed" in line:
            add_console_message(line + "\n", wx.GREEN)
        else:
            add_console_message(line + "\n")


#
# Add a console message.
#
def add_console_message(text, color=wx.WHITE, spacers=False):
    GlobalVariables.console_textbox.SetDefaultStyle(wx.TextAttr(color))
    if spacers:
        GlobalVariables.console_textbox.AppendText("\n")
    GlobalVariables.console_textbox.AppendText(text)
    if spacers:
        GlobalVariables.console_textbox.AppendText("\n")


#
# Check if can PAK
#
def can_PAK():
    if len(GlobalVariables.file_input_textbox.GetValue()) == 0:
        add_console_message("Input is empty.\n", wx.RED)
        return False
    if len(GlobalVariables.file_output_textbox.GetValue()) == 0:
        add_console_message("Output is empty.\n", wx.RED)
        return False
    if "." in GlobalVariables.file_output_textbox.GetValue():
        add_console_message("Output contains a file, not folder.\n", wx.RED)
        return False
    if "." in GlobalVariables.file_input_textbox.GetValue():
        add_console_message("Input contains a file, not folder.\n", wx.RED)
        return False

    return True


#
# Check if can UNPAK
#
def can_UNPAK():
    if len(GlobalVariables.file_input_textbox.GetValue()) == 0:
        add_console_message("Input is empty.\n", wx.RED)
        return False
    if len(GlobalVariables.file_output_textbox.GetValue()) == 0:
        add_console_message("Output is empty.\n", wx.RED)
        return False
    if "." in GlobalVariables.file_output_textbox.GetValue():
        add_console_message("Output contains a file, not folder.\n", wx.RED)
        return False
    if "." not in GlobalVariables.file_input_textbox.GetValue():
        add_console_message("Input contains a folder, not file.\n", wx.RED)
        return False

    return True


class QuantumPAK(wx.Frame):

    def __init__(self, *args, **kw):
        super(QuantumPAK, self).__init__(size=(400, 500), *args, **kw)

        self.SetTitle('QuantumModManager')
        self.Centre()
        self.init_gui()

    def init_gui(self):

        # Init Panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#333')

        # Set Font
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)

        # Set Font Size
        font.SetPointSize(9)

        # Set Overall BoxSizer Layout
        outer_box = wx.BoxSizer(wx.VERTICAL)


        ###########
        ## NAMES ##
        ###########
        name_horz = wx.BoxSizer(wx.HORIZONTAL)

        pak_text = wx.StaticText(panel, label='Input')
        pak_text.SetFont(font)
        pak_text.SetForegroundColour("#FFF")

        unpak_text = wx.StaticText(panel, label='Output')
        unpak_text.SetFont(font)
        unpak_text.SetForegroundColour("#FFF")

        name_horz.Add(pak_text, proportion=1)
        name_horz.Add(unpak_text, proportion=1)

        outer_box.Add(name_horz, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)


        ###########################
        ## Input Output Text Box ##
        ###########################
        text_ctrl_horz = wx.BoxSizer(wx.HORIZONTAL)

        # Input Text Box
        GlobalVariables.file_input_textbox = wx.TextCtrl(panel)
        GlobalVariables.file_input_textbox.SetValue(GlobalVariables.input_path)
        GlobalVariables.file_input_textbox.SetDropTarget(FileDropInput(panel))
        GlobalVariables.file_input_textbox.SetForegroundColour("#FFF")
        GlobalVariables.file_input_textbox.SetBackgroundColour("#333")

        # Output Text Box
        GlobalVariables.file_output_textbox = wx.TextCtrl(panel)
        GlobalVariables.file_output_textbox.SetValue(GlobalVariables.output_path)
        GlobalVariables.file_output_textbox.SetDropTarget(FileDropInput(panel))
        GlobalVariables.file_output_textbox.SetForegroundColour("#FFF")
        GlobalVariables.file_output_textbox.SetBackgroundColour("#333")

        text_ctrl_horz.Add(GlobalVariables.file_input_textbox, proportion=1)
        text_ctrl_horz.Add(GlobalVariables.file_output_textbox, proportion=1)

        outer_box.Add(text_ctrl_horz, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        #######################
        ## SELECTION BUTTONS ##
        #######################
        select_button_horz = wx.BoxSizer(wx.HORIZONTAL)

        # File Selection Button
        file_input_selection = wx.Button(panel, -1, "Select File")
        file_input_selection.Bind(wx.EVT_BUTTON, self.OpenInputSelector)
        file_input_selection.SetDropTarget(FileDropInput(panel))
        file_input_selection.SetForegroundColour("#FFF")
        file_input_selection.SetBackgroundColour("#333")

        # Folder Selection Button
        file_input_selection_f = wx.Button(panel, -1, "Select Folder")
        file_input_selection_f.Bind(wx.EVT_BUTTON, self.OpenInputSelectorFolder)
        file_input_selection_f.SetDropTarget(FileDropInput(panel))
        file_input_selection_f.SetForegroundColour("#FFF")
        file_input_selection_f.SetBackgroundColour("#333")

        # File Selection Button
        file_output_selection = wx.Button(panel, -1, "Select Folder")
        file_output_selection.Bind(wx.EVT_BUTTON, self.OpenOutputSelector)
        file_output_selection.SetDropTarget(FileDropOutput(panel))
        file_output_selection.SetForegroundColour("#FFF")
        file_output_selection.SetBackgroundColour("#333")

        select_button_horz.Add(file_input_selection, proportion=1)
        select_button_horz.Add(file_input_selection_f, proportion=1)
        select_button_horz.Add(file_output_selection, proportion=2)
        outer_box.Add(select_button_horz, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        #################
        ## DRAG AREAS ###
        #################
        drag_areas_horz = wx.BoxSizer(wx.HORIZONTAL)

        # Input Drag and Drop
        input_drag_box = wx.StaticBox(panel, label="Drag n' Drop")
        input_drag_box.SetDropTarget(FileDropInput(panel))
        input_drag_box.SetBackgroundColour("#333")
        input_drag_box.SetForegroundColour("#FFF")

        # Output Drag and Drop
        output_drag_box = wx.StaticBox(panel, label="Drag n' Drop")
        output_drag_box.SetDropTarget(FileDropOutput(panel))
        output_drag_box.SetBackgroundColour("#333")
        output_drag_box.SetForegroundColour("#FFF")

        drag_areas_horz.Add(input_drag_box, proportion=1, flag=wx.EXPAND)
        drag_areas_horz.Add(output_drag_box, proportion=1, flag=wx.EXPAND)
        outer_box.Add(drag_areas_horz, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)


        #######################
        ## PAK UNPAK Buttons ##
        #######################
        pak_horz = wx.BoxSizer(wx.HORIZONTAL)

        # PAK Button
        pakButton = wx.Button(panel, label='PAK', size=(100, 50))
        pakButton.Bind(wx.EVT_BUTTON, self.PAKEvent)
        pakButton.SetForegroundColour("#FFF")
        pakButton.SetBackgroundColour("#333")

        # UNPAK Button
        unpakButton = wx.Button(panel, label='UNPACK', size=(100, 50))
        unpakButton.Bind(wx.EVT_BUTTON, self.UNPAKEvent)
        unpakButton.SetForegroundColour("#FFF")
        unpakButton.SetBackgroundColour("#333")

        pak_horz.Add(pakButton, proportion=1)
        pak_horz.Add(unpakButton, proportion=1)
        outer_box.Add(pak_horz, flag=wx.EXPAND | wx.RIGHT | wx.LEFT | wx.BOTTOM, border=7)

        #############
        ## Console ##
        #############
        console_horz = wx.BoxSizer(wx.HORIZONTAL)

        console_text = wx.StaticText(panel, label='Console')
        console_text.SetFont(font)
        console_text.SetForegroundColour("#FFF")

        console_horz.Add(console_text)
        outer_box.Add(console_horz, flag=wx.LEFT | wx.TOP, border=10)

        console2_horz = wx.BoxSizer(wx.HORIZONTAL)
        GlobalVariables.console_textbox = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        GlobalVariables.console_textbox.SetBackgroundColour("#333")

        console2_horz.Add(GlobalVariables.console_textbox, proportion=1, flag=wx.EXPAND)
        outer_box.Add(console2_horz, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=10)


        # Add outer box to panel.
        panel.SetSizer(outer_box)

    #
    # On PAK Button Press
    #
    def PAKEvent(self, event):
        PAK()

    def UNPAKEvent(self, event):
        UNPAK()

    #
    # On --put Button Press
    #
    def OpenOutputSelector(self, event):
        dialog = wx.DirDialog(None, "Choose a directory/file:",
                              style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            GlobalVariables.output_path = dialog.GetPath()
            GlobalVariables.file_output_textbox.SetValue(GlobalVariables.output_path)
        dialog.Destroy()

    def OpenInputSelector(self, event):
        dialog = wx.FileDialog(None, "Choose a directory/file:",
                               style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON, wildcard="PAK files (*.pak)|*.pak")
        if dialog.ShowModal() == wx.ID_OK:
            GlobalVariables.input_path = dialog.GetPath()
            GlobalVariables.file_input_textbox.SetValue(GlobalVariables.input_path)
        dialog.Destroy()

    def OpenInputSelectorFolder(self, event):
        dialog = wx.DirDialog(None, "Choose a directory/file:",
                              style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            GlobalVariables.input_path = dialog.GetPath()
            GlobalVariables.file_input_textbox.SetValue(GlobalVariables.input_path)
        dialog.Destroy()


#
# Main Function.
#
def main():

    # Read or Create Config
    if os.path.isfile("Settings.ini"):
        json_data = json.load(open("Settings.ini", "r"))
        GlobalVariables.game_name = json_data["game_name"]
        GlobalVariables.input_path = json_data["input_path"]
        GlobalVariables.output_path = json_data["output_path"]
    else:
        json_data = {}
        json_data["game_name"] = "ReadyOrNot"
        json_data["input_path"] = ""
        json_data["output_path"] = ""
        json.dump(json_data, open("Settings.ini", "w"))



    # Create Visual
    app = wx.App()
    ex = QuantumPAK(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
