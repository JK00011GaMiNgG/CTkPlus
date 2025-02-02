import win32api
import win32con
import win32gui
import ctypes

class CustomWindow:
    def __init__(self):
        self.hinst = win32api.GetModuleHandle(None)
        self.class_name = "CustomWindowClass"

        # Register the window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.window_proc  # Set the window procedure
        wc.lpszClassName = self.class_name
        wc.hbrBackground = win32con.COLOR_WINDOW + 1
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        self.class_atom = win32gui.RegisterClass(wc)

        # Create the window with appropriate styles (including WS_CAPTION for title bar)
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_APPWINDOW,
            self.class_name,
            "Custom Window",
            win32con.WS_OVERLAPPEDWINDOW,  # Includes the title bar and border
            100, 100, 800, 600,
            0, 0, self.hinst, None
        )

        # Set the window style to ensure no default drawing of non-client area
        current_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, current_style & ~win32con.WS_CAPTION)  # Disable default title bar

        # Show the window
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)

    def on_ncpaint(self, hwnd, msg, wparam, lparam):
        """ Paint the non-client area, painting over the default Windows styles """
        # First, draw the default non-client area (title bar, etc.)
        win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

        # Now do custom painting after Windows paints the default non-client area
        hdc = win32gui.GetWindowDC(hwnd)

        # Get window dimensions
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        # Paint custom buttons (close, maximize, minimize)
        btn_width = 50
        btn_height = 32

        # Define button rectangles
        close_btn_rect = (width - btn_width, 0, width, btn_height)
        maximize_btn_rect = (width - (btn_width * 2), 0, width - btn_width, btn_height)
        minimize_btn_rect = (width - (btn_width * 3), 0, width - (btn_width * 2), btn_height)

        # Create a brush for painting buttons
        normal_brush = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 255))

        # Paint the buttons (you can customize this as needed)
        win32gui.FillRect(hdc, close_btn_rect, normal_brush)
        win32gui.FillRect(hdc, maximize_btn_rect, normal_brush)
        win32gui.FillRect(hdc, minimize_btn_rect, normal_brush)

        # Draw text inside buttons
        font = win32gui.GetStockObject(win32con.SYSTEM_FONT)
        win32gui.SelectObject(hdc, font)
        win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)

        # Draw text on buttons
        win32gui.DrawText(hdc, "✕", -1, close_btn_rect, win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE)
        win32gui.DrawText(hdc, "❐", -1, maximize_btn_rect, win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE)
        win32gui.DrawText(hdc, "--", -1, minimize_btn_rect, win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE)

        # Clean up brushes and release the device context
        win32gui.DeleteObject(normal_brush)
        win32gui.ReleaseDC(hwnd, hdc)

        return 0

    def on_size(self, hwnd, msg, wparam, lparam):
        """ Handle resizing events to ensure proper custom drawing """
        # Force a repaint of the non-client area after resizing
        win32gui.InvalidateRect(hwnd, None, True)
        return 0

    def on_activate(self, hwnd, msg, wparam, lparam):
        """ Handle activation (focus) to reapply custom styles if needed """
        # Force repaint of the non-client area to prevent default Windows styling
        win32gui.InvalidateRect(hwnd, None, True)
        return 0

    def window_proc(self, hwnd, msg, wparam, lparam):
        """ Window procedure to handle messages """
        if msg == win32con.WM_NCPAINT:
            return self.on_ncpaint(hwnd, msg, wparam, lparam)
        elif msg == win32con.WM_SIZE:
            return self.on_size(hwnd, msg, wparam, lparam)
        elif msg == win32con.WM_ACTIVATE:
            return self.on_activate(hwnd, msg, wparam, lparam)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def run(self):
        win32gui.PumpMessages()

if __name__ == "__main__":
    app = CustomWindow()
    app.run()