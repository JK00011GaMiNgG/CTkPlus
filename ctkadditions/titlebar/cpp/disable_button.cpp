#include <windows.h>

extern "C" __declspec(dllexport) void disableCloseButton(HWND hwnd) {
    if (!hwnd) return;
    HMENU hMenu = GetSystemMenu(hwnd, FALSE);
    if (hMenu) {
        EnableMenuItem(hMenu, SC_CLOSE, MF_GRAYED);
    }
}

extern "C" __declspec(dllexport) void disableMaximizeButton(HWND hwnd) {
	if (!hwnd) return;
	LONG style = GetWindowLong(hwnd, GWL_STYLE);
	style &= ~WS_MAXIMIZEBOX;
	SetWindowLong(hwnd, GWL_STYLE, style);
	SetWindowPos(hwnd, nullptr, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED);
}

extern "C" __declspec(dllexport) void disableMinimizeButton(HWND hwnd) {
	if (!hwnd) return;
	LONG style = GetWindowLong(hwnd, GWL_STYLE);
	style &= ~WS_MINIMIZEBOX;
	SetWindowLong(hwnd, GWL_STYLE, style);
	SetWindowPos(hwnd, nullptr, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED);
}