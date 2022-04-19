import json, os, wx, requests, sys, re, shutil, subprocess, datetime
from py7zr import unpack_7zarchive
import wx.lib.agw.ultimatelistctrl as wxu
import wx.lib.buttons as wxb
from wx.lib.embeddedimage import PyEmbeddedImage
import wx.lib.mixins.listctrl as listmix

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

        color = wx.Colour("#141414")

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

class ModManager(wx.Frame, listmix.ColumnSorterMixin):
    def __init__(self, *args, **kwds):
        kwds["style"] = style=wx.RESIZE_BORDER
        wx.Frame.__init__(self, *args, **kwds)

        shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)

        self.SetSize((750, 500))

        # Creting the custom title bar
        self.panelTitleBar = wx.Panel(self, wx.ID_ANY)
        self.btnMinimize = wx.Button(self.panelTitleBar, wx.ID_ANY, "", style=wx.BORDER_NONE | wx.BU_NOTEXT)
        self.btnMaximize = wx.Button(self.panelTitleBar, wx.ID_ANY, "", style=wx.BORDER_NONE | wx.BU_NOTEXT)
        self.btnExit = wx.Button(self.panelTitleBar, wx.ID_ANY, "", style=wx.BORDER_NONE | wx.BU_NOTEXT)
        self.panelBody = wx.Panel(self, wx.ID_ANY)

        self.Bind(wx.EVT_BUTTON, self.OnBtnExitClick, self.btnExit)
        self.Bind(wx.EVT_BUTTON, self.OnBtnMinimizeClick, self.btnMinimize)
        self.Bind(wx.EVT_BUTTON, self.OnBtnMaximizeClick, self.btnMaximize)
        self.panelTitleBar.Bind(wx.EVT_LEFT_DOWN, self.OnTitleBarLeftDown)
        self.panelTitleBar.Bind(wx.EVT_MOTION, self.OnMouseMove)


        self._isClickedDown = False
        self._LastPosition = self.GetPosition()


        self.__set_properties()
        self.__do_layout()

    def set_main(self, main):
        self.main = main
        self.setup_logic()

    def __set_properties(self):
        self.SetTitle("Quantum Mod Manager")
        self.btnMinimize.SetMinSize((22, 22))

        close_image = PyEmbeddedImage(
            b'iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAUfHpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHja1ZpZdiM7cobfsQovAXMAy8F4jnfg5fsLIMmSVFL1rbZfmjoSqWQyE4jhHwCa9T//vc1/8UgSs4lJSq45Wx6xxuobL4q9j3b+OhvP3/tPft5zn4+b9xueQ4HncP8tz3H3Ou7eF7hPjVfpw4XKeN7on9+o8bl++XKh50ZBR+R5MZ8L1edCwd833HOBdqdlcy3ycQp93efn8zcM/Br9I69R1/v89f8oRG8m7hO8X8EFy18fyh1A0F9vQuNF4K8P4s+hc8Sev/UZCQH5Lk7vB+eZrUON3570KSvvV+774+ZrtqJ/Tglfgpzfz98eNy59n5UT+g93juV55T8f99GlO6Iv0dffvWfZZ87MosVMqPMzqddUzivO69xCb10MQ8ukKVNDhWf9qfwUqnpQCtMO2/kZrjpPuraLbrrmtlvnebjBEKNfxpMr7/3w4Rws5K76QcZciPrjtpdQwwyFfA7SHjjq32Nx57bVDnPuVrjzdJzqHRdzpwj+8sf87Qf21lZwzpZ3rBiX9xpshqGZ07+cRkbcfoKaToBfP18fmtdABpNGWVukEth+L9GT+4UE4SQ6cGLi+fagk/lcgBBx68RgXCADZM2F5LKz4r04RyALCWoM3YfoOxlwKfnJIH0MIZOb4vXWfETcOdUnz2HDccCMTKSQg5CbGhrJijFRPxILNdRSSDGllJOkkmpqOeSYU85ZsoJikyDRSJIsIkWqtBJKLKnkIqWUWlr1NQCaqeYqtdRaW+OejSs3Pt04obXue+ixJ9Nzl1567W1QPiOONPKQUUYdbfoZJvgx85RZZp1tuUUprbjSyktWWXW1TantYHbcaectu+y62ztrT1p/+/mLrLkna/5kSk+Ud9Y4KvK6hFM4SZozEuYNzUvGNAUUtNec2eJi9Jo5zZmtnq5InkEmzdl0mjEyGJfzabtX7oy/GdXM/Z/yZiR+ypv/dzNnNHV/mbnf8/Zd1qbS0DgZu12oQbWB7tuhNl+a76OHRaEX/c++ns3XA//u83/6hXpsM4zQ20pgrU9j1lVmK2lEY3fl0Ai5rdUmyQ/ARLbb29Kc76Uln9xMvbvaY8pjE/ZB5S6qcTcnPWUFTW9q0LdKbWEv52AHr/9P22frAiW5WLV7ZliJ9Nede9y7Vpkrg2Nx1+Zq5h9TveMiUlYqs1BpoUEJbdgFstkdva81lm5P4qG8H58Btiawz+gC/4gdwfUBHxWQkUdEy9FDh4FbDTTuIFJZfh+9+Th8sN+WskvlYEmLyOxDAy3q8/K5bt/XiASmyR6jrx0cXTJ972bbtXrNjjCCmMwy09zULf0be0it01o0hIW3afNRLX2VawAJUEKAeQq9EKtkoOXxzzLfyXuuNt3k7FjBWPTXtnFLtWYk73MskwAzR5BllGV31tQv0CX2CrqQ59rTjoTTn+lWn+ed8Oykf7pB0zJb3/rWW8FZnOdz402avLc0tQg7cBbiLBLXDAgIruLdWKMQDTDMx+6WSQWFEGtboyVAxtY0K31eS86OEwKwBo/NtWUKsJHTuBDQECZj17hHmjoyg2TM/QwXkuxFh1kmNcVEAKE9QiKTc89FMqqAaGvXJWBrqm4zQE9UxhAwe9kACXhSKsAOoxguwTpkE0vgZ9sMalL2Y4c+lwf29gKAd02+rFhGALBmiiaJiwssTCvKjNl1VbhBXIs19DW5xBibYZ/5WKLwQ3GjRhpBseU0I8BJHyL8omfiHImMSQjv4H+La5FOOS6nsDyo15O3HuOqYsok0SAAReDoLFUhdJokWnLupO1zgkShDydVk75GXba6TCBPkIDx0RARtGdX2CACVDTlKrk6oB3Fp6JdfKP1X5NcbZ0iXYoGY3Hca7PUkI021DoiltA1UGF1WmZiwbR8MrkDh5ZGbweaKo+8tXz8EpWQK8Vy4rZM5joooF1OJy/U5Klc2FL2dpLGThmGFConzDL6ZurQHjOkxqiuvqqyUTAr99tIwB+NBC9WPkobZcaCKBPAI7lGz87WaF+cTtAgibQBx9HjQ+iQbNJghmnGp0GJuPay2q0vzwk2A4N2dRMpt3e35cIMxZPaMPmV/S+5hxA196GsVQqtOAKMHsJqT4tMXrvyxoduFMgapbxBlqdGmBhRpbVoVd7yAENd4I/WB9QgVLflgqCZNPChhcEZZky6RXOEJHATkKRuLhw4EnvhgDuCKxclSWnsvce6ht9ZLiYRNuMQrweS3Kkrq1LG0pTA8OqIgV/9/X17D0koluINJbwKCeRApCHRK+gdqI6iGCO/Wyy9WsvDRzqevXa2N7k70I3Gj5Nce8CAm8Vt1cMAaty8pCQrnI5qlsJaccbDgwwyh12iHpIIj2zDVAH7c2pwuWtWJjTsE5DYA1GEoMiDJZTIsNQQQIrZKDuylPqTpVDNbWXG3kjTxZwQW9M0dRqg4eC13cpqGiE5jQbrSU2KbAEZCNH0ICbUvB4ayfldjkLcydAtP421lt9QuiNu49SeE7m1t9RwRoOO25ReUNyQWv3kHAmx7yJux3ivrMbwJ6qinCmhaQAoNzCcBSzvrlvEKRXtaoINYf+ySkzhfIQ7aHSoosF9tvZ+Y6zFdU/cjHYRQG8V5im0qrmS3WCLCeJElQTgXoeZah0dlvWK7T7iUIHZJBB3okiXsU1bhLolERjbDE9whbagmzDcynmhpOnSJiA+KbSxg0CuSNbsjjU97FJXAkYgC2jGH1bogtwtY2cEbCfBOHKoeDLeKG1OwCeg0TuFEHdYayLgYsYp5GmSh5Si1iCqCdlGKXZ/5QHZBbu5awVXKzm+1Y1oLylHpg5W2D2RMT5OE3JJClsqidKck7EGT5XHxTHKBxKedArwVhd1lXXcsDW+QEamcKlbaH1348JW57booABijn0alPlSD3NqFzqwkQMgI2Qj9Dq2Vs+BfVBjrYoCcDeKdaFJR98pz2TKq8fQAXfJdC1QWvfSsrPax/GRYcJJVAMX8KdlXDfAbmNAcSllCYCGZ+hwBuBNBeMvpmwCzAQFdQq33dkkLpUvPcqZjhkKIZiVnYuGcHa0SAgoA7t4clB8uro3PZKYAU6GAY4MFYyZ5MxdsunI16nKoeNnKr8hMLSODN6qOrFDEJvrgqZRMJQtqvRaHQSLRAUKUD8zDEgBP0mDnhCQTZPhCcbuqidhA7AmjiueVTunxrTf/XNWBdqkH5NBhPvUtWQUx7VLjrZ0Ed15MMPDCU7lDpBmYUFRpfKh+DkQYnCmuaRDRmk7v5SCQGuuCDdQgVw5ZqEXPaJporOIEsU2UIEj7BnXymNxjOEbTEpTM+JXcpzpgdTiA5rUeZBN1p86/jT8KqBx2ubp2AIFBSHMx2w2yB9hhman6dD7qO9R2qdeUvFF5SBURp8zi6FyEspTCMhM6bQtupih047HVtAclM549xBBPbbC00KituJQ78Bmpb/2erQaCuawCQb8VBUIqUAMrW+MWUds9HjgzSqhqrYvaqIkAjz4DPH0FVbiQxjhqkWatnk5nBGuP8unXhN2TpVW8T3RuN2RMpBYHdrERVIm+xEURJ3CC5EROa44IclKr1FTBAO5zANQBXm04cCTnaBYLA4Xg31oI+CEolChf/nBAL9/9DLcMBFyOlTvR5gL4kArfY0sv5gimkzd6jozVjFI1vWQALsQKPo9qTQZKV4bU8/kJ12AfACZy+FnW0UUWcwq2V2HF7IGDkGD0tQHY6CSePJau6XO7X5xiS6ogplRL3WQyCRd8lYdSIOI36Sm0ayYq00ZrRjDiQBRa+1HVajP5qc3PjyDaEhvhBeoTL5pceoZEicGHEh9qKAyINqYlE7WZQBEKgIV5Yasc1hDGUhv1Ask2FRuHzDjnSoZyY5rh7cODuaEqgWXC4AnSTuoLnSmV7S78lSoKnyBaIARFFQX1TNpGDywF9cLBYguGMsAVIGyPpIOcFy/LEL+sS6IJgZgq4lZztKy4J8JhwloAMxhb7Q88IqV6YNeroJKRJKCygJxFgz8Rj2JEmnpeh4viQ9z6VR29VbrHWjumYT7Xkcejj/SFPjLfEnRVFUJhRmuAYt4PKqddvLM1sCkeMLGRyEiroghUpUKluii5COLBhhR/owJ5i8Wit5ZuBZRjl66mcAcn2QghmAtXdU8syf853QCeubfaS6B/8ChO32LT1r7Tn8KAtsWA7fdFZAC1SUYGlAHlsluQAZCFPp5SGMhLZCOYD0nTMTPTvgRXaBEiuAiDFflrRMcJICrKOTX4Hf7B6WgKxqaD7OfdABuNyHvdMAZW22ra3cVKysVviZN8uELJp1KUDESDLqt4t3RCcAqhNybrgCoFdkoBqbVJoK+J10tOEWLGq8gQty6zlZ2Vt0GYhrUz2JG6k2AEKgx4xNUlwAVXZUlxFtSAMHTvo4BuNB2hrZXt5eVUaXm9eLvnkFv+JBko/wYTqqqs48CXsgqHJCTnAckM6xT46rny83pbwtd7cBgplYONZmP3PSJmmgQgHeCkTQTCD28mmsS1WBkryt/aFSHJIb5t60GQYkFcKAT8jYH7aln4c+HhMsG1t7SBZJNitW1KelB71teQtebn101N/RFb4jcprzCe0WwZkrO86gqf4Gzs7+mq4Lnhl67oymTUkibmT+SLypOqhLBwh4lYtOjRIICjWQ0DByMqsVPa2HMjjKnRpFYRRXO2XLSNROkGXAk+8/kZIaKeyxBn4BJQoJmhx2f6pAdmH88WWhvMPmxVcx3b6gFo2V1iVMXTbWOsRU26obC4fG7S7wIt27Ugp9q19O2XWgrRxnHrAOktAia8wDOAOg7DXx8S3W6F+miV0NK96+LSLfGzLdFthDYwMuN4z6GAUrSO8hVOWhXUUPI9dMYbek2vaN9qJfjvvxW96XLUFkJnSKhVEn9NV/YXKcWvl93hwIWJekFjlkxNAI+LGW4FLDWzsFP6D4P7p3hz64dirrQtdkGjGbUaNaFKrQhub9lB3qYU5qj1o56eXR6LJmSkJdO10VuJPGj05EuDnXtIszbMfKBwPWc1K4LoQJJ5WUkOIC0tekxEtwX8HXuGImcqe6kuFWmnPXf/ihnmjZQJwR57vYs26+UBtjoGs6zt4OPqNiNB0UmQx4gGgrgLHHSLx0Zzzhg2qhkYGEJtHM9Wgc8bxndfF2XVfWvrqu1GB7X1ZIuFa91Ftm566qGQcg6aQ81zXUWZx3sqLQBsoCoWGo/vVdmr7o+NpY2JBnageQMGB2FuIyUtpGwxe87E26Vac1cls4jC4VQHR+fjnlAa+rgVYVAbDTjPvYcUV9RIxNfv3X8uMaqTozxc0YUykTBxG4Sh4d57S40nGn91TTYqdFJv7tfbUBKvORvVAzJ6nGi0DBv6HIJ818KsJjVyPgwYZDw6ihzWkppGNl73EtT2rDJUsst0I9oq4SVSxi2rEubCDcgD+/IMAa6jwrRZjXhLFxHpS5dxtRu5X9Ib6pfw+diyqr7XO40la6bqzDs8Syn6BdQhPqZSigPn6AbevYl2buiEnV7RXRFRT95VwW+4xTz9DuCKHpdMIFSY8VIeaQpqiwpUW94xZ+tFNEVIlwA7utNGfCYm85MOktl9Isw4jhI+A/UUsbNUIW6qlhwkFsXFQ+YU3hddw3+uCZ7Fj0dxVZQ91T8RPBr/4tpWfegPjKyuGOq8Sitia4qBaf8QMHBAXWJABQFiY34lgHD4SUpQXO2ENLdksFIt4QZVykdfSDa8O2/XBvtZ/HVWGTaQL/v6Oo1l4oSuOWGwFVvI6gfBoK1SZu0hVEm9hZ6CxICCiEAUnZFo6oRs5ygeYwiyqUKNrLhbeDBQLUfWTS+MzfIw19ro0Zx5be10V0ttaCjsX3Sz14XYbBUsXSvi/5Wcvd16I7lUMyXhoVQc5uJqu7GlBAuj/bDHFAUipOYN1tJSlVfr6NFBTpB/sWzvMB4AS5Tb5oogSdNSMPgzp5dB8Vm80IGM2isaYoo+Bi9ruhbp1tMtGJSwgOzdXthCW7a6+q4Gtf5VMMY7/XQd+peiXvSdqrv7FkZyu8Pa7KgMvQVMKS0ll1hlcdJxFQ+q0HzQR5ycsHR4QCITgAsyKAirNVwo8DRNzR1ghrAHl31Ju1UNp7SqobU9akwcPDwEXokPLH3+4k9kQ9XDyHZ/NJ156nkiw9CpawKT1Yo0+hKJ2SXoPkCaJAC61ZDEY2zWfeHXUeNcmy6UeAVahf1CTIstdfIJyiyTyQ4HDN0jeCaCMpFVGr3w6XOaXlV6GQBM7oF4Xwwulgt2mPMvkZsDnrtFBkVb0Hmqpw68KhAhh0qqQleK6+6QJzqFlB1Bp/nYPRQc7Jwo226p/Bl9fzT4rnTZUfsgr8bhHimgLhrBhve19bNs/LLLf4IZ1vJPHVdC8PwXYwRZd5udAuG6odjaVOC7TXLoAz1gAZ4bRowiFd4tnbfWCqF7o7I2RARcyCoowvXgRBFhK0gRIYfLL04VNILh84aAGDaySeOjFgRx2pGx/6jrxoeE4kR7wffm1aMhKqsq/VTPoXmHbMpn1M+cDrVLkOrx3QHh0LFNDhaIkk4dz5wh137AHdnNwDOfO86ft50NGfXkWsoivtEgLiyLF2r0RW/sTIGFlmhGihqD1FVx0Wr8udTiNOx8d7VgKGIDsZHHLntqPZsZg1lVG0jGJ9rIebD2Z5BPLRXd37aKzHfc9b5WkfEVNLkurJDGXbKkADbCie7GCSiDTp6RkUIpWt8rLorCV4BuY9WaOv1tQ6k1/1aR5H7tY75yMN2vtXh1/t7Eea3ZcP7JY66RTtHwSDBHiCb7rvp1yL8e3mQGtCHO3sNZr0WB+uhzH/yzQ5a7ywDorv0C4ThCAAzEADU1xUAimHhCgA+Es7XOj4M/+volRmfRb9l3ot+9i776YZl61d5kFj8BA2zVfL2oitmMEvufJIoHiIfC0ftLHgU1J2gGju1TX9khD3wU2CboGgE4B59r9LF928zf57N/8+Xhv6TL4Q2mNX8LwafAwRdd319AAABhGlDQ1BJQ0MgcHJvZmlsZQAAeJx9kT1Iw0AcxV/TiiIVB4uIdMhQnSxIFXGUKhbBQmkrtOpgcukXNGlIUlwcBdeCgx+LVQcXZ10dXAVB8APE0clJ0UVK/F9SaBHjwXE/3t173L0DhGaVqWZgElA1y0gn4mIuvyr2vsKPMAKIYVhipp7MLGbhOb7u4ePrXZRneZ/7cwwoBZMBPpF4jumGRbxBPLNp6Zz3iUOsLCnE58QTBl2Q+JHrsstvnEsOCzwzZGTT88QhYrHUxXIXs7KhEk8TRxRVo3wh57LCeYuzWq2z9j35C4MFbSXDdZphJLCEJFIQIaOOCqqwEKVVI8VEmvbjHv5Rx58il0yuChg5FlCDCsnxg//B727N4lTMTQrGgZ4X2/4YA3p3gVbDtr+Pbbt1AvifgSut4681gdlP0hsdLXIEDG4DF9cdTd4DLneAkSddMiRH8tMUikXg/Yy+KQ8M3QL9a25v7X2cPgBZ6mr5Bjg4BMZLlL3u8e6+7t7+PdPu7weasXK3FRMmAgAADRhpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+Cjx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDQuNC4wLUV4aXYyIj4KIDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIKICAgIHhtbG5zOkdJTVA9Imh0dHA6Ly93d3cuZ2ltcC5vcmcveG1wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgogICB4bXBNTTpEb2N1bWVudElEPSJnaW1wOmRvY2lkOmdpbXA6NmM1N2IwMWEtYmViMS00YjBkLWE2NDQtNWYwYzdiMDAwYjUwIgogICB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOmFjMDU2ZjhiLWMyNmYtNDljYy1iNWZiLWZkMDI1NzA4MWJlYiIKICAgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOmYyMmY2YWYxLWUzN2QtNGI4Yy1iZGU5LTcwNjIzMDU1OTg1YyIKICAgZGM6Rm9ybWF0PSJpbWFnZS9wbmciCiAgIEdJTVA6QVBJPSIyLjAiCiAgIEdJTVA6UGxhdGZvcm09IldpbmRvd3MiCiAgIEdJTVA6VGltZVN0YW1wPSIxNjQ4NDQzNjA5MzIxMjE4IgogICBHSU1QOlZlcnNpb249IjIuMTAuMjgiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiCiAgIHhtcDpDcmVhdG9yVG9vbD0iR0lNUCAyLjEwIj4KICAgPHhtcE1NOkhpc3Rvcnk+CiAgICA8cmRmOlNlcT4KICAgICA8cmRmOmxpCiAgICAgIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiCiAgICAgIHN0RXZ0OmNoYW5nZWQ9Ii8iCiAgICAgIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6MzNhMDk5NjgtMGZhMC00MjM4LThlOTMtYTRlYTU5NzE2ZmRhIgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJHaW1wIDIuMTAgKFdpbmRvd3MpIgogICAgICBzdEV2dDp3aGVuPSIyMDIyLTAzLTI3VDIyOjAwOjA5Ii8+CiAgICA8L3JkZjpTZXE+CiAgIDwveG1wTU06SGlzdG9yeT4KICA8L3JkZjpEZXNjcmlwdGlvbj4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PpNtytUAAAAGYktHRACZABEAEVIBF6sAAAAJcEhZcwAAAcAAAAHAAZfCvt0AAAAHdElNRQfmAxwFAAkusbqHAAAAe0lEQVQ4y+1VQQrAIAyz+YE+0j/NR/YL2wdamwplMOZJJImhJihX73crWGhF6yPCU7VN1ZC8w8ECW/ssDowr5iwUXmOk3Vkc8XLMuPJEt6PwCCwGp8To4ncKwsYtJcwWJN08a6ZRFOnmWQ/FiuMkUkwUkXXH4uT/QcqFH5+FQWCB/fM1AAAAAElFTkSuQmCC')
        minimize_image = PyEmbeddedImage(
            b'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UhAho44KqrAQpVUjxUSa9uMe/lHHnyKXTK4KGDkWUIMKyfGD/8Hvbs3iVMxNCsaBnhfb/hgDeneBVsO2v49tu3UC+J+BK63jrzWB2U/SGx0tcgQMbgMX1x1N3gMud4CRJ10yJEfy0xSKReD9jL4pDwzdAv1rbm/tfZw+AFnqavkGODgExkuUve7x7r7u3v490+7vB5qxcrcVEyYCAAANGGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNC40LjAtRXhpdjIiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iCiAgICB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIgogICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICAgeG1sbnM6R0lNUD0iaHR0cDovL3d3dy5naW1wLm9yZy94bXAvIgogICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iCiAgICB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iCiAgIHhtcE1NOkRvY3VtZW50SUQ9ImdpbXA6ZG9jaWQ6Z2ltcDpjZGY1YWU5NC1lMDZhLTQ3ZjAtOTY4MS05N2Y1NGQ4ZTNkMzQiCiAgIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OWRmZTViYWEtYjBmOC00N2EyLWE0YTgtNDhiNDViMGFkZGU2IgogICB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6MzJmMDFlZWQtODVhOC00MzcyLTgwMmUtMGFjMmMxNDI4OWJkIgogICBkYzpGb3JtYXQ9ImltYWdlL3BuZyIKICAgR0lNUDpBUEk9IjIuMCIKICAgR0lNUDpQbGF0Zm9ybT0iV2luZG93cyIKICAgR0lNUDpUaW1lU3RhbXA9IjE2NDg0NDM1MDI2NDE4NzkiCiAgIEdJTVA6VmVyc2lvbj0iMi4xMC4yOCIKICAgdGlmZjpPcmllbnRhdGlvbj0iMSIKICAgeG1wOkNyZWF0b3JUb29sPSJHSU1QIDIuMTAiPgogICA8eG1wTU06SGlzdG9yeT4KICAgIDxyZGY6U2VxPgogICAgIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9uPSJzYXZlZCIKICAgICAgc3RFdnQ6Y2hhbmdlZD0iLyIKICAgICAgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo5MzliOTU4Yi1mNTU2LTRjYWEtYWZkZS01NWIyNDY5ZTI3OTciCiAgICAgIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkdpbXAgMi4xMCAoV2luZG93cykiCiAgICAgIHN0RXZ0OndoZW49IjIwMjItMDMtMjdUMjE6NTg6MjIiLz4KICAgIDwvcmRmOlNlcT4KICAgPC94bXBNTTpIaXN0b3J5PgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+w+xlTQAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAABwAAAAcABl8K+3QAAAAd0SU1FB+YDHAQ6FofSAzwAAAA1SURBVDjLY5wpKPifgQaAiYFGYNTgUYNHDR41eEANZoEx0t69o4qBs4SERsMYFTCOVk0wAACmXQahg0moYwAAAABJRU5ErkJggg==')
        maximize_image = PyEmbeddedImage(
            b'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ZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIKICAgIHhtbG5zOkdJTVA9Imh0dHA6Ly93d3cuZ2ltcC5vcmcveG1wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgogICB4bXBNTTpEb2N1bWVudElEPSJnaW1wOmRvY2lkOmdpbXA6ZjYwYmMzNjktMTg0OC00YzhhLTgxMjAtMzY5NmYxNTk5YjFjIgogICB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOmU2MzZmMTkyLWQ1Y2YtNDA0ZS05NWUzLTZiZGYzZDJiMjg5OSIKICAgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjc2NjMzYjA3LTgxMzMtNDBiMS1iYWY5LTlhNWI3ZGQxN2ZkNyIKICAgZGM6Rm9ybWF0PSJpbWFnZS9wbmciCiAgIEdJTVA6QVBJPSIyLjAiCiAgIEdJTVA6UGxhdGZvcm09IldpbmRvd3MiCiAgIEdJTVA6VGltZVN0YW1wPSIxNjQ4NDQzNjA2NTM5NTkwIgogICBHSU1QOlZlcnNpb249IjIuMTAuMjgiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiCiAgIHhtcDpDcmVhdG9yVG9vbD0iR0lNUCAyLjEwIj4KICAgPHhtcE1NOkhpc3Rvcnk+CiAgICA8cmRmOlNlcT4KICAgICA8cmRmOmxpCiAgICAgIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiCiAgICAgIHN0RXZ0OmNoYW5nZWQ9Ii8iCiAgICAgIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6NDY1ZDM0MGQtNjIwZi00YWFiLTg4MDgtYTNlZTMzMDI4MDdiIgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJHaW1wIDIuMTAgKFdpbmRvd3MpIgogICAgICBzdEV2dDp3aGVuPSIyMDIyLTAzLTI3VDIyOjAwOjA2Ii8+CiAgICA8L3JkZjpTZXE+CiAgIDwveG1wTU06SGlzdG9yeT4KICA8L3JkZjpEZXNjcmlwdGlvbj4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/Po6iXAsAAAAGYktHRACZABEAEVIBF6sAAAAJcEhZcwAAAcAAAAHAAZfCvt0AAAAHdElNRQfmAxwFAAa+DqcWAAAAY0lEQVQ4y2OcKSj4n4EGgImBRoBmBrMgc4Ifv2DgYmMmy6Bvv/4yrJWVwG4wFxszAycr8xAKCmQwS0iIKAPS3r0bJqli1OBRgwdDzsOVowaXi7/9+ku2Qeh6UQxGLk9HXqoAANqxFBRCJ3Z2AAAAAElFTkSuQmCC')

        self.btnMinimize.SetBitmap(minimize_image.Bitmap)
        self.btnMaximize.SetMinSize((22, 22))
        self.btnMaximize.SetBitmap(maximize_image.Bitmap)
        self.btnExit.SetMinSize((22, 22))
        self.btnExit.SetBitmap(close_image.Bitmap)
        self.panelTitleBar.SetBackgroundColour(wx.Colour("#911"))
        self.panelBody.SetBackgroundColour(wx.Colour("#252525"))


    def GetListCtrl(self):
        return self.mod_selector


    def __do_layout(self):

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)
        title_bar_sizer = wx.FlexGridSizer(1, 5, 0, 0)

        #iconTitleBar = wx.StaticBitmap(self.panelTitleBar, wx.ID_ANY, wx.Bitmap("images\\icon.ico", wx.BITMAP_TYPE_ANY))
        #title_bar_sizer.Add(iconTitleBar, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        title_bar_sizer.Add((1,1), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        title = wx.StaticText(self.panelTitleBar, wx.ID_ANY, "Quantum Mod Manager")
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        title_bar_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.TOP, 10)
        title_bar_sizer.Add(self.btnMinimize, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        title_bar_sizer.Add(self.btnMaximize, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        title_bar_sizer.Add(self.btnExit, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        title_bar_sizer.AddGrowableRow(0)
        title_bar_sizer.AddGrowableCol(1)

        self.panelTitleBar.SetSizer(title_bar_sizer)
        grid_sizer_1.Add(self.panelTitleBar, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.panelBody, 1, wx.EXPAND, 0)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        ##############################
        # Start customizable section #
        ##############################

        self.current_version = 3.4

        self.current_item = None
        self.previous_item = None

        # body_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        # body_sizer.Add(wx.Button(self.panelBody, label="Hello"))

        outer_horz_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panelBody.SetSizer(outer_horz_sizer)

        right_panel_vert_sizer = wx.BoxSizer(wx.VERTICAL)

        #Create Panels
        self.left_panel = wx.Panel(self.panelBody)
        self.right_panel = wx.Panel(self.panelBody)

        ##############
        # Left Panel #
        ##############

        left_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # QMM Font
        qmm_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        qmm_font.SetPointSize(16)

        text = wx.StaticText(self.left_panel, label="", style=wx.ALIGN_CENTER)
        left_panel_sizer.Add(text, 1, wx.BOTTOM)

        self.left_panel.SetSizer(left_panel_sizer)

        ###############
        # Right Panel #
        ###############

        right_panel_vert_sizer.Add((-1, 10))

        self.create_mods_text(right_panel_vert_sizer)

        # Add mod selector.
        self.create_mod_selector()
        right_panel_vert_sizer.Add(self.mod_selector, 4, wx.EXPAND | wx.TOP, 3)

        #
        # Mod Settings
        #
        mod_settings_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.create_mod_settings(mod_settings_sizer)
        right_panel_vert_sizer.Add(mod_settings_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        self.create_profiles_text(right_panel_vert_sizer)

        self.create_profile_selector()
        right_panel_vert_sizer.Add(self.profile_selector, 4, wx.EXPAND | wx.BOTTOM, 3)

        #
        # Profile Buttons
        #
        profile_options = wx.BoxSizer(wx.HORIZONTAL)
        self.create_profile_settings(profile_options)
        right_panel_vert_sizer.Add(profile_options, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)


        bottom_buttons = wx.BoxSizer(wx.HORIZONTAL)
        button_color = wx.Colour("#141414")
        # Change Game Path button.
        game_path_button = wx.Button(self.right_panel, label='Change Game Path', size=(-1, 30))
        game_path_button.SetBackgroundColour(button_color)
        game_path_button.SetForegroundColour(wx.Colour(text_color))

        # Run Ready or Not Button
        run_ready_or_not = wx.Button(self.right_panel, label='Run Ready or Not', size=(-1, 30))
        run_ready_or_not.SetBackgroundColour(button_color)
        run_ready_or_not.SetForegroundColour(wx.Colour(text_color))

        game_path_button.Bind(wx.EVT_BUTTON, self.OnChangeGamePath)
        run_ready_or_not.Bind(wx.EVT_BUTTON, self.OnRunReadyOrNot)

        bottom_buttons.Add(game_path_button, proportion=1)
        bottom_buttons.Add(run_ready_or_not, proportion=1)


        right_panel_vert_sizer.Add(bottom_buttons, flag=wx.EXPAND)
        right_panel_vert_sizer.Add((-1, 10))

        #
        # Version Warning
        #
        warning_pane = wx.BoxSizer(wx.HORIZONTAL)
        self.create_warning_message(warning_pane)
        right_panel_vert_sizer.Add(warning_pane, flag=wx.EXPAND)

        self.right_panel.SetSizer(right_panel_vert_sizer)

        # Add left and right panels to main sizer
        outer_horz_sizer.Add(self.left_panel, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        outer_horz_sizer.Add(self.right_panel, 1, wx.EXPAND | wx.RIGHT, 5)
        outer_horz_sizer.Add((3, -1))

        listmix.ColumnSorterMixin.__init__(self, 5)
        self.SetSizer(sizer_1)
        self.Layout()



    def setup_logic(self):
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


    def create_mod_selector(self):
        self.mod_selector = wxu.UltimateListCtrl(self.right_panel, agwStyle=wx.LC_REPORT | wxu.ULC_NO_HIGHLIGHT | wxu.ULC_SINGLE_SEL)
        self.mod_selector.Bind(wx.EVT_MOTION, self.OnMouseOver)
        self.mod_selector.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        #self.mod_selector._mainWin.ShowScrollbars(horz=wx.SHOW_SB_DEFAULT, vert=wx.SHOW_SB_DEFAULT)

        self.mod_selector.SetForegroundColour(wx.Colour(text_color))
        self.mod_selector.SetBackgroundColour(wx.Colour("#141414"))
        self.mod_selector.SetTextColour(wx.Colour(text_color))

        self.mod_selector.InsertColumn(0, 'Mod', width=200)
        self.mod_selector.InsertColumn(1, 'Category')
        self.mod_selector.InsertColumn(2, 'Size')
        self.mod_selector.InsertColumn(3, 'Full Name', width=240)
        self.mod_selector.InsertColumn(4, 'Created')

        self.mod_selector.SetHeaderCustomRenderer(UltimateHeaderRenderer(self.mod_selector))
        self.mod_selector.SetDropTarget(ModFileDrop(self.right_panel, self))

        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnHeaderClick, self.mod_selector)


    def create_profile_selector(self):
        self.profile_selector = wxu.UltimateListCtrl(self.right_panel, agwStyle = wx.LC_REPORT | wxu.ULC_NO_HEADER | wxu.ULC_SINGLE_SEL)

        self.profile_selector.SetForegroundColour(wx.Colour(text_color))
        self.profile_selector.SetBackgroundColour(wx.Colour("#141414"))
        self.profile_selector.SetTextColour(wx.Colour(text_color))

        self.profile_selector.InsertColumn(0, 'Profile')
        self.profile_selector.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnProfileClick)


    def create_mod_settings(self, mod_settings_sizer):

        button_color = wx.Colour("#141414")

        select_all_mod = wx.Button(self.right_panel, label='Select All')
        select_all_mod.SetBackgroundColour(button_color)
        select_all_mod.SetForegroundColour(wx.Colour(text_color))

        deselect_all_mod = wx.Button(self.right_panel, label='Deselect All')
        deselect_all_mod.SetBackgroundColour(button_color)
        deselect_all_mod.SetForegroundColour(wx.Colour(text_color))

        refresh_mod = wx.Button(self.right_panel, label='Refresh')
        refresh_mod.SetBackgroundColour(button_color)
        refresh_mod.SetForegroundColour(wx.Colour(text_color))

        apply_mod = wx.Button(self.right_panel, label='Apply Changes')
        apply_mod.SetBackgroundColour(button_color)
        apply_mod.SetForegroundColour(wx.Colour(text_color))

        select_all_mod.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        deselect_all_mod.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        refresh_mod.Bind(wx.EVT_BUTTON, self.OnRefresh)
        apply_mod.Bind(wx.EVT_BUTTON, self.OnApply)

        mod_settings_sizer.Add(select_all_mod, flag=wx.ALIGN_CENTER, proportion=1)
        mod_settings_sizer.Add(deselect_all_mod, flag=wx.ALIGN_CENTER, proportion=1)
        mod_settings_sizer.Add(refresh_mod, flag=wx.ALIGN_CENTER, proportion=1)
        mod_settings_sizer.Add(apply_mod, flag=wx.ALIGN_CENTER, proportion=1)

    def create_profile_settings(self, profile_options):

        button_color = wx.Colour("#141414")

        # Load Profile Button
        load_profile = wx.Button(self.right_panel, label="Load Profile")
        load_profile.SetBackgroundColour(button_color)
        load_profile.SetForegroundColour(wx.Colour(text_color))

        # Save Profile Button
        save_profile = wx.Button(self.right_panel, label="Save Profile")
        save_profile.SetBackgroundColour(button_color)
        save_profile.SetForegroundColour(wx.Colour(text_color))

        # Delete Profile Button
        delete_profile = wx.Button(self.right_panel, label="Delete Profile")
        delete_profile.SetBackgroundColour(button_color)
        delete_profile.SetForegroundColour(wx.Colour(text_color))

        # Profile Name Input
        self.profile_textctrl = wx.TextCtrl(self.right_panel, style=wx.BORDER_DOUBLE)
        self.profile_textctrl.SetForegroundColour(wx.Colour("#FFF"))
        self.profile_textctrl.SetBackgroundColour(wx.Colour("#141414"))

        # Bind buttons to functions.
        load_profile.Bind(wx.EVT_BUTTON, self.OnLoadProfile)
        save_profile.Bind(wx.EVT_BUTTON, self.OnSaveProfile)
        delete_profile.Bind(wx.EVT_BUTTON, self.OnDeleteProfile)

        # Add all items to sizer.
        profile_options.Add(load_profile)
        profile_options.Add(save_profile)
        profile_options.Add(delete_profile)
        profile_options.Add(self.profile_textctrl, proportion=1)


    def create_warning_message(self, warning_pane):
        try:
            # Send a response to the page with the version number.
            response = requests.get('https://unofficial-modding-guide.com/tools.html')
            # If we got a response back.
            if response is not None and str(response.reason) == "OK":
                # Get the version from the striped HTML.
                version = float(str(response.content).split("Quantum Mod Manager")[1][2:5])
                # If out version is lower, show update button.
                if version > self.current_version:
                    self.newest_version = version
                    warning_message = wx.StaticText(self.right_panel,
                                                    label="Version Outdated: https://unofficial-modding-guide.com/downloads/QuantumModManager.exe")
                    warning_message.SetForegroundColour(wx.Colour(text_color))

                    warning_button = wx.Button(self.right_panel, label="Download")
                    warning_button.SetForegroundColour(wx.Colour(text_color))
                    warning_button.SetBackgroundColour(wx.Colour("#141414"))

                    warning_button.Bind(wx.EVT_BUTTON, self.OnDownloadLatest)

                    warning_pane.Add(warning_message, flag=wx.TOP, border=7)
                    warning_pane.Add(warning_button, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, border=5)
        except:
            ...



    def create_profiles_text(self, right_panel_vert_sizer):
        header_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        header_font.SetPointSize(12)

        right_panel_vert_sizer.Add((-1, 10))
        profiles_text = wx.StaticText(self.right_panel, label="Profiles")
        profiles_text.SetForegroundColour(wx.Colour(text_color))
        profiles_text.SetFont(header_font.Bold())
        right_panel_vert_sizer.Add(profiles_text)

    def create_mods_text(self, right_panel_vert_sizer):
        header_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        header_font.SetPointSize(12)

        mods_text = wx.StaticText(self.right_panel, label="Mods")
        mods_text.SetForegroundColour(wx.Colour(text_color))
        mods_text.SetFont(header_font.Bold())
        right_panel_vert_sizer.Add(mods_text)



    #
    # Refresh Mods List
    #
    def refresh_mods(self):
        mods_list = []

        # Get list of all mods as a file path.
        mods = helper_functions.get_mods(self.main)

        for mod_path in mods:

            # Vars
            mod_path_without_old = mod_path.replace(".old", "")
            mod_path_with_old = mod_path_without_old + ".old"
            regex_prepped_name = self.get_regex_prep_name(mod_path)
            regexed_name = self.get_regex_name(regex_prepped_name)
            category = self.get_category(mod_path)
            full_name_without_old = mod_path_without_old.split("\\")[-1]
            full_name_with_old = mod_path_with_old.split("\\")[-1]
            time = os.path.getctime(mod_path)
            size = str(round(os.path.getsize(mod_path) / 1000000, 2)) + " MB"

            # Check for duplicates.
            if os.path.exists(mod_path_without_old) and os.path.exists(mod_path_with_old):
                # Remove likely older version.
                os.remove(mod_path_with_old)

                # Check if we are on the older version, if so, skip. Eventually, we should read metadata to ensure which
                # file is older / younger.
                if mod_path == mod_path_with_old:
                    continue


            # name category size fullname, date
            mods_list.append( (
                (regexed_name if len(regexed_name) > 0 else regex_prepped_name), #name
                str(category), #category
                size, #size
                full_name_without_old, # full name
                str(datetime.datetime.fromtimestamp(time).strftime('%d-%m-%Y')) #date
                )
            )

        # Remove all the items from the list so we can add them back.
        self.mod_selector.DeleteAllItems()

        # Sorts mod by alphabetized.
        mods_list = sorted(mods_list)

        for rowIndex, data in enumerate(mods_list):
            for colIndex, coldata in enumerate(data):
                if colIndex == 0:
                    self.mod_selector.InsertStringItem(rowIndex, coldata, it_kind=1)

                    # If the file is enabled.
                    if helper_functions.is_file_enabled(data[3], data[1], self.main):
                        item = self.mod_selector.GetItem(rowIndex, 0)
                        item.Check(True)
                        self.mod_selector.SetItem(item)
                else:
                    self.mod_selector.SetStringItem(rowIndex, colIndex, coldata)
            self.mod_selector.SetItemData(rowIndex, data)

        self.itemDataMap = {data: data for data in mods_list}


    def get_regex_prep_name(self, mod_path):
        name = mod_path.split("\\")[-1]  # Get file name with extension.
        name = name.split("-", maxsplit=1)[-1]  # Get file name without pakchunk99
        name = name.split(".")[0]  # Remove extenstion
        name = name.replace("_P", "")  # Remove patch file modifier.
        name = name.replace("Mods", "")  # Remove mods.
        name = name.replace("_", "")  # Remove left over _'s
        name = name.replace("-", "")  # Remove left over -'s
        name = name.replace(" ", "")  # Prepare for camelcase regex.
        return name


    def get_regex_name(self, regex_prepped_name):
            name_list = re.findall(r'[A-Z,0-9](?:[a-z]+|[A-Z,0-9]*(?=[A-Z,0-9]|$))', regex_prepped_name)
            final_name = ""
            for item in name_list:
                final_name += item + " "
            final_name.strip(" ")
            return final_name


    def get_category(self, mod_path):
            category = mod_path.split("Paks")[1]
            category = category.split("\\")
            if ".pak" in category[1]:
                category = None
            else:
                category = category[1]
            return category


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


    ###################
    # Interact Events #
    ###################
    def OnMouseLeave(self, event):
        if self.current_item is not None:
            self.mod_selector.SetItemBackgroundColour(self.current_item, wx.Colour(wx.Colour("#141414")))


    def OnMouseOver(self, event):
        x = event.GetX()
        y = event.GetY()

        item, flags = self.mod_selector.HitTest((x, y))
        if item < 0:
            if self.previous_item is not None:
                self.mod_selector.SetItemBackgroundColour(self.previous_item, wx.Colour(wx.Colour("#141414")))
            if self.current_item is not None:
                self.mod_selector.SetItemBackgroundColour(self.current_item, wx.Colour(wx.Colour("#141414")))
            return

        if item is self.previous_item:
            return

        self.previous_item = self.current_item
        self.current_item = item

        if self.previous_item is not None:
            self.mod_selector.SetItemBackgroundColour(self.previous_item, wx.Colour(wx.Colour("#141414")))
        self.mod_selector.SetItemBackgroundColour(item, wx.Colour("#911"))


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
                helper_functions.enable_mod(self.mod_selector.GetItem(i, col=3).GetText(), self.mod_selector.GetItem(i, col=1).GetText(), self.main)
            else:
                helper_functions.disable_mod(self.mod_selector.GetItem(i, col=3).GetText(), self.mod_selector.GetItem(i, col=1).GetText(), self.main)

    def OnHeaderClick(self, event):
        pass


    def OnLoadProfile(self, event):
        profile_name = self.profile_textctrl.GetValue()
        if profile_name == "":
            return

        self.refresh_mods()

        file = open("Profiles\\" + profile_name + ".json", "r")
        enabled_mods = json.load(file).keys()

        for i in range(self.mod_selector.GetItemCount()):
            if self.mod_selector.GetItem(i, col=3).GetText() in enabled_mods:

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
                mods_dict[self.mod_selector.GetItem(i, col=3).GetText()] = True
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
        url = 'https://github.com/QuantumNuke75/Unofficial-Modding-Guide/raw/gh-pages/downloads/QuantumModManager.exe'
        r = requests.get(url, stream=True)
        with open(f"QuantumModManager v{self.newest_version}.exe", "wb") as exe:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    exe.write(chunk)

        sys.exit()


    ###########################
    # IMPORTANT WINDOW EVENTS #
    ###########################
    def OnTitleBarLeftDown(self, event):
        self._LastPosition = event.GetPosition()

    def OnBtnExitClick(self, event):
        self.Close()

    def OnBtnMinimizeClick(self, event):
        self.Iconize( True )

    def OnBtnMaximizeClick(self, event):
        self.Maximize(not self.IsMaximized())

    def OnMouseMove(self, event):
        if event.Dragging():
            mouse_x, mouse_y = wx.GetMousePosition()
            self.Move(mouse_x-self._LastPosition[0],mouse_y-self._LastPosition[1])





