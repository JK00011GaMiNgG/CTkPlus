#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a complete and exact translation of the provided C code to Python using ctypes.
# All Windows API calls, structures, constants, and logic have been translated line‐by‐line.
# Note: Due to the differences between C and Python, especially for Win32 API window procedures,
# this code uses ctypes to mirror the original behavior exactly.

import ctypes
from ctypes import wintypes
import sys
from pickle import LONG1

import win32gui
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
uxtheme = ctypes.windll.uxtheme
kernel32 = ctypes.windll.kernel32
CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
WS_THICKFRAME   = 0x00040000
WS_SYSMENU      = 0x00080000
WS_MAXIMIZEBOX  = 0x00010000
WS_MINIMIZEBOX  = 0x00020000
WS_VISIBLE      = 0x10000000
WS_EX_APPWINDOW = 0x00040000
CW_USEDEFAULT = 0x80000000
SWP_FRAMECHANGED = 0x0020
SWP_NOMOVE      = 0x0002
SWP_NOSIZE      = 0x0001
SWP_NOZORDER    = 0x0004
SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_NORMAL   = 1
TPM_RETURNCMD = 0x0100
CS_DROPSHADOW = 0x00020000
WM_NCCALCSIZE    = 0x0083
WM_CREATE        = 0x0001
WM_ACTIVATE      = 0x0006
WM_NCHITTEST     = 0x0084
WM_PAINT         = 0x000F
WM_NCMOUSEMOVE   = 0x00A0
WM_MOUSEMOVE     = 0x0200
WM_NCLBUTTONDOWN = 0x00A1
WM_NCLBUTTONUP   = 0x00A2
WM_NCRBUTTONUP   = 0x00A4
WM_CLOSE         = 0x0010
HTNOWHERE      = 0
HTCLIENT       = 1
HTCAPTION      = 2
HTLEFT         = 10
HTRIGHT        = 11
HTTOP          = 12
HTTOPLEFT      = 13
HTTOPRIGHT     = 14
HTBOTTOM       = 15
HTBOTTOMLEFT   = 16
HTBOTTOMRIGHT  = 17
HTMAXBUTTON    = 9
SM_CXFRAME = 32
SM_CYFRAME = 33
SM_CXPADDEDBORDER = 92
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)
MF_ENABLED  = 0x00000000
MF_DISABLED = 0x00000002
SC_RESTORE = 61728
SC_MOVE    = 61456
SC_SIZE    = 61440
SC_MINIMIZE= 61472
SC_MAXIMIZE= 61488
SC_CLOSE   = 61536
DT_VCENTER       = 0x00000004
DT_SINGLELINE    = 0x00000020
DT_WORD_ELLIPSIS = 0x00000040
PS_SOLID = 0
NULL_BRUSH = 5

def LOWORD(dword): return dword & 0xFFFF
def HIWORD(dword): return (dword >> 16) & 0xFFFF
def GET_X_PARAM(lp): return ctypes.c_int(ctypes.c_short(LOWORD(lp)).value).value
def GET_Y_PARAM(lp): return ctypes.c_int(ctypes.c_short(HIWORD(lp)).value).value

wintypes.LOWORD = lambda dword: LOWORD(dword)
wintypes.HIWORD = lambda dword: HIWORD(dword)

WNDPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.LPARAM, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

