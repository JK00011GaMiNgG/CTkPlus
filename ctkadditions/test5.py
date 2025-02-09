import win32api
import win32con
import win32gui
import ctypes

from wndproc import WNDPROC
from utils import *
from win32con import *

def set_titlebar_layout(hwnd, layout):
    layout = 1 if layout == "left-to-right" else 0
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        6,
        ctypes.byref(ctypes.c_int(layout)),
        4,
    )

class CustomWindow:
    def __init__(self):
        self.hinst = win32api.GetModuleHandle(None)
        self.class_name = "CustomWindowClass"

        # Register the window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.proc  # Set the window procedure
        wc.lpszClassName = self.class_name
        wc.hbrBackground = win32con.COLOR_WINDOW + 1
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        self.class_atom = win32gui.RegisterClass(wc)

        # Create the window with appropriate styles (including WS_CAPTION for title bar)
        self.hwnd = win32gui.CreateWindowEx(WS_EX_OVERLAPPEDWINDOW, self.class_name, "Custom Window", WS_OVERLAPPEDWINDOW, 100, 100, 800, 600, 0, 0, self.hinst, None)

        # set_titlebar_layout(self.hwnd, "left-to-right")

        # Show the window
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)

    def proc(self, hwnd, msg, wparam, lparam):
        extra_stuff = (0xAA0000, 32, 0x0000FF, None, {lambda:print("HELLO")})
        wp = WNDPROC(extra_stuff)
        return wp.wndproc(hwnd, msg, wparam, lparam)

    def run(self):
        win32gui.PumpMessages()

if __name__ == "__main__":
    app = CustomWindow()
    app.run()