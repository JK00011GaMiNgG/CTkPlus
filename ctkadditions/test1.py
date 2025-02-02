import ctypes
from tkinter import *

import win32gui
import win32api
import win32con

_titlebar_cxt_menu_item_id = 0
_titlebar_cxt_menu_commands = {}

def add_button(hwnd, text, command):
    global _titlebar_cxt_menu_item_id
    h_menu = win32gui.GetSystemMenu(hwnd, False)
    _titlebar_cxt_menu_commands[_titlebar_cxt_menu_item_id] = command
    win32gui.InsertMenu(h_menu, _titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION | win32con.MF_STRING, _titlebar_cxt_menu_item_id, text)
    _titlebar_cxt_menu_item_id += 1
    if _titlebar_cxt_menu_item_id > 1:
        win32gui.RemoveMenu(h_menu, _titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION)
    win32gui.InsertMenu(h_menu, _titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION | win32con.MF_SEPARATOR, 0, "")
    win32gui.DrawMenuBar(hwnd)

def window_proc(hwnd, msg, wparam, lparam):
    if msg == win32con.WM_SYSCOMMAND and wparam in _titlebar_cxt_menu_commands:
        _titlebar_cxt_menu_commands[wparam]()
    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

root = Tk()
root.update()

# Register and create the window
wnd_class_name = "CustomSystemMenuApp"
hinst = win32api.GetModuleHandle(None)
wnd_class = win32gui.WNDCLASS()
wnd_class.lpfnWndProc = window_proc
wnd_class.lpszClassName = wnd_class_name
class_atom = win32gui.RegisterClass(wnd_class)

# hwnd = win32gui.CreateWindow(class_atom, "Test Window", win32con.WS_OVERLAPPEDWINDOW, 100, 100, 300, 200, 0, 0, hinst, None)
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
# hwnd = root.winfo_id()

ctypes.windll.user32.SetClassWord(hwnd, 0, class_atom)

add_button(hwnd, "Hello, World!", lambda:print("Hello"))

win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()

root.mainloop()