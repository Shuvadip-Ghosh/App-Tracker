import psutil
import win32process, win32gui
import datetime
from pywinauto.application import Application
import json

"""
brave.exe
vivaldi.exe

a_string = "chrome.exe something something"
print(any([x in a_string for x in matches]))
"""

active_app = ""
active_url = ""
start_time = datetime.datetime.now()
browsernames =["chrome.exe","msedge.exe","launcher.exe","firefox.exe"]

def get_app_name():
    hwnd = win32gui.GetForegroundWindow()
    _,pid = win32process.GetWindowThreadProcessId(hwnd)
    process = psutil.Process(pid)
    process_name = process.name()
    return pid,process_name

def get_url(pid,appname):
    app = Application(backend="uia").connect(process=pid, time_out=10)
    dlg = app.top_window()

    if appname == browsernames[0]:
        url = dlg.child_window(title="Address and search bar", control_type="Edit").get_value()
    elif appname == browsernames[1]:
        wrapper = dlg.child_window(title="App bar", control_type="ToolBar")
        url = wrapper.descendants(control_type='Edit')[0].get_value()
    elif appname == browsernames[2]:
        url = dlg.child_window(title="Address field", control_type="Edit").get_value()
    elif appname == browsernames[3]:
        url = dlg.child_window(title="Search with Google or enter address", auto_id="urlbar-input", control_type="Edit").get_value()

    return url

while True:
    try:
        pid,app_name = get_app_name()
        if app_name in browsernames:
            url = get_url(pid,app_name)
            if active_url == "":
                active_url == url
            elif active_app not in browsernames:
                end_time = datetime.datetime.now()
                print(active_app)
                print(str(end_time-start_time).split(".")[0])
                active_app = app_name
                start_time = datetime.datetime.now()
            elif active_url != url:
                end_time = datetime.datetime.now()
                print(active_url)
                print(str(end_time-start_time).split(".")[0])
                start_time = datetime.datetime.now()
            active_url = url

        if app_name not in browsernames :
            if active_app == "":
                active_app = app_name
            elif active_app in browsernames:
                end_time = datetime.datetime.now()
                print(active_url)
                print(str(end_time-start_time).split(".")[0])
                start_time = datetime.datetime.now()
            elif active_app != app_name :
                end_time = datetime.datetime.now()
                print(active_app)
                print(str(end_time-start_time).split(".")[0])
                start_time = datetime.datetime.now()
            active_app = app_name
        
    except KeyboardInterrupt:
        break
    except:
        pass