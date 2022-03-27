import json, os, wx, requests, sys, re, shutil, subprocess
from py7zr import unpack_7zarchive
import wx.lib.agw.ultimatelistctrl as wxu


# -----------------------------------------------------------------------------------------------------------------------

class Info(wx.Frame):

    def __init__(self, *args, **kw):
        super(Info, self).__init__(size=(400, 250), *args, **kw)

        # Panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#333")

        right_panel_vert_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_horz = wx.BoxSizer(wx.HORIZONTAL)

        right_panel = wx.Panel(panel)

        #
        # Right Panel
        #

        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        font.SetPointSize(9)

        text = wx.StaticText(right_panel, label="Author")
        text.SetForegroundColour("#FFF")
        text.SetFont(font.Bold())
        right_panel_vert_sizer.Add(text)

        text = wx.StaticText(right_panel, label="QuantumNuke75")
        text.SetForegroundColour("#FFF")
        right_panel_vert_sizer.Add(text)


        right_panel.SetSizer(right_panel_vert_sizer)

        # Add left and right panels to main sizer
        outer_horz.Add(right_panel, 1, wx.EXPAND)
        outer_horz.Add((3, -1))

        # Add main sizer to main panel
        panel.SetSizer(outer_horz)

        # Final window changes
        self.SetTitle('Information')
        self.Centre()







