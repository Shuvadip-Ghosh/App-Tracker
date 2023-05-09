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
fname = "dev.json"
active_app = ""
active_url = ""
today_date = str(datetime.datetime.now()).split(" ")[0]
start_time = datetime.datetime.now()

jsonobj = open(fname,"r")
activities = json.load(jsonobj)
jsonobj.close()
tracked_before = []
if today_date in activities:
    for apps in activities[today_date]:
        tracked_before.append(apps)
else:
    activities.update({today_date:{}})

browsernames =["chrome.exe","msedge.exe","launcher.exe","firefox.exe"]
unwanted = ["ONLINENT.EXE","SearchApp.exe","rundll32.exe","ShellExperienceHost.exe"]

def update_json(key,start_time,end_time,time):
    st = int(time.split(":")[2])
    if st > 3 and key not in unwanted and "." in key:
        if key in tracked_before:
            activities[today_date][key].insert(0,[str(start_time).split(".")[0],str(end_time).split(".")[0],time])
        elif key not in tracked_before:
            tracked_before.append(key)
            activities[today_date].update({key:[[str(start_time).split(".")[0],str(end_time).split(".")[0],time]]})
        
        jsonwr = open(fname,"w")
        json.dump(activities,jsonwr,indent=4)
        jsonwr.close()
        print(key)
        print(time)

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
        url = dlg.child_window(title="Address and search bar", control_type="Edit").get_value().split("/")[0]
    elif appname == browsernames[1]:
        wrapper = dlg.child_window(title="App bar", control_type="ToolBar")
        url = wrapper.descendants(control_type='Edit')[0].get_value()
    elif appname == browsernames[2]:
        url = dlg.child_window(title="Address field", control_type="Edit").get_value()
    elif appname == browsernames[3]:
        url = dlg.child_window(title="Search with Google or enter address", auto_id="urlbar-input", control_type="Edit").get_value()
    url = url.replace("https://","")
    url = url.split("/")[0]
    return url

while True:
    # print("here")
    try:
        pid,app_name = get_app_name()
        if app_name in browsernames:
            url = get_url(pid,app_name)
            if active_url == "":
                active_url == url
            elif active_app not in browsernames:
                end_time = datetime.datetime.now()
                update_json(active_app, end_time,start_time,str(end_time-start_time).split(".")[0])
                active_app = app_name
                start_time = datetime.datetime.now()
            elif active_url != url:
                end_time = datetime.datetime.now()
                update_json(active_url, end_time,start_time,str(end_time-start_time).split(".")[0])
                start_time = datetime.datetime.now()
            active_url = url
            # print(active_app)

        if app_name not in browsernames :
            if active_app == "":
                active_app = app_name
            elif active_app in browsernames:
                end_time = datetime.datetime.now()
                update_json(active_url, end_time,start_time,str(end_time-start_time).split(".")[0])
                start_time = datetime.datetime.now()
            elif active_app != app_name :
                end_time = datetime.datetime.now()
                update_json(active_app, end_time,start_time,str(end_time-start_time).split(".")[0])
                start_time = datetime.datetime.now()
            active_app = app_name
    except KeyboardInterrupt:
        end_time = datetime.datetime.now()
        if active_app in browsernames:
            update_json(active_url, end_time,start_time,str(end_time-start_time).split(".")[0])
        else:
            update_json(active_app, end_time,start_time,str(end_time-start_time).split(".")[0])
        break
    except:
        pass