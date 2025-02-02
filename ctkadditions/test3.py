import ctypes
import win32gui
import win32con
import win32api

import customtkinter as ctk
from win32gui import EnableMenuItem

def disableCloseButton(hwnd):
    hMenu = win32gui.GetSystemMenu(hwnd, False)
    EnableMenuItem(hMenu, win32con.SC_CLOSE, win32con.MF_GRAYED)

def disableMinimizeButton(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_MINIMIZEBOX
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

def disableMaximizeButton(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_MAXIMIZEBOX
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

def test(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_CAPTION | win32con.WS_SYSMENU
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

root = ctk.CTk()
root.update()

hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

test(hwnd)

# disableMinimizeButton(hwnd)
# disableMaximizeButton(hwnd)
# disableCloseButton(hwnd)

root.mainloop()