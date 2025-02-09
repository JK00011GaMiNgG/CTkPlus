import ctypes
import os
import tempfile
import winreg
import socket
import ctypes
from io import BytesIO

from PIL import Image
from ctypes import wintypes
from ctypes.wintypes import HWND, UINT
from win32ui import *
from win32gui import *
from win32api import *
from win32con import *

class PWINDOWPOS(ctypes.Structure):
    _fields_ = [
        ("hWnd", HWND),
        ("hwndInsertAfter", HWND),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("cx", ctypes.c_int),
        ("cy", ctypes.c_int),
        ("flags", UINT),
    ]

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class NCCALCSIZE_PARAMS(ctypes.Structure):
    _fields_ = [
        ("rgrc", RECT * 3),
        ("lppos", ctypes.POINTER(PWINDOWPOS))
    ]

class FLASHWINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("hwnd", ctypes.c_void_p),
        ("dwFlags", ctypes.c_uint),
        ("uCount", ctypes.c_uint),
        ("dwTimeout", ctypes.c_uint),
    ]

class WindowPlacement(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("flags", ctypes.c_ulong),
        ("showCmd", ctypes.c_ulong),
        ("ptMinPosition", ctypes.c_ulong * 2),
        ("ptMaxPosition", ctypes.c_ulong * 2),
        ("rcNormalPosition", ctypes.c_long * 4)
    ]

class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_long),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", ctypes.c_long),
        ("szDevice", ctypes.c_char * 32)
    ]

class NONCLIENTMETRICS(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("iBorderWidth", ctypes.c_int),
        ("iScrollWidth", ctypes.c_int),
        ("iScrollHeight", ctypes.c_int),
        ("iCaptionWidth", ctypes.c_int),
        ("iCaptionHeight", ctypes.c_int),
        ("iMenuWidth", ctypes.c_int),
        ("iMenuHeight", ctypes.c_int),
        ("iIconSpacing", ctypes.c_int),
        ("iSmIconSpacing", ctypes.c_int),
        ("iMenuFont", ctypes.c_int),
        ("iStatusFont", ctypes.c_int),
        ("iMessageFont", ctypes.c_int),
        ("iSmCaptionFont", ctypes.c_int),
        ("iSmCaptionHeight", ctypes.c_int),
        ("iSmCaptionWidth", ctypes.c_int),
        ("iMenuBarHeight", ctypes.c_int),
        ("iSmCaptionWidth", ctypes.c_int),
        ("iMenuHeight", ctypes.c_int)
    ]

class ScreenHeight:
    def __init__(self):
        self.monitor_heights = []
        self.enumerate_display()

    def get_heights(self, hMonitor, hdcMonitor, lprcMonitor, dwData):
        monitor_info = MONITORINFOEX()
        monitor_info.cbSize = ctypes.sizeof(MONITORINFOEX)

        if ctypes.windll.user32.GetMonitorInfoA(hMonitor, ctypes.byref(monitor_info)):
            self.monitor_heights.append(monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top)
        return True

    def enumerate_display(self):
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_double)
        monitor_enum_proc = MonitorEnumProc(self.get_heights)

        if ctypes.windll.user32.EnumDisplayMonitors(0, 0, monitor_enum_proc, 0) == 0:
            raise ctypes.WinError()

    def __getitem__(self, index):
        return self.monitor_heights[index]

    def __len__(self):
        return len(self.monitor_heights)

class ScreenWidth:
    def __init__(self):
        self.monitor_widths = []
        self.enumerate_display()

    def get_widths(self, hMonitor, hdcMonitor, lprcMonitor, dwData):
        monitor_info = MONITORINFOEX()
        monitor_info.cbSize = ctypes.sizeof(MONITORINFOEX)

        if ctypes.windll.user32.GetMonitorInfoA(hMonitor, ctypes.byref(monitor_info)):
            self.monitor_widths.append(monitor_info.rcMonitor.right - monitor_info.rcMonitor.left)
        return True

    def enumerate_display(self):
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_double)
        monitor_enum_proc = MonitorEnumProc(self.get_widths)

        if ctypes.windll.user32.EnumDisplayMonitors(0, 0, monitor_enum_proc, 0) == 0:
            raise ctypes.WinError()

    def __getitem__(self, index):
        return self.monitor_widths[index]

    def __len__(self):
        return len(self.monitor_widths)

