import ctypes
import win32gui #pip package = pywin32

def all_hwnds() -> list[int]:
    """returns a list of window handles for all visible windows."""

    enumWindows = ctypes.windll.user32.EnumWindows
    enumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
    hwnd_list = []

    def foreach_window(hwnd, lParam):
        if ctypes.windll.user32.IsWindowVisible(hwnd) != 0:
            # DWM Cloaked Check
            is_cloaked = ctypes.c_int(0)
            ctypes.WinDLL("dwmapi").DwmGetWindowAttribute(hwnd, 14, ctypes.byref(is_cloaked), ctypes.sizeof(is_cloaked))
            if is_cloaked.value == 0:
                hwnd_list.append(hwnd)

        return True

    enumWindows(enumWindowsProc(foreach_window), 0)

    return hwnd_list
    
def pid_of_hwnd(hwnd: int) -> int:
    """returns the name of the executable that belongs to the window"""
    lpdw_process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
    process_id = lpdw_process_id.value

    return process_id
    
def window_position(hwnd: int) -> (int, int, int, int):
    """return: left, top, right, bottom pixel position of a window"""
    rect = wintypes.RECT()
    ff = ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
    # print(rect.left, rect.top, rect.right, rect.bottom)
    return rect.left, rect.top, rect.right, rect.bottom


def window_to_foreground(hwnd: int, e=None) -> None:
    """bring window to front"""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                          win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
    ctypes.windll.user32.SwitchToThisWindow(hwnd, True)


def window_minimize(hwnd: int, e=None) -> None:
    ctypes.windll.user32.CloseWindow(hwnd)


def window_close(hwnd: int, e=None) -> None:
    ctypes.windll.user32.PostMessageA(hwnd, 0x10, 0, 0)


def window_title(hwnd: int) -> str:
    """returns title of window"""
    text_len_in_characters = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    string_buffer = ctypes.create_unicode_buffer(
        text_len_in_characters + 1)  # +1 for the \0 at the end of the null-terminated string.
    ctypes.windll.user32.GetWindowTextW(hwnd, string_buffer, text_len_in_characters + 1)

    # fixme: ambiguous if an error or title is empty.
    result = string_buffer.value
    # if result == "":
    #     result = '<NO TITLE>'
    return result


def rename_window_title(hwnd: int, title: str = "") -> None:
    """new title for given window"""
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowtextw
    try:
        ctypes.windll.user32.SetWindowTextW(hwnd, title)

    except Exception as e:
        print(e)
        pass


def check_priviliges(hwnd: int) -> bool:
    """tries to change a windows title to test if we got the priviliges to do it"""
    orig_title = window_title(hwnd)
    dummy_title = ''
    if orig_title == '':
        dummy_title = 'testifican'
    rename_window_title(hwnd, dummy_title)
    if window_title(hwnd) == orig_title:
        return True
    if window_title(hwnd) == dummy_title:
        rename_window_title(hwnd, orig_title)
        return False
