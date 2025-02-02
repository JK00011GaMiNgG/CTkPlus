import base64

import customtkinter as ctk
import tempfile
import requests
import uuid
import io
import os

import ctypes.wintypes

import win32api
import win32con
import win32gui
from PIL import Image
from io import *

from ctkadditions.titlebar.CTkTitlebarButton import CTkTitlebarButton
from ctkadditions.titlebar.titlebar import Titlebar

from ctkadditions.utils.utils import *
from typing import *

class CTkPlus(ctk.CTk):
    _titlebar_height_reduction: Dict[int, int] = {}
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
        self._title_bar_height = 30
        self._title_color = title_color
        self._border_color = border_color
        self._corner_type = corner_type
        self._icon_taskbar = icon_taskbar
        self._bg_color = bg_color

        self._disabled_titlebar = False
        self._empty_titlebar = False

        self._unclosable = unclosable
        self._frameless = frameless
        self._last_state = None

        self._fullscreen = False
        self._x, self._y, self._width, self._height, self._maximized = None, None, None, None, False

        self._titlebar_cxt_menu_item_id = 0
        self._titlebar_cxt_menu_commands = {}

        self._parent_window_handle = user32.GetParent(self.winfo_id())

        self._set_ctypes_attributes()
        self._set_default_attributes()
        self._set_window_proc()

        self.title(self._title)
        # self.titlebar = Titlebar(self, self._title_bar_color, self._title_bar_height)
        self.__fullscreen_titlebar = ctk.CTkFrame(self, height=self._title_bar_height+1, width=screenWidth, fg_color=self._title_bar_color, corner_radius=0)
        self.bind("<Map>", lambda event:self._maximization_detection(event))
        self.update()

    def _set_window_proc(self):
        pass

    def _window_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_SYSCOMMAND and wparam in self._titlebar_cxt_menu_commands:
            self._titlebar_cxt_menu_commands[wparam]()
        return win32gui.CallWindowProc(hwnd, msg, wparam, lparam)

    def _set_default_attributes(self):
        if self._frameless:
            self.enable_empty_titlebar()
            self.disable_titlebar()
        self.protocol("WM_DELETE_WINDOW", noop) if self._unclosable else None

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

    def _maximization_detection(self, event=None):
        if self.wm_state() != self._last_state:
            # self.titlebar.set_titlebar_height(23) if self.wm_state() == "zoomed" else self.titlebar.set_titlebar_height(30)
            self._last_state = self.wm_state()

    def _enable_button(self, button):
        enable_button = ctypes.CDLL(f'titlebar\\cpp\\enable_button.dll')
        if button in ('close', 'minimize', 'maximize'):
            func = getattr(enable_button, f'enable{button.capitalize()}Button')
            func.argtypes, func.restype = [ctypes.wintypes.HWND], None
            func(self._parent_window_handle)

    def _toggle_titlebar_buttons(self):
        # if self._disabled_titlebar:
        #     self.titlebar._hide_children()
        # elif self._empty_titlebar:
        #     self.titlebar._hide_children()
        # else:
        #     self.titlebar._show_children()
        pass

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
        self._toggle_titlebar_buttons()

    def enable_empty_titlebar(self):
        old_style = user32.GetWindowLongPtrA(self._parent_window_handle, -16)
        new_style = old_style & ~0x00080000
        user32.SetWindowLongPtrW(self._parent_window_handle, -16, new_style)
        user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 2 | 1 | 4 | 32)
        self.__title("")
        self._empty_titlebar = True
        self._toggle_titlebar_buttons()

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
        self._toggle_titlebar_buttons()

    def disable_empty_titlebar(self):
        old_style = user32.GetWindowLongPtrA(self._parent_window_handle, -16)
        new_style = old_style | 0x0080000
        user32.SetWindowLongPtrW(self._parent_window_handle, -16, new_style)
        user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 2 | 1 | 4 | 32)
        self._empty_titlebar = False
        self._toggle_titlebar_buttons()

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

    # def add_button(self, text, command, bind=None, icon=None):
    #     h_menu = win32gui.GetSystemMenu(self._parent_window_handle, False)
    #     self._titlebar_cxt_menu_commands[self._titlebar_cxt_menu_item_id] = command
    #     win32gui.InsertMenu(h_menu, self._titlebar_cxt_menu_item_id,
    #                         win32con.MF_BYPOSITION | win32con.MF_STRING,
    #                         self._titlebar_cxt_menu_item_id, text)
    #     self._titlebar_cxt_menu_item_id += 1
    #
    #     if len(self._titlebar_cxt_menu_commands) != 1:
    #         win32gui.RemoveMenu(h_menu, len(self._titlebar_cxt_menu_commands), win32con.MF_BYPOSITION)
    #
    #     win32gui.InsertMenu(h_menu, len(self._titlebar_cxt_menu_commands),
    #                         win32con.MF_BYPOSITION | win32con.MF_SEPARATOR, 0, "")

    def add_button(self, text, command):
        h_menu = win32gui.GetSystemMenu(self._parent_window_handle, False)
        self._titlebar_cxt_menu_commands[self._titlebar_cxt_menu_item_id] = command
        win32gui.InsertMenu(h_menu, self._titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION | win32con.MF_STRING, self._titlebar_cxt_menu_item_id, text)
        self._titlebar_cxt_menu_item_id += 1
        if self._titlebar_cxt_menu_item_id > 1:
            win32gui.RemoveMenu(h_menu, self._titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION)
        win32gui.InsertMenu(h_menu, self._titlebar_cxt_menu_item_id, win32con.MF_BYPOSITION | win32con.MF_SEPARATOR, 0, "")
        win32gui.DrawMenuBar(self._parent_window_handle)

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
            return super().title("") # self.titlebar.tk.call('wm', 'title', self._w, "")
        else:
            self._title = string
            return super().title(self.style_text(string, style-1)) # self.titlebar.tk.call('wm', 'title', self._w, self.style_text(string, style-1))

    def __title(self, string):
        return super().title(string) # self.titlebar.tk.call('wm', 'title', self._w, string)

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
        # self.titlebar.attributes("-alpha", opacity)
        old_ex_style = user32.GetWindowLongPtrA(self._parent_window_handle, -20)
        new_ex_style = old_ex_style | 524288
        user32.SetWindowLongPtrW(self._parent_window_handle, -20, new_ex_style)
        if isinstance(opacity, float) and 0.0 <= opacity <= 1.0:
            opacity = int(opacity * 255)
        user32.SetLayeredWindowAttributes(self._parent_window_handle, 0, opacity, 2)

    def set_preset(self, preset):
        if preset == "normal":
            self.minimize_button(state="normal")
            self.maximize_button(state="normal")
            self.close_button(state="normal")
        elif preset == "toolwindow":
            self.minimize_button(state="disabled")
            self.maximize_button(state="disabled")
        elif preset == "tabbedwindow":
            pass

    def close(self):
        self.destroy()

    def minimize(self, minimize):
        self.iconify() if minimize else self.deiconify()

    def maximize(self, maximize):
        self.state("zoomed") if maximize else self.state("normal")

    def fullscreen(self, fullscreen):
        if fullscreen:
            if not self._fullscreen:
                self._maximized = self.state() == "zoomed"
                if not self._maximized:
                    self._x, self._y, self._width, self._height = self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height()
                else:
                    self.state("normal")
                self.geometry(f"{screenWidth}x{screenHeight}")
                ctypes.windll.user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 0x0001 | 0x0004)
                self.overrideredirect(True)
        else:
            self._fullscreen_titlebar(False)
            if self._fullscreen:
                if not self._maximized:
                    self.geometry(f"{self._x}x{self._y}+{self._width}+{self._height}")
                else:
                    self.state("zoomed")
                self.overrideredirect(False)
        self._fullscreen = not self._fullscreen

    def _fullscreen_titlebar_activation(self, event):
        print("triggered")
        if event.y < 10:
            print("1")
            self._fullscreen_titlebar(True)
        elif event.y > 10:
            print("2")
            self._fullscreen_titlebar(False)
        else:
            print("3")

    def _fullscreen_titlebar(self, enabled):
        if enabled:
            if self._fullscreen:
                self.__fullscreen_titlebar.place(x=0, y=0)
                self.__fullscreen_titlebar.lift()
                hvcolor = generate_hover_color(self._title_bar_color)
                closeimg = Image.open(BytesIO(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAAXNSR0IArs4c6QAAAD9JREFUKFNj/P///39GRkZGBjwArAYkj08xTA5uEjbFyGIoViJLoGvEcBtIAcg56O4mTyFRVhPlGaKCh9gABwC+yEgDfxpCIAAAAABJRU5ErkJggg==")))
                maximizeimg = Image.open(BytesIO(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAAXNSR0IArs4c6QAAAEdJREFUKFOVkEkKADAIA5v/PzolQkoR7eLFg8MYgvEwJImOiyMA7yMoieDYJ6NvglswC/5ABd7fVHGW0XAXJ8BcRWk0dOt9Aj2LKAfl+/RJAAAAAElFTkSuQmCC")))
                minimizeimg = Image.open(BytesIO(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAoAAAABCAYAAADn9T9+AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsEAAA7BAbiRa+0AAAGHaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9J1c1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCc/Pg0KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyI+PHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj48cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0idXVpZDpmYWY1YmRkNS1iYTNkLTExZGEtYWQzMS1kMzNkNzUxODJmMWIiIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIj48dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPjwvcmRmOkRlc2NyaXB0aW9uPjwvcmRmOlJERj48L3g6eG1wbWV0YT4NCjw/eHBhY2tldCBlbmQ9J3cnPz4slJgLAAAAEElEQVQYV2P8////fwYiAACZuAP+/Bq/sgAAAABJRU5ErkJggg==")))
                closeimage = ctk.CTkImage(light_image=closeimg, dark_image=closeimg, size=(10, 10))
                closebutton = ctk.CTkButton(self.__fullscreen_titlebar, text="", image=closeimage, width=45, height=self._title_bar_height, corner_radius=0, fg_color=self._title_bar_color, hover_color="#e81123", command=self.close)
                closebutton.place(x=screenWidth-45)
                maximizeimage = ctk.CTkImage(light_image=maximizeimg, dark_image=maximizeimg, size=(10, 10))
                minimizebutton = ctk.CTkButton(self.__fullscreen_titlebar, text="", image=maximizeimage, width=45, height=self._title_bar_height, corner_radius=0, fg_color=self._title_bar_color, hover_color=hvcolor, command=lambda:self.fullscreen(False))
                minimizebutton.place(x=screenWidth-91)
                minimizeimage = ctk.CTkImage(light_image=minimizeimg, dark_image=minimizeimg, size=(10, 1))
                minimizebutton = ctk.CTkButton(self.__fullscreen_titlebar, text="", image=minimizeimage, width=45, height=self._title_bar_height, corner_radius=0, fg_color=self._title_bar_color, hover_color=hvcolor, command=lambda:self.minimize(True))
                minimizebutton.place(x=screenWidth-137)
                titlelabel = ctk.CTkLabel(self.__fullscreen_titlebar, text=self._title, height=self._title_bar_height)
                titlelabel.place(x=10)
        else:
            self.__fullscreen_titlebar.lower()
            self.__fullscreen_titlebar.place_forget()

    def f11_fullscreen(self, event):
        self.fullscreen(self._fullscreen)

    def overrideredirect(self, enabled):
        style = ctypes.windll.user32.GetWindowLongW(self._parent_window_handle, -16)
        new_style = style & ~(0x00C00000 | 0x00040000) if enabled else style | 0x00C00000 | 0x00040000
        ctypes.windll.user32.SetWindowLongW(self._parent_window_handle, -16, new_style)
        ctypes.windll.user32.SetWindowPos(self._parent_window_handle, 0, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0004 | 0x0020)
        dwmapi.DwmSetWindowAttribute(self._parent_window_handle, 33, ctypes.byref(ctypes.c_int(1 if enabled else corner_types.get(self._corner_type, None))), ctypes.sizeof(ctypes.c_int))

root = CTkPlus(
    corner_type="round"
)
root.title("Hello")
root.geometry('600x600+100+100')

root.set_preset("toolwindow")

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

root.close_button(bind=lambda:d)

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

n = ctk.CTkButton(root, text="Fullscreen Titlebar Enabled", command=lambda:root._fullscreen_titlebar(True))
n.pack(pady=y)

o = ctk.CTkButton(root, text="Fullscreen Titlebar Disabled", command=lambda:root._fullscreen_titlebar(False))
o.pack(pady=y)

root.mainloop()