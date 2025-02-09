from ctypes import wintypes

import win32gui
from yt_dlp.compat import passthrough_module

from utils.utils import *
from win32con import *
from win32api import *
from win32gui import *
from PIL import Image

WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.wintypes.LPARAM, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

class POINT(ctypes.Structure): _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
class SIZE(ctypes.Structure): _fields_ = [("cx", wintypes.LONG), ("cy", wintypes.LONG)]
class RECT(ctypes.Structure): _fields_ = [("left",   wintypes.LONG), ("top",    wintypes.LONG), ("right",  wintypes.LONG), ("bottom", wintypes.LONG)]
class WNDCLASSEX(ctypes.Structure):_fields_ = [("cbSize", wintypes.UINT), ("style", wintypes.UINT), ("lpfnWndProc", WNDPROCTYPE), ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON), ("hCursor", wintypes.LONG), ("hbrBackground", wintypes.HBRUSH), ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR), ("hIconSm", wintypes.HICON)]
class MSG(ctypes.Structure): _fields_ = [("hwnd", wintypes.HWND), ("message", wintypes.UINT), ("wParam", wintypes.WPARAM), ("lParam", wintypes.LPARAM), ("time", wintypes.DWORD), ("pt", POINT)]
class PAINTSTRUCT(ctypes.Structure): _fields_ = [("hdc", wintypes.HDC), ("fErase", wintypes.BOOL), ("rcPaint", RECT), ("fRestore", wintypes.BOOL), ("fIncUpdate", wintypes.BOOL), ("rgbReserved", ctypes.c_byte * 32)]
class NCCALCSIZE_PARAMS(ctypes.Structure): _fields_ = [("rgrc", RECT * 3), ("lppos", ctypes.c_void_p)]
class WINDOWPLACEMENT(ctypes.Structure): _fields_ = [("length", wintypes.UINT), ("flags", wintypes.UINT), ("showCmd", wintypes.UINT), ("ptMinPosition", POINT), ("ptMaxPosition", POINT), ("rcNormalPosition",RECT)]
class LOGFONT(ctypes.Structure): _fields_ = [("lfHeight", wintypes.LONG), ("lfWidth", wintypes.LONG), ("lfEscapement", wintypes.LONG), ("lfOrientation", wintypes.LONG), ("lfWeight", wintypes.LONG), ("lfItalic", wintypes.BYTE), ("lfUnderline", wintypes.BYTE), ("lfStrikeOut", wintypes.BYTE), ("lfCharSet", wintypes.BYTE), ("lfOutPrecision", wintypes.BYTE), ("lfClipPrecision", wintypes.BYTE), ("lfQuality", wintypes.BYTE), ("lfPitchAndFamily", wintypes.BYTE), ("lfFaceName", wintypes.WCHAR * 32)]
class DTTOPTS(ctypes.Structure): _fields_ = [("dwSize", wintypes.DWORD), ("dwFlags", wintypes.DWORD), ("crText", wintypes.COLORREF), ("crBorder", wintypes.COLORREF), ("crShadow", wintypes.COLORREF), ("iTextShadowType", ctypes.c_int), ("ptShadowOffset", POINT), ("iBorderSize", ctypes.c_int), ("iFontPropId", ctypes.c_int), ("iColorPropId", ctypes.c_int), ("iStateId", ctypes.c_int), ("fApplyOverlay", wintypes.BOOL), ("iGlowSize", ctypes.c_int), ("pfnDrawTextCallback", ctypes.c_void_p), ("lParam", wintypes.LPARAM)]
class TitleBarButtonRects(ctypes.Structure): _fields_ = [("close", RECT), ("maximize", RECT), ("minimize", RECT)]
class MINMAXINFO(ctypes.Structure): _fields_ = [("ptReserved", POINT), ("ptMaxSize", POINT), ("ptMaxPosition", POINT), ("ptMinTrackSize", POINT), ("ptMaxTrackSize", POINT) ]

def LOWORD(dword): return dword & 0xFFFF
def HIWORD(dword): return (dword >> 16) & 0xFFFF
def GET_X_PARAM(lp): return ctypes.c_int(ctypes.c_short(LOWORD(lp)).value).value
def GET_Y_PARAM(lp): return ctypes.c_int(ctypes.c_short(HIWORD(lp)).value).value

