import psutil
import win32process, win32gui
import datetime
from pywinauto.application import Application
import json
import customtkinter
import threading
from PIL import Image

"""
brave.exe
vivaldi.exe

a_string = "chrome.exe something something"
print(any([x in a_string for x in matches]))
"""

class Activity:
    def __init__(self) -> None:
        self.fname = "dev.json"
        self.active_app = ""
        self.active_url = ""
        self.today_date = str(datetime.datetime.now()).split(" ")[0]
        self.start_time = datetime.datetime.now()
        self.gui_done = False

        jsonobj = open(self.fname,"r")
        self.activities = json.load(jsonobj)
        jsonobj.close()
        self.tracked_before = []
        if self.today_date in self.activities:
            for apps in self.activities[self.today_date]:
                self.tracked_before.append(apps)
        else:
            self.activities.update({self.today_date:{}})

        self.browsernames =["chrome.exe","msedge.exe","launcher.exe","firefox.exe"]
        self.unwanted = ["ONLINENT.EXE","SearchApp.exe","rundll32.exe","ShellExperienceHost.exe"]


        gui_thread = threading.Thread(target=self.guiLoop)
        gui_thread.start()
        # self.activity()
        # self.guiLoop()

    def update_json(self,key,end_time,start_time):
        time = str(end_time-start_time).split(".")[0]
        st = int(time.split(":")[2])
        if st > 3 and key not in self.unwanted and "." in key:
            if key in self.tracked_before:
                self.activities[self.today_date][key].insert(0,[str(start_time).split(".")[0],str(end_time).split(".")[0],time])
            elif key not in self.tracked_before:
                self.tracked_before.append(key)
                self.activities[self.today_date].update({key:[[str(start_time).split(".")[0],str(end_time).split(".")[0],time]]})
            
            jsonwr = open(self.fname,"w")
            json.dump(self.activities,jsonwr,indent=4)
            jsonwr.close()
            print(key)
            print(time)

    def get_app_name(self):
        hwnd = win32gui.GetForegroundWindow()
        _,pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        process_name = process.name()
        return pid,process_name

    def get_url(self,pid,appname):
        app = Application(backend="uia").connect(process=pid, time_out=10)
        dlg = app.top_window()

        if appname == self.browsernames[0]:
            url = dlg.child_window(title="Address and search bar", control_type="Edit").get_value().split("/")[0]
        elif appname == self.browsernames[1]:
            wrapper = dlg.child_window(title="App bar", control_type="ToolBar")
            url = wrapper.descendants(control_type='Edit')[0].get_value()
        elif appname == self.browsernames[2]:
            url = dlg.child_window(title="Address field", control_type="Edit").get_value()
        elif appname == self.browsernames[3]:
            url = dlg.child_window(title="Search with Google or enter address", auto_id="urlbar-input", control_type="Edit").get_value()
        url = url.replace("https://","")
        url = url.split("/")[0]
        return url
    
    def activity(self):
        while True:
            # print("here")
            try:
                pid,app_name = self.get_app_name()
                if app_name in self.browsernames:
                    url = self.get_url(pid,app_name)
                    if self.active_url == "":
                        self.active_url == url
                    elif self.active_app not in self.browsernames:
                        print("here")
                        self.end_time = datetime.datetime.now()
                        self.update_json(self.active_app, self.end_time,self.start_time)
                        self.active_app = app_name
                        self.start_time = datetime.datetime.now()
                    elif self.active_url != url:
                        self.end_time = datetime.datetime.now()
                        self.update_json(self.active_url, self.end_time,self.start_time)
                        self.start_time = datetime.datetime.now()
                    self.active_url = url
                    # print(active_app)

                if app_name not in self.browsernames :
                    if self.active_app == "":
                        self.active_app = app_name
                    elif self.active_app in self.browsernames:
                        self.end_time = datetime.datetime.now()
                        self.update_json(self.active_url, self.end_time,self.start_time)
                        self.start_time = datetime.datetime.now()
                    elif self.active_app != app_name :
                        self.end_time = datetime.datetime.now()
                        self.update_json(self.active_app, self.end_time,self.start_time)
                        self.start_time = datetime.datetime.now()
                    self.active_app = app_name
            except KeyboardInterrupt:
                self.end_time = datetime.datetime.now()
                if self.active_app in self.browsernames:
                    self.update_json(self.active_url, self.end_time,self.start_time)
                else:
                    self.update_json(self.active_app, self.end_time,self.start_time)
                break
            except Exception as e:
                # print(e)
                pass
          

    def guiLoop(self):
        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("dark-blue")
        self.app = customtkinter.CTk(fg_color="#151515")
        self.app.geometry("1000x520")
        # use a colour sceheme of dark-gold-white and if possible blue
        # https://dribbble.com/shots/19514541-Activity-Tracking-Dashboardcan take this as a example
        self.app.grid_columnconfigure((0,1,2), weight=1)
        self.app.grid_rowconfigure(0, weight=1)
        self.app.title("Tracked")

        # ===================Frame Left=========================
        self.frame_left = customtkinter.CTkFrame(master=self.app, width=200,height=520,fg_color="#363636")
        self.frame_left.configure(corner_radius=20)
        self.frame_left.grid(row=0, column=0,padx=15,pady=15,sticky="nsew")
        # ===================Frame Center=========================
        self.frame_center = customtkinter.CTkScrollableFrame(master=self.app, width=420,height=520,fg_color="#151515")
        self.frame_center.configure(corner_radius=20)
        self.frame_center.grid(row=0, column=1 ,padx=0,pady=10,sticky="nsew")

        # ===================Frame Right=========================
        self.frame_right = customtkinter.CTkScrollableFrame(master=self.app, width=300,height=520,fg_color="#363636")
        self.frame_right.configure(corner_radius=20)
        self.frame_right.grid(row=0, column=2,padx=15,pady=15,sticky="nsew")

        # ===================Frame Left Components=========================
        my_image = customtkinter.CTkImage(light_image=Image.open('images/logo.png'),
                                   dark_image=Image.open('images/logo.png'),
                                   size=(100,100)
                                   )
        self.logo = customtkinter.CTkLabel(self.frame_left,image=my_image,text="")
        self.logo.grid(row=1,column=0,pady=10,padx=5,sticky="nsew")

        self.overview = customtkinter.CTkButton(self.frame_left, text="Overview")
        self.overview.configure(font=("Roboto",16), fg_color="#363636", hover_color="gray5",anchor="center")
        self.overview.grid(row=2, column=0,pady=5,padx=5,sticky="nsew")

        self.detailed = customtkinter.CTkButton(self.frame_left, text="Detailed")
        self.detailed.configure(font=("Roboto",16), fg_color="#363636", hover_color="gray5",anchor="center")
        self.detailed.grid(row=3, column=0,pady=5,padx=5,sticky="nsew")

        self.settings = customtkinter.CTkButton(self.frame_left, text="Settings")
        self.settings.configure(font=("Roboto",16), fg_color="#363636", hover_color="gray5",anchor="center")
        self.settings.grid(row=4, column=0,pady=5,padx=5,sticky="nsew")

        # ===================Frame Right Components=========================
        self.heading = customtkinter.CTkLabel(self.frame_right,text="Activity Tracking",font=("Roboto",27),justify="left")
        self.heading.grid(row=1,column=0,padx=5,sticky="nsew")

        self.date_g = customtkinter.CTkLabel(self.frame_right,text=datetime.datetime.today().strftime("%A,%d %b"),font=("Roboto",13),anchor="w",justify="left")
        self.date_g.grid(row=2,column=0,padx=5,sticky="nsew")
        


        self.gui_done = True
        self.overview_com = [self.overview,self.detailed]
        self.app.mainloop()

acti = Activity()