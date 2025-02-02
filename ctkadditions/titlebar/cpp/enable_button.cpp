#include <windows.h>

extern "C" __declspec(dllexport) void enableCloseButton(HWND hwnd) {
	if (!hwnd) return;
	HMENU hMenu = GetSystemMenu(hwnd, FALSE);
	if (hMenu) {
		EnableMenuItem(hMenu, SC_CLOSE, MF_ENABLED);
	}
}

extern "C" __declspec(dllexport) void enableMaximizeButton(HWND hwnd) {
	if (!hwnd) return;
	LONG style = GetWindowLong(hwnd, GWL_STYLE);
	style |= WS_MAXIMIZEBOX;
	SetWindowLong(hwnd, GWL_STYLE, style);
	SendMessage(hwnd, WM_SYSCOMMAND, SC_RESTORE, 0);
	SetWindowPos(hwnd, nullptr, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED);
}

extern "C" __declspec(dllexport) void enableMinimizeButton(HWND hwnd) {
	if (!hwnd) return;
	LONG style = GetWindowLong(hwnd, GWL_STYLE);
	style |= WS_MINIMIZEBOX;
	SetWindowLong(hwnd, GWL_STYLE, style);
	SendMessage(hwnd, WM_SYSCOMMAND, SC_RESTORE, 0);
	SetWindowPos(hwnd, nullptr, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED);
}