CustomTitleBarHoveredButton_None = 0
CustomTitleBarHoveredButton_Minimize = 1
CustomTitleBarHoveredButton_Maximize = 2
CustomTitleBarHoveredButton_Close = 3

class WNDPROC:
    def __init__(self, arguments, button_details=None, detailed_maximized_button=False):
        button_details = (False, True, False, True, False, True)

        self.close_button_enabled = button_details[0]
        self.close_button_existent = button_details[1]
        self.maximize_button_enabled = button_details[2]
        self.maximize_button_existent = button_details[3]
        self.minimize_button_enabled = button_details[4]
        self.minimize_button_existent = button_details[5]

        arguments = (None, "#242424", 70, True, False, "#ffffff", "CTk", Image.open("assets/customtkinter.ico"), True, [], [])
        self.old_wndproc = arguments[0]

        self.titlebar_color = swap_r_b_int(hex_to_int(arguments[1]))
        self.titlebar_height = arguments[2]
        self.titlebar_height_maximized = self.titlebar_height - 6
        self.titlebar_enabled = arguments[3]
        self.reversed_layout = arguments[4]

        self.title_color = swap_r_b_int(hex_to_int(arguments[5]))
        self.title = arguments[6]

        self.icon = arguments[7]
        self.icon_enabled = arguments[8]

        self.titlebar_context_menu_commands = arguments[9]
        self.titlebar_context_menu = arguments[10]
        self.titlebar_context_menu_id = 0

        self.dmb = detailed_maximized_button

    def wndproc(self, hwnd, msg, wparam, lparam):
        self.title_bar_rect = self.win32_titlebar_rect(hwnd)
        self.dpi = user32.GetDpiForWindow(hwnd)
        maximized_extension = 3 if self.win32_window_is_maximized(hwnd) else 0
        title_bar_hovered_button = ctypes.c_long(user32.GetWindowLongPtrW(hwnd, -21)).value
        if msg == WM_NCCALCSIZE:
            if not wparam:
                return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
            dpi = user32.GetDpiForWindow(hwnd)
            frame_x = user32.GetSystemMetricsForDpi(SM_CXFRAME, dpi)
            frame_y = user32.GetSystemMetricsForDpi(SM_CYFRAME, dpi)
            padding = user32.GetSystemMetricsForDpi(92, dpi)
            params = ctypes.cast(lparam, ctypes.POINTER(NCCALCSIZE_PARAMS)).contents
            requested_client_rect = params.rgrc[0]
            requested_client_rect.right -= frame_x + padding
            requested_client_rect.left  += frame_x + padding
            requested_client_rect.bottom -= frame_y + padding
            if self.win32_window_is_maximized(hwnd):
                requested_client_rect.top += padding
            return 0
        elif msg == WM_CREATE:
            user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER)
        elif msg == WM_ACTIVATE:
            title_bar_rect = self.win32_titlebar_rect(hwnd)
            user32.InvalidateRect(hwnd, ctypes.byref(title_bar_rect), False)
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        elif msg == WM_NCHITTEST:
            hit = user32.DefWindowProcW(hwnd, msg, wparam, lparam)
            if hit in (0, HTRIGHT, HTLEFT, HTTOPLEFT, HTTOP, HTTOPRIGHT, HTBOTTOMRIGHT, HTBOTTOM, HTBOTTOMLEFT):
                return hit
            if title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize:
                return HTMAXBUTTON
            dpi = user32.GetDpiForWindow(hwnd)
            frame_y = user32.GetSystemMetricsForDpi(SM_CYFRAME, dpi)
            padding = user32.GetSystemMetricsForDpi(92, dpi)
            cursor_point = POINT(0, 0)
            cursor_point.x = GET_X_PARAM(lparam)
            cursor_point.y = GET_Y_PARAM(lparam)
            user32.ScreenToClient(hwnd, ctypes.byref(cursor_point))
            if 0 < cursor_point.y < (frame_y + padding):
                return HTTOP
            tb_rect = self.win32_titlebar_rect(hwnd)
            if cursor_point.y < tb_rect.bottom:
                return HTCAPTION
            return HTCLIENT
        elif msg == WM_PAINT:
            if self.titlebar_enabled:
                getR = lambda r: r & 0xFF
                getG = lambda g: (g >> 8) & 0xFF
                getB = lambda b: (b >> 16) & 0xFF
                has_focus = bool(user32.GetFocus())
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
                theme = uxtheme.OpenThemeData(hwnd, "WINDOW")
                title_bar_brush = gdi32.CreateSolidBrush(self.titlebar_color)
                title_bar_hover_color = generate_hover_color_int(self.titlebar_color)
                title_bar_hover_brush = gdi32.CreateSolidBrush(title_bar_hover_color)
                title_bar_rect = self.title_bar_rect
                user32.FillRect(hdc, ctypes.byref(title_bar_rect), title_bar_brush)
                title_bar_item_color = 0x000000 if has_focus else 0xFFFFFF
                button_icon_brush = gdi32.CreateSolidBrush(title_bar_item_color)
                button_icon_pen = gdi32.CreatePen(PS_SOLID, 1, title_bar_item_color)
                button_rects = self.win32_get_title_bar_button_rects(hwnd, title_bar_rect)
                dpi = user32.GetDpiForWindow(hwnd)
                icon_dimension = self.win32_dpi_scale(10, dpi)
                if title_bar_hovered_button == CustomTitleBarHoveredButton_Minimize:
                    user32.FillRect(hdc, ctypes.byref(button_rects.minimize), title_bar_hover_brush)
                icon_rect = RECT(0, 0, icon_dimension, 1)
                self.win32_center_rect_in_rect(icon_rect, button_rects.minimize, maximized_extension)
                user32.FillRect(hdc, ctypes.byref(icon_rect), button_icon_brush)
                if title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize:
                    user32.FillRect(hdc, ctypes.byref(button_rects.maximize), title_bar_hover_brush)
                icon_rect = RECT(0, 0, icon_dimension, icon_dimension)
                self.win32_center_rect_in_rect(icon_rect, button_rects.maximize, maximized_extension)
                gdi32.SelectObject(hdc, button_icon_pen)
                gdi32.SelectObject(hdc, gdi32.GetStockObject(5))
                if self.win32_window_is_maximized(hwnd):
                    if not self.reversed_layout:
                        if self.dmb:
                            gdi32.Rectangle(hdc, icon_rect.left + 2, icon_rect.top - 1, icon_rect.right + 2, icon_rect.bottom - 1)
                            user32.FillRect(hdc, ctypes.byref(icon_rect), title_bar_hover_brush if title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize else title_bar_brush)
                            MoveToEx(hdc, icon_rect.left + 2, icon_rect.top - 1)
                            LineTo(hdc, icon_rect.left + 2, icon_rect.top + 1)
                        else:
                            MoveToEx(hdc, icon_rect.left + 2, icon_rect.top - 1)
                            LineTo(hdc, icon_rect.right + 1, icon_rect.top - 1)
                            MoveToEx(hdc, icon_rect.right + 1, icon_rect.top - 1)
                            LineTo(hdc, icon_rect.right + 1, icon_rect.bottom - 1)
                    else:
                        self.dmb = False
                        if self.dmb:
                            gdi32.Rectangle(hdc, icon_rect.right - 2, icon_rect.top - 1, icon_rect.left - 2, icon_rect.bottom - 1)
                            user32.FillRect(hdc, ctypes.byref(icon_rect), title_bar_hover_brush if title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize else title_bar_brush)
                            MoveToEx(hdc, icon_rect.right - 2, icon_rect.top - 1)
                            LineTo(hdc, icon_rect.right - 2, icon_rect.top + 1)
                        else:
                            MoveToEx(hdc, icon_rect.right - 2, icon_rect.top - 1)
                            LineTo(hdc, icon_rect.left - 2, icon_rect.top - 1)
                            MoveToEx(hdc, icon_rect.left - 2, icon_rect.top - 1)
                            LineTo(hdc, icon_rect.left - 2, icon_rect.bottom - 1)
                    gdi32.Rectangle(hdc, icon_rect.left, icon_rect.top + 1, icon_rect.right, icon_rect.bottom + 1)
                else:
                    gdi32.Rectangle(hdc, icon_rect.left, icon_rect.top, icon_rect.right, icon_rect.bottom)
                custom_pen = 0
                if title_bar_hovered_button == CustomTitleBarHoveredButton_Close:
                    fill_brush = gdi32.CreateSolidBrush(0x2311e8)
                    user32.FillRect(hdc, ctypes.byref(button_rects.close), fill_brush)
                    gdi32.DeleteObject(fill_brush)
                    custom_pen = gdi32.CreatePen(PS_SOLID, 1, 0xFFFFFF)
                    gdi32.SelectObject(hdc, custom_pen)
                icon_rect = RECT(0, 0, icon_dimension,icon_dimension)
                self.win32_center_rect_in_rect(icon_rect, button_rects.close, maximized_extension)
                MoveToEx(hdc, icon_rect.left, icon_rect.top)
                LineTo(hdc, icon_rect.right + 1, icon_rect.bottom + 1)
                MoveToEx(hdc, icon_rect.left, icon_rect.bottom)
                LineTo(hdc, icon_rect.right + 1, icon_rect.top - 1)
                if custom_pen: gdi32.DeleteObject(custom_pen)
                gdi32.DeleteObject(title_bar_hover_brush)
                gdi32.DeleteObject(button_icon_brush)
                gdi32.DeleteObject(button_icon_pen)
                gdi32.DeleteObject(title_bar_brush)
                logical_font = LOGFONT()
                old_font = None
                if user32.SystemParametersInfoForDpi:
                    res = user32.SystemParametersInfoForDpi(0x001F, ctypes.sizeof(logical_font), ctypes.byref(logical_font), False, dpi)
                    if res:
                        theme_font = gdi32.CreateFontIndirectW(ctypes.byref(logical_font))
                        old_font = gdi32.SelectObject(hdc, theme_font)
                text_padding = 5 if self.win32_window_is_maximized(hwnd) else 8
                if self.icon_enabled:
                    icon_padding = 5 if self.win32_window_is_maximized(hwnd) else 8
                    if self.reversed_layout:
                        icon_padding = title_bar_rect.right - (21 if self.win32_window_is_maximized(hwnd) else 24)
                    text_padding = 32
                    icon = image_hicon(self.icon)
                    user32.CreateIconFromResourceEx(icon, len(icon), True, 0x00030000, 32, 32, LR_DEFAULTCOLOR)
                anchor = DT_RIGHT if self.reversed_layout else DT_LEFT
                text_rect_left = title_bar_rect.left + text_padding if not self.reversed_layout else title_bar_rect.left
                text_rect_right = title_bar_rect.right - text_padding if self.reversed_layout else title_bar_rect.right
                text_rect_bottom = 50 if title_bar_rect.bottom >= 50 else title_bar_rect.bottom
                win32gui.SetBkColor(hdc, self.titlebar_color)
                win32gui.SetTextColor(hdc, self.title_color)
                win32gui.SetBkMode(hdc, OPAQUE)
                win32gui.DrawText(hdc, self.title, -1, (text_rect_left, title_bar_rect.top, text_rect_right, text_rect_bottom), anchor | DT_VCENTER | DT_SINGLELINE)
                if old_font: gdi32.SelectObject(hdc, old_font)
                uxtheme.CloseThemeData(theme)
                shadow_color = 0x646464
                if has_focus:
                    fake_top_shadow_color = shadow_color
                else:
                    fake_top_shadow_color = ((getR(self.titlebar_color)+getR(shadow_color))//2 | ((getG(self.titlebar_color)+getG(shadow_color))//2 << 8) | ((getB(self.titlebar_color)+getB(shadow_color))//2 << 16))
                fake_top_shadow_brush = gdi32.CreateSolidBrush(fake_top_shadow_color)
                fake_top_shadow_rect = self.win32_fake_shadow_rect(hwnd)
                user32.FillRect(hdc, ctypes.byref(fake_top_shadow_rect), fake_top_shadow_brush)
                gdi32.DeleteObject(fake_top_shadow_brush)
                user32.EndPaint(hwnd, ctypes.byref(ps))
        elif msg == WM_NCMOUSEMOVE:
            cursor_point = POINT()
            user32.GetCursorPos(ctypes.byref(cursor_point))
            user32.ScreenToClient(hwnd, ctypes.byref(cursor_point))
            title_bar_rect = self.win32_titlebar_rect(hwnd)
            button_rects = self.win32_get_title_bar_button_rects(hwnd, title_bar_rect)
            new_hovered_button = CustomTitleBarHoveredButton_None
            if user32.PtInRect(ctypes.byref(button_rects.close), cursor_point):
                new_hovered_button = CustomTitleBarHoveredButton_Close
            elif user32.PtInRect(ctypes.byref(button_rects.minimize), cursor_point):
                new_hovered_button = CustomTitleBarHoveredButton_Minimize
            elif user32.PtInRect(ctypes.byref(button_rects.maximize), cursor_point):
                new_hovered_button = CustomTitleBarHoveredButton_Maximize
            if new_hovered_button != title_bar_hovered_button:
                user32.InvalidateRect(hwnd, ctypes.byref(button_rects.close), False)
                user32.InvalidateRect(hwnd, ctypes.byref(button_rects.minimize), False)
                user32.InvalidateRect(hwnd, ctypes.byref(button_rects.maximize), False)
                user32.SetWindowLongPtrW(hwnd, -21, new_hovered_button)
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        elif msg == WM_MOUSEMOVE:
            if title_bar_hovered_button:
                title_bar_rect = self.win32_titlebar_rect(hwnd)
                user32.InvalidateRect(hwnd, ctypes.byref(title_bar_rect), False)
                user32.SetWindowLongPtrW(hwnd, -21, CustomTitleBarHoveredButton_None)
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        elif msg == WM_NCLBUTTONDOWN:
            if title_bar_hovered_button:
                return 0
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        elif msg == WM_NCLBUTTONUP:
            if title_bar_hovered_button == CustomTitleBarHoveredButton_Close:
                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                return 0
            elif title_bar_hovered_button == CustomTitleBarHoveredButton_Minimize:
                user32.ShowWindow(hwnd, SW_MINIMIZE)
                return 0
            elif title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize:
                mode = SW_NORMAL if self.win32_window_is_maximized(hwnd) else SW_MAXIMIZE
                user32.ShowWindow(hwnd, mode)
                return 0
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        elif msg == WM_SYSCOMMAND and wparam in self.titlebar_context_menu_commands:
            self.titlebar_context_menu_commands[wparam]()
        elif msg == WM_GETMINMAXINFO:
            min_max_info = ctypes.cast(lparam, ctypes.POINTER(MINMAXINFO)).contents
            min_max_info.ptMinTrackSize.y = self.titlebar_height+8
        elif msg == WM_NCRBUTTONUP and wparam == HTCAPTION:
            button_rects = self.win32_get_title_bar_button_rects(hwnd, self.title_bar_rect)
            x, y = self.get_mouse_pos(hwnd)
            if (button_rects.close.left <= x <= button_rects.close.right and
                button_rects.close.top <= y <= button_rects.close.bottom) or \
               (button_rects.maximize.left <= x <= button_rects.maximize.right and
                button_rects.maximize.top <= y <= button_rects.maximize.bottom) or \
               (button_rects.minimize.left <= x <= button_rects.minimize.right and
                button_rects.minimize.top <= y <= button_rects.minimize.bottom):
                return 0
            else:
                is_maximized = user32.IsZoomed(hwnd)
                sys_menu = user32.GetSystemMenu(hwnd, False)

                self.set_menu_item_state(sys_menu, None, SC_RESTORE, bool(is_maximized))
                self.set_menu_item_state(sys_menu, None, SC_MOVE, not bool(is_maximized))
                self.set_menu_item_state(sys_menu, None, SC_SIZE, not bool(is_maximized))
                self.set_menu_item_state(sys_menu, None, SC_MINIMIZE, True)
                self.set_menu_item_state(sys_menu, None, SC_MAXIMIZE, not bool(is_maximized))
                self.set_menu_item_state(sys_menu, None, SC_CLOSE, True)

                result = user32.TrackPopupMenu(sys_menu, TPM_RETURNCMD, GET_X_PARAM(lparam), GET_Y_PARAM(lparam), 0, hwnd, None)

                if result == SC_CLOSE:
                    user32.PostMessageW(hwnd, wintypes.UINT(0x0010), 0, 0)
                elif result == SC_MINIMIZE:
                    user32.ShowWindow(hwnd, 6)
                elif result == SC_RESTORE:
                    user32.ShowWindow(hwnd, 9)
                elif result == SC_MAXIMIZE:
                    user32.ShowWindow(hwnd, 3)
                elif result == SC_MOVE:
                    user32.SendMessageW(hwnd, 0x00A1, HTCAPTION, lparam)
                return 0
        else:
            return DefWindowProc(hwnd, msg, wparam, lparam)
        try:
            return user32.DefWindowProcW(ctypes.c_void_p(hwnd), ctypes.c_uint(msg), ctypes.c_void_p(wparam), ctypes.c_void_p(lparam))
        except OverflowError:
            print(f"OverflowError in DefWindowProcW: msg={msg}, w_param={wparam}, l_param={lparam}")
            return 0

    def win32_dpi_scale(self, value, dpi):
        return int(float(value) * dpi / 96)

    def set_menu_item_state(self, menu, menuItemInfo, item, enabled):
        state = MF_ENABLED if enabled else MF_DISABLED
        user32.EnableMenuItem(menu, item, state)

    def get_mouse_pos(self, hwnd):
        cursor_pos = GetCursorPos()
        client_rect = GetClientRect(hwnd)
        client_left, client_top, client_right, client_bottom = client_rect
        screen_left, screen_top = win32gui.ClientToScreen(hwnd, (client_left, client_top))
        screen_right, screen_bottom = win32gui.ClientToScreen(hwnd, (client_right, client_bottom))
        client_x = cursor_pos[0] - screen_left
        client_y = cursor_pos[1] - screen_top
        return (client_x, client_y)

    def win32_titlebar_rect(self, hwnd):
        theme = uxtheme.OpenThemeData(hwnd, "WINDOW")
        size = SIZE()
        uxtheme.GetThemePartSize(theme, None, 1, 1, None, 1, ctypes.byref(size))
        uxtheme.CloseThemeData(theme)
        rect = RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rect))
        titlebar_height = self.titlebar_height_maximized if self.win32_window_is_maximized(hwnd) else self.titlebar_height
        rect.bottom = rect.top + titlebar_height
        return rect

    def win32_fake_shadow_rect(self, hwnd):
        rect = RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rect))
        rect.bottom = rect.top + 1
        return rect

    def win32_get_title_bar_button_rects(self, hwnd, title_bar_rect):
        dpi = user32.GetDpiForWindow(hwnd)
        button_rects = TitleBarButtonRects()
        button_width = self.win32_dpi_scale(47, dpi)
        if title_bar_rect.bottom >= 50:
            title_bar_rect.bottom = 50
        if not self.reversed_layout:
            button_rects.close = title_bar_rect
            button_rects.close.top += 1
            button_rects.close.left = button_rects.close.right - button_width
            button_rects.maximize = button_rects.close
            button_rects.maximize.left -= button_width
            button_rects.maximize.right -= button_width
            button_rects.minimize = button_rects.maximize
            button_rects.minimize.left -= button_width
            button_rects.minimize.right -= button_width
        else:
            button_rects.close = title_bar_rect
            button_rects.close.left += 1
            button_rects.close.right = button_rects.close.left + button_width
            button_rects.maximize = button_rects.close
            button_rects.maximize.left = button_rects.close.right + 1
            button_rects.maximize.right = button_rects.maximize.left + button_width
            button_rects.minimize = button_rects.maximize
            button_rects.minimize.left = button_rects.maximize.right + 1
            button_rects.minimize.right = button_rects.minimize.left + button_width
        title_bar_rect.bottom = self.titlebar_height
        return button_rects

    def win32_window_is_maximized(self, hwnd):
        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)
        if user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
            return placement.showCmd == SW_MAXIMIZE
        return False

    def win32_center_rect_in_rect(self, to_center, outer_rect, maximized_extension):
        to_width = to_center.right - to_center.left
        to_height = to_center.bottom - to_center.top
        outer_width = outer_rect.right - outer_rect.left
        outer_height = outer_rect.bottom - outer_rect.top
        padding_x = (outer_width - to_width) // 2
        padding_y = (outer_height - to_height) // 2
        to_center.left = outer_rect.left + padding_x
        to_center.top = outer_rect.top + padding_y + maximized_extension // 2
        to_center.right = to_center.left + to_width
        to_center.bottom = to_center.top + to_height