class ScreenDepth:
    def __init__(self):
        self.monitor_depths = []
        self.enumerate_display()

    def get_depths(self, hMonitor, hdcMonitor, lprcMonitor, dwData):
        hdc = ctypes.windll.gdi32.CreateCompatibleDC(0)
        if hdc:
            depth = ctypes.windll.gdi32.GetDeviceCaps(hdc, 12)
            self.monitor_depths.append(depth)
            ctypes.windll.gdi32.DeleteDC(hdc)
        return True

    def enumerate_display(self):
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_double)
        monitor_enum_proc = MonitorEnumProc(self.get_depths)

        if ctypes.windll.user32.EnumDisplayMonitors(0, 0, monitor_enum_proc, 0) == 0:
            raise ctypes.WinError()

    def __getitem__(self, index):
        return self.monitor_depths[index]

    def __len__(self):
        return len(self.monitor_depths)

def image_hicon(img: Image.Image):
    buffer = BytesIO()
    img = img.convert("RGBA")
    img = img.resize((16, 16), Image.LANCZOS)
    img.save(buffer, format='ICO')
    buffer.seek(0)
    return buffer.read()

def get_windows_theme():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, regtype = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except FileNotFoundError:
        return "unknown"
    except Exception as e:
        return f"Error: {e}"

def has_internet() -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

def hex_to_int(hex_color: str) -> int:
    if not (hex_color.startswith('#') and len(hex_color) == 7):
        raise ValueError("Input must be in the format '#RRGGBB'")
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return (b << 16) | (g << 8) | r

def swap_r_b_int(_hex: int) -> int:
    red = (_hex >> 16) & 0xFF
    green = (_hex >> 8) & 0xFF
    blue = _hex & 0xFF
    swapped_hex = (blue << 16) | (green << 8) | red
    return swapped_hex

def generate_hover_color_int(_hex: int) -> int:
    blue = (_hex >> 16) & 0xFF
    green = (_hex >> 8) & 0xFF
    red = _hex & 0xFF
    hover_blue = min(blue + 13.5, 255)
    hover_green = min(green + 13.5, 255)
    hover_red = min(red + 13.5, 255)
    return (int(hover_blue) << 16) | (int(hover_green) << 8) | int(hover_red)

def generate_opposite_color_int(_hex: int) -> int:
    r = (_hex >> 16) & 0xFF
    g = (_hex >> 8) & 0xFF
    b = _hex & 0xFF
    r_opposite = 255 - r
    g_opposite = 255 - g
    b_opposite = 255 - b
    return (r_opposite << 16) | (g_opposite << 8) | b_opposite

def generate_hover_color(hex_color):
    hex_color = hex_color.lstrip('#')
    first_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    second_color = tuple(min(c + 13.5, 255) for c in first_color)
    return '#' + ''.join(f'{int(c):02X}' for c in second_color)

def generate_opposite_color(hex_color):
    return "#{:02X}{:02X}{:02X}".format(*(255 - int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)))

def darken_color(color, percentage):
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    factor = 1 - percentage / 100
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return (r << 16) | (g << 8) | b

def lighten_color(color, percentage):
    r, g, b = color
    factor = percentage / 100
    return (min(255, int(r + (255 - r) * factor)), min(255, int(g + (255 - g) * factor)), min(255, int(b + (255 - b) * factor)))

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32
dwmapi = ctypes.windll.dwmapi
gdi32 = ctypes.windll.gdi32
uxtheme = ctypes.windll.uxtheme
kernel32 = ctypes.windll.kernel32

screenWidth, screenHeight = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

align_types = {
    "right": "right",
    "left": "left",
    "center": "center"
}

corner_types = {
    "default": 0,
    "flat": 1,
    "round": 2,
    "round_small": 3
}

icon_types = {
    "transparent": "assets/transparent.ico",
    "customtkinter": "assets/customtkinter.ico",
    "tkinter": "",
    "kivy": "assets/kivy.ico"
}

icon_types_names = [
    "customtkinter",
    "tkinter",
    "kivy",
    "ctk",
    "tk",
    "kv"
]

if get_windows_theme() == "light":
    default_title_bar_color = "#ffffff"
    default_title_color = "#000000"
    default_border_color = "#dddddd"
    default_bg_color = "#ebebeb"
else:
    default_title_bar_color = "#000000"
    default_title_color = "#ffffff"
    default_border_color = "#222222"
    default_bg_color = "#242424"

default_corner_type = "flat"
default_unclosable = False
default_frameless = False
default_transparency = 1.0
default_icon_taskbar = True
default_icon = "customtkinter"
