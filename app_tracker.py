import psutil
import win32process, win32gui

previous_process = ""


while True:
    try:
        hwnd = win32gui.GetForegroundWindow()
        _,pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        process_name = process.name()
    except:
        pass
    if process_name != previous_process:
        print(process_name)
        previous_process = process_name