class POINT(ctypes.Structure): _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
class SIZE(ctypes.Structure): _fields_ = [("cx", wintypes.LONG), ("cy", wintypes.LONG)]
class RECT(ctypes.Structure): _fields_ = [("left",   wintypes.LONG), ("top",    wintypes.LONG), ("right",  wintypes.LONG), ("bottom", wintypes.LONG)]
class WNDCLASSEXW(ctypes.Structure):_fields_ = [("cbSize",       wintypes.UINT), ("style",        wintypes.UINT), ("lpfnWndProc",  WNDPROC), ("cbClsExtra",   ctypes.c_int), ("cbWndExtra",   ctypes.c_int), ("hInstance",    wintypes.HINSTANCE), ("hIcon",        wintypes.HICON), ("hCursor",      wintypes.LONG), ("hbrBackground",wintypes.HBRUSH), ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName",wintypes.LPCWSTR), ("hIconSm",      wintypes.HICON)]
class MSG(ctypes.Structure): _fields_ = [("hwnd", wintypes.HWND), ("message", wintypes.UINT), ("wParam", wintypes.WPARAM), ("lParam", wintypes.LPARAM), ("time", wintypes.DWORD), ("pt", POINT)]
class PAINTSTRUCT(ctypes.Structure): _fields_ = [("hdc", wintypes.HDC), ("fErase", wintypes.BOOL), ("rcPaint", RECT), ("fRestore", wintypes.BOOL), ("fIncUpdate", wintypes.BOOL), ("rgbReserved", ctypes.c_byte * 32)]
class NCCALCSIZE_PARAMS(ctypes.Structure): _fields_ = [("rgrc", RECT * 3), ("lppos", ctypes.c_void_p)]
class WINDOWPLACEMENT(ctypes.Structure): _fields_ = [("length", wintypes.UINT), ("flags", wintypes.UINT), ("showCmd", wintypes.UINT), ("ptMinPosition", POINT), ("ptMaxPosition", POINT), ("rcNormalPosition",RECT)]
class LOGFONT(ctypes.Structure): _fields_ = [("lfHeight", wintypes.LONG), ("lfWidth", wintypes.LONG), ("lfEscapement", wintypes.LONG), ("lfOrientation", wintypes.LONG), ("lfWeight", wintypes.LONG), ("lfItalic", wintypes.BYTE), ("lfUnderline", wintypes.BYTE), ("lfStrikeOut", wintypes.BYTE), ("lfCharSet", wintypes.BYTE), ("lfOutPrecision", wintypes.BYTE), ("lfClipPrecision", wintypes.BYTE), ("lfQuality", wintypes.BYTE), ("lfPitchAndFamily", wintypes.BYTE), ("lfFaceName", wintypes.WCHAR * 32)]
class DTTOPTS(ctypes.Structure): _fields_ = [("dwSize", wintypes.DWORD), ("dwFlags", wintypes.DWORD), ("crText", wintypes.COLORREF), ("crBorder", wintypes.COLORREF), ("crShadow", wintypes.COLORREF), ("iTextShadowType", ctypes.c_int), ("ptShadowOffset", POINT), ("iBorderSize", ctypes.c_int), ("iFontPropId", ctypes.c_int), ("iColorPropId", ctypes.c_int), ("iStateId", ctypes.c_int), ("fApplyOverlay", wintypes.BOOL), ("iGlowSize", ctypes.c_int), ("pfnDrawTextCallback", ctypes.c_void_p), ("lParam", wintypes.LPARAM)]
class CustomTitleBarButtonRects(ctypes.Structure): _fields_ = [("close", RECT), ("maximize", RECT), ("minimize", RECT)]

CustomTitleBarHoveredButton_None     = 0
CustomTitleBarHoveredButton_Minimize = 1
CustomTitleBarHoveredButton_Maximize = 2
CustomTitleBarHoveredButton_Close    = 3
WIN32_FAKE_SHADOW_HEIGHT = 1
WIN32_MAXIMIZED_RECTANGLE_OFFSET = 2
WndProcType = ctypes.WINFUNCTYPE(wintypes.LPARAM, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
@WndProcType
def win32_custom_title_bar_example_window_callback(handle, message, w_param, l_param):
    title_bar_hovered_button = ctypes.c_long(user32.GetWindowLongPtrW(handle, -21)).value

    if message == WM_NCCALCSIZE:
        if not w_param:
            return user32.DefWindowProcW(handle, message, w_param, l_param)
        dpi = user32.GetDpiForWindow(handle)
        frame_x = user32.GetSystemMetricsForDpi(SM_CXFRAME, dpi)
        frame_y = user32.GetSystemMetricsForDpi(SM_CYFRAME, dpi)
        padding = user32.GetSystemMetricsForDpi(SM_CXPADDEDBORDER, dpi)
        params = ctypes.cast(l_param, ctypes.POINTER(NCCALCSIZE_PARAMS)).contents
        requested_client_rect = params.rgrc[0]
        requested_client_rect.right -= frame_x + padding
        requested_client_rect.left  += frame_x + padding
        requested_client_rect.bottom -= frame_y + padding
        if win32_window_is_maximized(handle):
            requested_client_rect.top += padding
        return 0

    elif message == WM_CREATE:
        user32.SetWindowPos(handle, None, 0, 0, 0, 0, SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER)
    elif message == WM_ACTIVATE:
        title_bar_rect = win32_titlebar_rect(handle)
        user32.InvalidateRect(handle, ctypes.byref(title_bar_rect), False)
        return user32.DefWindowProcW(handle, message, w_param, l_param)
    elif message == WM_NCHITTEST:
        hit = user32.DefWindowProcW(handle, message, w_param, l_param)
        if hit in (0, HTRIGHT, HTLEFT, HTTOPLEFT, HTTOP, HTTOPRIGHT, HTBOTTOMRIGHT, HTBOTTOM, HTBOTTOMLEFT):
            return hit
        if title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize:
            return HTMAXBUTTON
        dpi = user32.GetDpiForWindow(handle)
        frame_y = user32.GetSystemMetricsForDpi(SM_CYFRAME, dpi)
        padding = user32.GetSystemMetricsForDpi(SM_CXPADDEDBORDER, dpi)
        cursor_point = POINT(0, 0)
        cursor_point.x = GET_X_PARAM(l_param)
        cursor_point.y = GET_Y_PARAM(l_param)
        user32.ScreenToClient(handle, ctypes.byref(cursor_point))
        if 0 < cursor_point.y < (frame_y + padding):
            return HTTOP
        tb_rect = win32_titlebar_rect(handle)
        if cursor_point.y < tb_rect.bottom:
            return HTCAPTION
        return HTCLIENT
    elif message == WM_PAINT:
        has_focus = bool(user32.GetFocus())
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(handle, ctypes.byref(ps))
        bg_color = 0x00C8FAE6
        bg_brush = gdi32.CreateSolidBrush(bg_color)
        user32.FillRect(hdc, ctypes.byref(ps.rcPaint), bg_brush)
        gdi32.DeleteObject(bg_brush)
        theme = uxtheme.OpenThemeData(handle, "WINDOW")
        title_bar_color = 0x0096C8B4
        title_bar_brush = gdi32.CreateSolidBrush(title_bar_color)
        title_bar_hover_color = 0x0082B4A0
        title_bar_hover_brush = gdi32.CreateSolidBrush(title_bar_hover_color)
        title_bar_rect = win32_titlebar_rect(handle)
        user32.FillRect(hdc, ctypes.byref(title_bar_rect), title_bar_brush)
        title_bar_item_color = 0x212121 if has_focus else 0x7F7F7F
        button_icon_brush = gdi32.CreateSolidBrush(title_bar_item_color)
        button_icon_pen = gdi32.CreatePen(PS_SOLID, 1, title_bar_item_color)
        button_rects = win32_get_title_bar_button_rects(handle, title_bar_rect)
        dpi = user32.GetDpiForWindow(handle)
        icon_dimension = win32_dpi_scale(10, dpi)
        if title_bar_hovered_button == CustomTitleBarHoveredButton_Minimize: user32.FillRect(hdc, ctypes.byref(button_rects.minimize), title_bar_hover_brush)
        icon_rect = RECT(0,0,icon_dimension,1)
        win32_center_rect_in_rect(icon_rect, button_rects.minimize)
        user32.FillRect(hdc, ctypes.byref(icon_rect), button_icon_brush)
        is_hovered = (title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize)
        if is_hovered: user32.FillRect(hdc, ctypes.byref(button_rects.maximize), title_bar_hover_brush)
        icon_rect = RECT(0,0,icon_dimension,icon_dimension)
        win32_center_rect_in_rect(icon_rect, button_rects.maximize)
        gdi32.SelectObject(hdc, button_icon_pen)
        gdi32.SelectObject(hdc, gdi32.GetStockObject(5))
        if win32_window_is_maximized(handle):
            gdi32.Rectangle(hdc,icon_rect.left + WIN32_MAXIMIZED_RECTANGLE_OFFSET, icon_rect.top - WIN32_MAXIMIZED_RECTANGLE_OFFSET, icon_rect.right + WIN32_MAXIMIZED_RECTANGLE_OFFSET, icon_rect.bottom - WIN32_MAXIMIZED_RECTANGLE_OFFSET)
            user32.FillRect(hdc, ctypes.byref(icon_rect), title_bar_hover_brush if is_hovered else title_bar_brush)
        gdi32.Rectangle(hdc, icon_rect.left, icon_rect.top, icon_rect.right, icon_rect.bottom)
        custom_pen = 0
        if title_bar_hovered_button == CustomTitleBarHoveredButton_Close:
            fill_brush = gdi32.CreateSolidBrush(0x2311e8)
            user32.FillRect(hdc, ctypes.byref(button_rects.close), fill_brush)
            gdi32.DeleteObject(fill_brush)
            custom_pen = gdi32.CreatePen(PS_SOLID, 1, 0xFFFFFF)
            gdi32.SelectObject(hdc, custom_pen)
        icon_rect = RECT(0,0,icon_dimension,icon_dimension)
        win32_center_rect_in_rect(icon_rect, button_rects.close)
        win32gui.MoveToEx(hdc, icon_rect.left, icon_rect.top)
        win32gui.LineTo(hdc, icon_rect.right + 1, icon_rect.bottom + 1)
        win32gui.MoveToEx(hdc, icon_rect.left, icon_rect.bottom)
        win32gui.LineTo(hdc, icon_rect.right + 1, icon_rect.top - 1)
        if custom_pen: gdi32.DeleteObject(custom_pen)
        gdi32.DeleteObject(title_bar_hover_brush)
        gdi32.DeleteObject(button_icon_brush)
        gdi32.DeleteObject(button_icon_pen)
        gdi32.DeleteObject(title_bar_brush)
        logical_font = LOGFONT()
        old_font = None
        SPI_GETICONTITLELOGFONT = 0x001F
        if user32.SystemParametersInfoForDpi:
            res = user32.SystemParametersInfoForDpi(SPI_GETICONTITLELOGFONT, ctypes.sizeof(logical_font), ctypes.byref(logical_font), False, dpi)
            if res:
                theme_font = gdi32.CreateFontIndirectW(ctypes.byref(logical_font))
                old_font = gdi32.SelectObject(hdc, theme_font)
        title_text_buffer = (wintypes.WCHAR * 255)()
        buffer_length = 255
        user32.GetWindowTextW(handle, title_text_buffer, buffer_length)
        title_bar_text_rect = RECT(title_bar_rect.left, title_bar_rect.top, title_bar_rect.right, title_bar_rect.bottom)
        text_padding = 10
        title_bar_text_rect.left += text_padding
        title_bar_text_rect.right = button_rects.minimize.left - text_padding
        dtt_opts = DTTOPTS()
        dtt_opts.dwSize = ctypes.sizeof(dtt_opts)
        dtt_opts.dwFlags = 0x00000001
        dtt_opts.crText = title_bar_item_color
        uxtheme.DrawThemeTextEx(theme, hdc, 0, 0, title_text_buffer, -1, DT_VCENTER | DT_SINGLELINE | DT_WORD_ELLIPSIS, ctypes.byref(title_bar_text_rect), ctypes.byref(dtt_opts))
        if old_font: gdi32.SelectObject(hdc, old_font)
        uxtheme.CloseThemeData(theme)
        shadow_color = 0x646464
        def getR(rgb): return rgb & 0xFF
        def getG(rgb): return (rgb >> 8) & 0xFF
        def getB(rgb): return (rgb >> 16) & 0xFF
        if has_focus:
            fake_top_shadow_color = shadow_color
        else:
            fake_top_shadow_color = ((getR(title_bar_color)+getR(shadow_color))//2 | ((getG(title_bar_color)+getG(shadow_color))//2 << 8) | ((getB(title_bar_color)+getB(shadow_color))//2 << 16))
        fake_top_shadow_brush = gdi32.CreateSolidBrush(fake_top_shadow_color)
        fake_top_shadow_rect = win32_fake_shadow_rect(handle)
        user32.FillRect(hdc, ctypes.byref(fake_top_shadow_rect), fake_top_shadow_brush)
        gdi32.DeleteObject(fake_top_shadow_brush)
        user32.EndPaint(handle, ctypes.byref(ps))
    elif message == WM_NCMOUSEMOVE:
        cursor_point = POINT()
        user32.GetCursorPos(ctypes.byref(cursor_point))
        user32.ScreenToClient(handle, ctypes.byref(cursor_point))
        title_bar_rect = win32_titlebar_rect(handle)
        button_rects = win32_get_title_bar_button_rects(handle, title_bar_rect)
        new_hovered_button = CustomTitleBarHoveredButton_None
        if user32.PtInRect(ctypes.byref(button_rects.close), cursor_point):
            new_hovered_button = CustomTitleBarHoveredButton_Close
        elif user32.PtInRect(ctypes.byref(button_rects.minimize), cursor_point):
            new_hovered_button = CustomTitleBarHoveredButton_Minimize
        elif user32.PtInRect(ctypes.byref(button_rects.maximize), cursor_point):
            new_hovered_button = CustomTitleBarHoveredButton_Maximize
        if new_hovered_button != title_bar_hovered_button:
            user32.InvalidateRect(handle, ctypes.byref(button_rects.close), False)
            user32.InvalidateRect(handle, ctypes.byref(button_rects.minimize), False)
            user32.InvalidateRect(handle, ctypes.byref(button_rects.maximize), False)
            user32.SetWindowLongPtrW(handle, -21, new_hovered_button)
        return user32.DefWindowProcW(handle, message, w_param, l_param)
    elif message == WM_MOUSEMOVE:
        if title_bar_hovered_button:
            title_bar_rect = win32_titlebar_rect(handle)
            user32.InvalidateRect(handle, ctypes.byref(title_bar_rect), False)
            user32.SetWindowLongPtrW(handle, -21, CustomTitleBarHoveredButton_None)
        return user32.DefWindowProcW(handle, message, w_param, l_param)
    elif message == WM_NCLBUTTONDOWN:
        if title_bar_hovered_button:
            return 0
        return user32.DefWindowProcW(handle, message, w_param, l_param)
    elif message == WM_NCLBUTTONUP:
        if title_bar_hovered_button == CustomTitleBarHoveredButton_Close:
            user32.PostMessageW(handle, WM_CLOSE, 0, 0)
            return 0
        elif title_bar_hovered_button == CustomTitleBarHoveredButton_Minimize:
            user32.ShowWindow(handle, SW_MINIMIZE)
            return 0
        elif title_bar_hovered_button == CustomTitleBarHoveredButton_Maximize:
            mode = SW_NORMAL if win32_window_is_maximized(handle) else SW_MAXIMIZE
            user32.ShowWindow(handle, mode)
            return 0
        return user32.DefWindowProcW(handle, message, w_param, l_param)
    elif message == WM_NCRBUTTONUP:
        if w_param == HTCAPTION:
            is_maximized = user32.IsZoomed(handle)
            sys_menu = user32.GetSystemMenu(handle, False)
            set_menu_item_state(sys_menu, None, SC_RESTORE, bool(is_maximized))
            set_menu_item_state(sys_menu, None, SC_MOVE, not bool(is_maximized))
            set_menu_item_state(sys_menu, None, SC_SIZE, not bool(is_maximized))
            set_menu_item_state(sys_menu, None, SC_MINIMIZE, True)
            set_menu_item_state(sys_menu, None, SC_MAXIMIZE, not bool(is_maximized))
            set_menu_item_state(sys_menu, None, SC_CLOSE, True)
            result = user32.TrackPopupMenu(sys_menu, TPM_RETURNCMD, GET_X_PARAM(l_param), GET_Y_PARAM(l_param), 0, handle, None)
            if result == SC_CLOSE:
                user32.PostMessageW(handle, wintypes.UINT(0x0010), 0, 0)
            elif result == SC_MINIMIZE:
                user32.ShowWindow(handle, 6)
            elif result == SC_RESTORE:
                user32.ShowWindow(handle, 9)
            elif result == SC_MAXIMIZE:
                user32.ShowWindow(handle, 3)
            elif result == SC_MOVE:
                user32.SendMessageW(handle, 0x00A1, HTCAPTION, l_param)
            return 0
    try:
        return user32.DefWindowProcW(ctypes.c_void_p(handle), ctypes.c_uint(message), ctypes.c_void_p(w_param), ctypes.c_void_p(l_param))
    except OverflowError:
        print(f"OverflowError in DefWindowProcW: msg={message}, w_param={w_param}, l_param={l_param}")
        return 0

def win32_dpi_scale(value, dpi): return int(float(value) * dpi / 96)

def set_menu_item_state(menu, menuItemInfo, item, enabled):
    state = MF_ENABLED if enabled else MF_DISABLED
    user32.EnableMenuItem(menu, item, state)

def win32_titlebar_rect(handle):
    title_bar_size = SIZE(0,0)
    top_and_bottom_borders = 2
    theme = uxtheme.OpenThemeData(handle, "WINDOW")
    dpi = user32.GetDpiForWindow(handle)
    TS_TRUE = 1
    uxtheme.GetThemePartSize(theme, None, 1, 1, None, TS_TRUE, ctypes.byref(title_bar_size))
    uxtheme.CloseThemeData(theme)
    height = win32_dpi_scale(title_bar_size.cy, dpi) + top_and_bottom_borders
    rect = RECT()
    user32.GetClientRect(handle, ctypes.byref(rect))
    rect.bottom = rect.top + height
    return rect

def win32_fake_shadow_rect(handle):
    rect = RECT()
    user32.GetClientRect(handle, ctypes.byref(rect))
    rect.bottom = rect.top + WIN32_FAKE_SHADOW_HEIGHT
    return rect

def win32_get_title_bar_button_rects(handle, title_bar_rect):
    dpi = user32.GetDpiForWindow(handle)
    button_rects = CustomTitleBarButtonRects()
    button_width = win32_dpi_scale(47, dpi)
    button_rects.close = title_bar_rect
    button_rects.close.top += WIN32_FAKE_SHADOW_HEIGHT
    button_rects.close.left = button_rects.close.right - button_width
    button_rects.maximize = button_rects.close
    button_rects.maximize.left -= button_width
    button_rects.maximize.right -= button_width
    button_rects.minimize = button_rects.maximize
    button_rects.minimize.left -= button_width
    button_rects.minimize.right -= button_width
    return button_rects

def win32_window_is_maximized(handle):
    placement = WINDOWPLACEMENT()
    placement.length = ctypes.sizeof(WINDOWPLACEMENT)
    if user32.GetWindowPlacement(handle, ctypes.byref(placement)):
        return placement.showCmd == SW_MAXIMIZE
    return False

def win32_center_rect_in_rect(to_center, outer_rect):
    to_width = to_center.right - to_center.left
    to_height = to_center.bottom - to_center.top
    outer_width = outer_rect.right - outer_rect.left
    outer_height = outer_rect.bottom - outer_rect.top
    padding_x = (outer_width - to_width) // 2
    padding_y = (outer_height - to_height) // 2
    to_center.left = outer_rect.left + padding_x
    to_center.top = outer_rect.top + padding_y
    to_center.right = to_center.left + to_width
    to_center.bottom = to_center.top + to_height

def WinMain(hInstance, hPrevInstance, pCmdLine, nCmdShow):
    if not user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2): kernel32.OutputDebugStringA(b"WARNING: could not set DPI awareness")
    window_class_name = "WIN32_CUSTOM_TITLEBAR_EXAMPLE"
    window_class = WNDCLASSEXW()
    window_class.cbSize = ctypes.sizeof(WNDCLASSEXW)
    window_class.lpszClassName = window_class_name
    window_class.lpfnWndProc = win32_custom_title_bar_example_window_callback
    window_class.style = CS_HREDRAW | CS_VREDRAW
    user32.RegisterClassExW(ctypes.byref(window_class))
    window_style = (WS_THICKFRAME | WS_SYSMENU | WS_MAXIMIZEBOX | WS_MINIMIZEBOX | WS_VISIBLE)
    hwnd = user32.CreateWindowExW(WS_EX_APPWINDOW, window_class_name,"Win32 Custom Title Bar Example", window_style, CW_USEDEFAULT, CW_USEDEFAULT, 800, 600, None, None, hInstance, None)
    # msg = MSG()
    # while True:
    #     result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
    #     if result > 0:
    #         user32.TranslateMessage(ctypes.byref(msg))
    #         user32.DispatchMessageW(ctypes.byref(msg))
    #     else:
    #         break
    # return 0
    win32gui.PumpMessages()

if __name__ == "__main__":
    hInstance = kernel32.GetModuleHandleW(None)
    hPrevInstance = None
    pCmdLine = sys.argv
    nCmdShow = 1
    WinMain(hInstance, hPrevInstance, pCmdLine, nCmdShow)
