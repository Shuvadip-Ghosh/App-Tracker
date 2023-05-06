import psutil
import win32process, win32gui
import time

browsernames ="""
chrome.exe
msedge.exe

firefox.exe
launcher.exe opera
brave.exe
vivaldi.exe
"""


previous_process = ""
start_time = time.time()
while True:
    try:
        hwnd = win32gui.GetForegroundWindow()
        _,pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        process_name = process.name()
    except:
        pass
    if process_name != previous_process:
        if previous_process !="":
            end_time = time.time()
            print(end_time-start_time)
            start_time = time.time()
        
        print(process_name)
        previous_process = process_name