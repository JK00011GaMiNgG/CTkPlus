import base64
import ctypes.wintypes
from ctypes.wintypes import LONG, LPARAM

import customtkinter as ctk
import tempfile
import requests
import uuid
import io
import os

from ctypes import wintypes

import win32api
import win32con
import win32gui
from PIL import Image
from io import *

from ctkadditions.titlebar.CTkTitlebarButton import CTkTitlebarButton
from ctkadditions.titlebar.titlebar import Titlebar

from ctkadditions.utils.utils import *
from typing import *
from wndproc import WNDPROC, WNDPROCTYPE

class CTkPlus(ctk.CTk):
    _titlebar_height_reduction: Dict[int, int] = {}
    _window_states = {}
    def __init__(self,
                 title_bar_color: str = default_title_bar_color,
                 title_color: str = default_title_color,
                 border_color: str = default_border_color,
                 corner_type: str = default_corner_type,
                 bg_color: str = default_bg_color,
                 unclosable: bool = default_unclosable,
                 frameless: bool = default_frameless,
                 icon_taskbar: bool = default_icon_taskbar,
                 **kwargs):
        super().__init__()

        self._title = "CTkPlus"
        self._title_bar_color = title_bar_color
        self._title_bar_height = 0
        self._title_color = title_color
        self._border_color = border_color
        self._corner_type = corner_type
        self._icon_taskbar = icon_taskbar
        self._bg_color = bg_color

        self._window_type = "normal"

        self._disabled_titlebar = False
        self._empty_titlebar = False

        self._unclosable = unclosable
        self._frameless = frameless
        self._last_state = None

        self._fullscreen = False

        self._titlebar_cxt_menu_item_id = 0
        self._titlebar_cxt_menu_commands = {}

        self._parent_window_handle = user32.GetParent(self.winfo_id())

        self._old_wndproc = win32gui.SetWindowLong(self._parent_window_handle, win32con.GWL_WNDPROC, WNDPROCTYPE(self._wndproc))
        self._new_wndproc = WNDPROCTYPE(self._wndproc)

        self._set_ctypes_attributes()
        self._set_default_attributes()
        self._set_window_proc()

        self.bind("<F11>", self._f11_fullscreen)

        self.title(self._title)

        self.update()

    def _set_window_proc(self):
        win32gui.SetWindowLong(self._parent_window_handle, win32con.GWL_WNDPROC, self._new_wndproc)

    def _wndproc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_SYSCOMMAND and wparam in self._titlebar_cxt_menu_commands:
            self._titlebar_cxt_menu_commands[wparam]()
            return 0
        elif msg == win32con.WM_PAINT:
            return 0
        elif msg == win32con.WM_DESTROY:
            return 0
        # return self._default_wndproc(msg, wparam, lparam)
        extra_stuff = (self._title_bar_color, self._title_bar_height, self._title_color, self._old_wndproc, self._titlebar_cxt_menu_commands)
        return WNDPROC(extra_stuff).wndproc(hwnd, msg, wparam, lparam)

    def _default_wndproc(self, msg, wparam, lparam):
        return win32gui.CallWindowProc(self._old_wndproc, self._parent_window_handle, msg, wparam, lparam)

    def _set_default_attributes(self):
        if self._frameless:
            self.enable_empty_titlebar()
            self.disable_titlebar()
        self.protocol("WM_DELETE_WINDOW", lambda:None) if self._unclosable else None
        super().config(bg=self._bg_color)

    def _set_ctypes_attributes(self):
        shell32.SetCurrentProcessExplicitAppUserModelID(str(uuid.uuid4())) if self._icon_taskbar else None

        dwmapi.DwmSetWindowAttribute(
            self._parent_window_handle,
            33,
            ctypes.byref(ctypes.c_int(corner_types.get(self._corner_type, None))),
            ctypes.sizeof(ctypes.c_int)
        )

        dwmapi.DwmSetWindowAttribute(
            self._parent_window_handle,
            34,
            ctypes.byref(ctypes.c_int(hex_to_int(self._border_color))),
            ctypes.sizeof(ctypes.c_int)
        )

        dwmapi.DwmSetWindowAttribute(
            self._parent_window_handle,
            35,
            ctypes.byref(ctypes.c_int(hex_to_int(self._title_bar_color))),
            ctypes.sizeof(ctypes.c_int)
        )

        dwmapi.DwmSetWindowAttribute(
            self._parent_window_handle,
            36,
            ctypes.byref(ctypes.c_int(hex_to_int(self._title_color))),
            ctypes.sizeof(ctypes.c_int)
        )

    def _enable_button(self, button):
        enable_button = ctypes.CDLL(f'titlebar\\cpp\\enable_button.dll')
        if button in ('close', 'minimize', 'maximize'):
            func = getattr(enable_button, f'enable{button.capitalize()}Button')
            func.argtypes, func.restype = [ctypes.wintypes.HWND], None
            func(self._parent_window_handle)

    def enable_titlebar(self):
        if globals().get("old_wndproc") is not None:
            user32.SetWindowLongPtrW(self._parent_window_handle, -4, globals()["old_wndproc"])
            globals()["old_wndproc"] = None

        height_reduction: int = CTkPlus._titlebar_height_reduction.pop(self._parent_window_handle, 0)

        old_style = user32.GetWindowLongPtrA(self._parent_window_handle, -16)
        new_style = old_style | 0x00C00000
        user32.SetWindowLongPtrW(self._parent_window_handle, -16, new_style)

        if height_reduction:
            rect = RECT()
            user32.GetWindowRect(self._parent_window_handle, ctypes.byref(rect))
            user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, rect.right - rect.left, rect.bottom - rect.top + height_reduction, 4 | 2)
            return

        user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 2 | 1 | 4 | 32)
        self._disabled_titlebar = False

    def enable_empty_titlebar(self):
        old_style = user32.GetWindowLongPtrA(self._parent_window_handle, -16)
        new_style = old_style & ~0x00080000
        user32.SetWindowLongPtrW(self._parent_window_handle, -16, new_style)
        user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 2 | 1 | 4 | 32)
        self.__title("")
        self._empty_titlebar = True

    def disable_titlebar(self):
        def handle(hwnd: int, msg: int, wp: int, lp: int) -> int:
            if msg == 0x0083 and wp:
                lpncsp = NCCALCSIZE_PARAMS.from_address(lp)
                lpncsp.rgrc[0].top -= border_width

            elif msg in [0x0086, 0x0085]:
                return 1

            return user32.CallWindowProcW(*map(ctypes.c_uint64, (globals()[old], hwnd, msg, wp, lp)))

        old, new = "old_wndproc", "new_wndproc"
        prototype = ctypes.WINFUNCTYPE(ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64)

        rect = RECT()
        client_rect = RECT()
        user32.GetWindowRect(self._parent_window_handle, ctypes.byref(rect))
        user32.GetClientRect(self._parent_window_handle, ctypes.byref(client_rect))

        full_width: int = rect.right - rect.left
        full_height: int = rect.bottom - rect.top
        client_width: int = client_rect.right
        client_height: int = client_rect.bottom

        border_width: int = (full_width - client_width) // 2
        title_bar_height: int = (full_height - client_height - border_width)

        if globals().get(old) is None:
            globals()[old] = user32.GetWindowLongPtrA(self._parent_window_handle, -4)

        globals()[new] = prototype(handle)
        user32.SetWindowLongPtrW(self._parent_window_handle, -4, globals()[new])

        old_style = user32.GetWindowLongPtrA(self._parent_window_handle, -16)
        new_style = (old_style & ~0x00C00000) | 0x00800000
        user32.SetWindowLongPtrW(self._parent_window_handle, -16, new_style)

        no_span = False

        if no_span:
            CTkPlus._titlebar_height_reduction[self._parent_window_handle] = title_bar_height
            user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, full_width, full_height-title_bar_height, 4 | 2)
            return

        user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 2 | 1 | 4 | 32)
        self._disabled_titlebar = True

    def disable_empty_titlebar(self):
        old_style = user32.GetWindowLongPtrA(self._parent_window_handle, -16)
        new_style = old_style | 0x0080000
        user32.SetWindowLongPtrW(self._parent_window_handle, -16, new_style)
        user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 2 | 1 | 4 | 32)
        self._empty_titlebar = False

    def _disable_button(self, button):
        disable_button = ctypes.CDLL(f'titlebar\\cpp\\disable_button.dll')
        if button in ('close', 'minimize', 'maximize'):
            func = getattr(disable_button, f'disable{button.capitalize()}Button')
            func.argtypes, func.restype = [ctypes.wintypes.HWND], None
            func(self._parent_window_handle)

    def start_flashing(self, count: int = 10, interval: int = 100):
        info = FLASHWINFO(cbSize=ctypes.sizeof(FLASHWINFO), hwnd=self._parent_window_handle, dwFlags=3 | 4, uCount=count, dwTimeout=interval)
        user32.FlashWindowEx(ctypes.pointer(info))

    def stop_flashing(self):
        info = FLASHWINFO(cbSize=ctypes.sizeof(FLASHWINFO), hwnd=self._parent_window_handle, dwFlags=0, uCount=0, dwTimeout=0)
        user32.FlashWindowEx(ctypes.pointer(info))

    def set_titlebar_layout(self, layout):
        layout = 1 if layout == "left-to-right" else 0
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            self._parent_window_handle,
            6,
            ctypes.byref(ctypes.c_int(layout)),
            4,
        )

    def add_button(self, text, command):
        h_menu = win32gui.GetSystemMenu(self._parent_window_handle, False)
        self._titlebar_cxt_menu_commands[self._titlebar_cxt_menu_item_id] = command
        win32gui.InsertMenu(h_menu, self._titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION | win32con.MF_STRING, self._titlebar_cxt_menu_item_id, text)
        self._titlebar_cxt_menu_item_id += 1
        if self._titlebar_cxt_menu_item_id > 1:
            win32gui.RemoveMenu(h_menu, self._titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION)
        win32gui.InsertMenu(h_menu, self._titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION | win32con.MF_SEPARATOR, 0, "")

    def close_button(self, state: Optional[Union[Literal['disabled'], Literal['normal']]] = None, bind: Union[Callable[[], Any], None] = None, **kwargs):
        self._disable_button('close') if state == 'disabled' else self._enable_button('close') if state == 'normal' else None

    def minimize_button(self, state: Optional[Union[Literal['disabled'], Literal['normal']]] = None, bind: Union[Callable[[], Any], None] = None, **kwargs):
        self._disable_button('minimize') if state == 'disabled' else self._enable_button('minimize') if state == 'normal' else None

    def maximize_button(self, state: Optional[Union[Literal['disabled'], Literal['normal']]] = None, bind: Union[Callable[[], Any], None] = None, **kwargs):
        self._disable_button('maximize') if state == 'disabled' else self._enable_button('maximize') if state == 'normal' else None

    def style_text(self, phrase, style):
        self.common = [list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"),
                       list("𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢"),
                       list("𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢"),
                       list("𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘"),
                       list("ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ①②③④⑤⑥⑦⑧⑨⓪"),
                       list("𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶")]
        return ''.join(c if c not in self.common[0] else self.common[style][self.common[0].index(c)] for c in phrase)

    def update(self):
        super().update()

    def wm_title(self, string=None, style=1):
        if string in [None, ""]:
            self._title = ""
            return super().title("")
        else:
            self._title = string
            return super().title(self.style_text(string, style-1))

    def __title(self, string):
        return super().title(string)

    title = wm_title

    def set_icon(self, path: Union[str, None]):
        internet = has_internet()
        if path in [None, ""]:
            self.iconbitmap(icon_types.get("transparent", None))
        elif path in icon_types_names:
            if path in ["customtkinter", "ctk"]:
                self.iconbitmap(icon_types.get("customtkinter", None))
            elif path in ["tkinter", "tk"]:
                self.iconbitmap(None)
            elif path in ["kivy", "kv"]:
                self.iconbitmap(icon_types.get("kivy", None))
        else:
            if path.startswith('https://') or path.startswith('http://'):
                if not internet:
                    raise ConnectionError("Using URLs requires internet access.")
                elif internet:
                    response = requests.get(path)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content)).convert('RGBA')

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.ico') as temp_file:
                        image.save(temp_file, format='ico')
                        temp_file_name = temp_file.name
            else:
                image = Image.open(path).convert('RGBA')

                with tempfile.NamedTemporaryFile(delete=False, suffix='.ico') as temp_file:
                    image.save(temp_file, format='ico')
                    temp_file_name = temp_file.name

            self.iconbitmap(temp_file_name)
            os.remove(temp_file_name)

    def set_opacity(self, opacity: float):
        old_ex_style = user32.GetWindowLongPtrA(self._parent_window_handle, -20)
        new_ex_style = old_ex_style | 524288
        user32.SetWindowLongPtrW(self._parent_window_handle, -20, new_ex_style)
        if isinstance(opacity, float) and 0.0 <= opacity <= 1.0:
            opacity = int(opacity * 255)
        user32.SetLayeredWindowAttributes(self._parent_window_handle, 0, opacity, 2)

    def set_window_type(self, type):
        if type == "normal":
            self._window_type = "normal"
            self.maximize_button(state="normal")
            self.minimize_button(state="normal")
        elif type == "toolwindow":
            self._window_type = "tool"
            self.maximize_button(state="disabled")
            self.minimize_button(state="disabled")
        elif type == "tabbedwindow":
            self._window_type = "tabbed"
        else:
            raise SyntaxError("That is not a valid window type. Valid window types are \"normal\", \"toolwindow\", and \"tabbedwindow\".")

    def close(self):
        self.destroy()

    def minimize(self, minimize):
        self.iconify() if minimize else self.deiconify()

    def maximize(self, maximize):
        self.state("zoomed") if maximize else self.state("normal")

    def fullscreen(self, fullscreen):
        if fullscreen:
            placement = win32gui.GetWindowPlacement(self._parent_window_handle)
            style = win32gui.GetWindowLong(self._parent_window_handle, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(self._parent_window_handle, win32con.GWL_EXSTYLE)
            CTkPlus._window_states[self._parent_window_handle] = (placement, style, ex_style)
            win32gui.SetWindowLong(self._parent_window_handle, win32con.GWL_STYLE, style & ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME))
            win32gui.SetWindowLong(self._parent_window_handle, win32con.GWL_EXSTYLE, ex_style & ~(win32con.WS_EX_DLGMODALFRAME | win32con.WS_EX_WINDOWEDGE))
            win32gui.ShowWindow(self._parent_window_handle, win32con.SW_MAXIMIZE)
        else:
            if self._parent_window_handle in CTkPlus._window_states:
                placement, style, ex_style = CTkPlus._window_states.pop(self._parent_window_handle)
                win32gui.SetWindowLong(self._parent_window_handle, win32con.GWL_STYLE, style)
                win32gui.SetWindowLong(self._parent_window_handle, win32con.GWL_EXSTYLE, ex_style)
                win32gui.SetWindowPlacement(self._parent_window_handle, placement)
                win32gui.ShowWindow(self._parent_window_handle, win32con.SW_SHOWNORMAL)
        self._fullscreen = fullscreen

    def _f11_fullscreen(self, event):
        self.fullscreen(not self._fullscreen)

    def get_hwnd(self):
        return self._parent_window_handle

root = CTkPlus(
    title_color="#00ff00"
)
root.title("Hello")
root.geometry('600x600+100+100')

# titlebarButton = CTkTitlebarButton(root.titlebar, text="Hi")
# titlebarButton.pack()
#
# titlebarButton2 = CTkTitlebarButton(root.titlebar, text="Bye")
# titlebarButton2.pack()

def changeOpacity(value):
    root.set_opacity(value)

x = len(root.common)
y = 15

def a():
    root.minimize_button(switchVar.get())

def b():
    root.maximize_button(switch2Var.get())

def c():
    root.close_button(switch3Var.get())

def d():
    print("Hello")

root.add_button("Say Hello", lambda: print("Hello!"))
root.add_button("Command", d)
root.add_button("BROOO", d)

slider = ctk.CTkSlider(root, number_of_steps=100, from_=0, to=1, command=changeOpacity)
slider.pack(pady=y)
slider.set(1)

button = ctk.CTkButton(root, text="Enable Titlebar", command=lambda:root.enable_titlebar())
button.pack(pady=y)

button2 = ctk.CTkButton(root, text="Disable Titlebar", command=lambda:root.disable_titlebar())
button2.pack(pady=y)

button3 = ctk.CTkButton(root, text="Enable Empty Titlebar", command=lambda:root.enable_empty_titlebar())
button3.pack(pady=y)

button4 = ctk.CTkButton(root, text="Disable Empty Titlebar", command=lambda:root.disable_empty_titlebar())
button4.pack(pady=y)

switchVar = ctk.StringVar(value="normal")
switch = ctk.CTkSwitch(root, text="Minimize Button", command=a, variable=switchVar, onvalue="normal", offvalue="disabled")
switch.pack(pady=y)

switch2Var = ctk.StringVar(value="normal")
switch2 = ctk.CTkSwitch(root, text="Maximize Button", command=b, variable=switch2Var, onvalue="normal", offvalue="disabled")
switch2.pack(pady=y)

switch3Var = ctk.StringVar(value="normal")
switch3 = ctk.CTkSwitch(root, text="Close Button", command=c, variable=switch3Var, onvalue="normal", offvalue="disabled")
switch3.pack(pady=y)

fullscreen = ctk.CTkButton(root, text="Fullscreen", command=lambda:root.fullscreen(True))
fullscreen.pack(pady=y)

fullscreen2 = ctk.CTkButton(root, text="Fullscreen Disabled", command=lambda:root.fullscreen(False))
fullscreen2.pack(pady=y)

root.mainloop()