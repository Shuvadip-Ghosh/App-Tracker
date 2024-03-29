import psutil # pip install psutil
from pywinauto.application import Application # pip install pywinauto
from PIL import Image # pip install pillow
import pystray # pip install pystary
import win32com.client # pip install pywin32

import win32process, win32gui

import customtkinter
import datetime
import json
import threading
from multiprocessing import Queue,Process
import time
import os
import sys
import getpass


"""
brave.exe
vivaldi.exe

a_string = "chrome.exe something something"
print(any([x in a_string for x in matches]))
"""

class GraphicalUserInterface:
    def __init__(self,rnq,fname) -> None:
        self.fname = fname
        self.first_time = True
        self.active_frame = ""
        self.guiframes = {
            "home":"self.home",
            "details":"self.details",
            "settings":"self.settings"
        }
        self.today_date = str(datetime.datetime.now()).split(" ")[0]
        self.start_time = datetime.datetime.now()
        self.dates = [self.start_time + datetime.timedelta(days=i) for i in range(0 - self.start_time.weekday(), 7 - self.start_time.weekday())]
        self.gui_done = False
        self.running=rnq

        sttobj = open("data/settings.json","r")
        self.settings_js = json.load(sttobj)
        sttobj.close()

        jsonobj = open(self.fname,"r")
        self.activities = json.load(jsonobj)
        jsonobj.close()
    
    def start(self):
        self.gui_thread = threading.Thread(target=self.guiLoop)
        self.tray = threading.Thread(target=self.systray)

        self.gui_thread.start()
        self.tray.start()
        time.sleep(1)
        self.get_total_times()
        self.setting_checker()
        self.gui_time()
        self.active_frame = self.guiframes["home"]
        
        # while True:
        #     for thread in threading.enumerate():
        #         print(thread.name)
        #     time.sleep(4)

    
    def get_activities(self):
        jsonobj = open(self.fname,"r")
        self.activities = json.load(jsonobj)
        jsonobj.close()
    
    def add_to_startup(self):
        startup_folder_file = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\App Meter.lnk"
        # code to create shortcut using python and send it to the startup_folder

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(startup_folder_file)
        shortcut.TargetPath = os.path.join(os.getcwd(),f"{os.path.basename(sys.argv[0])}")
        logo_path = os.path.join(os.getcwd(),"images\\logo.ico")
        shortcut.IconLocation = f"{logo_path},{0}"
        shortcut.Save()

        self.settings_js["added_to_startup_folder"] = True
        self.settings_json_update("update")

    def remove_from_startup(self):
        startup_folder_file = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\App Meter.lnk"
        # code to remove shortcut from startup_folder using python 
        try:
            os.remove(startup_folder_file)
        except OSError as e:
            pass

        self.settings_js["added_to_startup_folder"] = False
        self.settings_json_update("update")

    def window(self,op):
        if op == "show":
            try:
                self.showing = "Hide"
                self.icon.update_menu()
                self.app.after(0,self.app.deiconify())
            except:
                pass
        elif op == "quit":
            try:
                self.running = False
                self.gui_time_th.cancel()
                print("time")
                self.icon.stop()
                print("icon")
                self.setting_checker_thread.cancel()
                print("setting")
                self.app.quit()
                self.app.destroy()
                print("app")
            except Exception as e:
                print(e)
        elif op=="hide":
            try:
                self.app.withdraw()
                self.showing = "Show"
                self.icon.update_menu()
            except:
                pass

    def systray(self):
        image=Image.open("images/logo.ico")
        if self.settings_js["start_min"]:
            self.showing = "Show"
            self.menu=(pystray.MenuItem('Quit', lambda: self.window("quit")), 
                       pystray.MenuItem(lambda text:self.showing, lambda: self.window(self.showing.lower())))
        else:
            self.showing = "Hide"
            self.menu=(pystray.MenuItem('Quit', lambda: self.window("quit")),
                       pystray.MenuItem(lambda text:self.showing, lambda: self.window(self.showing.lower())))
        self.icon=pystray.Icon("App Meter", image, "App Meter shortcut", self.menu)
        self.icon.run()

    def setting_checker(self):
        if self.app.state() == "normal" and self.settings_js["start_min"] and self.first_time:
            self.window("hide")

        if self.settings_js["launch_startup"] and not self.settings_js["added_to_startup_folder"]:
            self.add_to_startup()

        if not self.settings_js["launch_startup"] and self.settings_js["added_to_startup_folder"]:
            self.remove_from_startup()()

        if self.first_time:
            self.first_time=False

        if self.running == False:
            self.window("quit")
        
        if self.running:
            self.setting_checker_thread = threading.Timer(5.0,self.setting_checker)
            self.setting_checker_thread.start()

    def settings_json_update(self,wid,v=""):
        if wid == "min_win":
            if self.min_win.get():
                self.app.after(0,self.app.wm_protocol('WM_DELETE_WINDOW', lambda:self.window("hide")))
            if not self.min_win.get():
                self.app.after(0,self.app.wm_protocol('WM_DELETE_WINDOW', lambda:self.window("quit")))
            self.settings_js[wid] = self.min_win.get()

        elif wid == "launch_startup":
            if self.launch.get() and not self.settings_js["added_to_startup_folder"]:
                self.add_to_startup()
            elif not self.launch.get() and self.settings_js["added_to_startup_folder"]:
                self.remove_from_startup()
            self.settings_js[wid] = self.launch.get()

        elif wid == "start_min":
            self.settings_js[wid] = self.startmin.get()
        
        else:
            pass

        
        jsonwr = open("data/settings.json","w")
        json.dump(self.settings_js,jsonwr,indent=4)
        jsonwr.close()

    def get_total_times(self):
        self.get_activities()
        self.tm = {}
        t = datetime.timedelta(seconds=0,hours=0,minutes=0)
        for s in self.activities:
            for g in self.activities[s]:
                time_tot= datetime.timedelta(seconds=0,hours=0,minutes=0)
                for f in self.activities[s][g]:
                    time_tot = time_tot+datetime.timedelta(hours=int(f[2].split(":")[0]),minutes=int(f[2].split(":")[1]),seconds=int(f[2].split(":")[2]))
                if g in self.tm:
                    self.tm[g].append(time_tot)
                else:
                    self.tm.update({g:[time_tot]})
        for a in self.tm:
            tt= datetime.timedelta(seconds=0,hours=0,minutes=0)
            for ts in self.tm[a]:
                tt =tt+ts
            self.tm[a] = tt
        self.tm = dict(sorted(self.tm.items(), key=lambda item: item[1]))
        self.total_time_per_app = list(self.tm.items())

    def gui_time(self, b=False):
        if self.gui_done and self.running:
            self.get_activities()
            self.tlist = []
            tot = datetime.timedelta(seconds=0,hours=0,minutes=0)
            for i in self.dates:
                if i.strftime("%Y-%m-%d") in self.activities:
                    time_tot= datetime.timedelta(seconds=0,hours=0,minutes=0)
                    for g in self.activities[i.strftime("%Y-%m-%d")]:
                        for f in self.activities[i.strftime("%Y-%m-%d")][g]:
                            time_tot = time_tot+datetime.timedelta(hours=int(f[2].split(":")[0]),minutes=int(f[2].split(":")[1]),seconds=int(f[2].split(":")[2]))
                    tot=tot+time_tot
                    self.tlist.append(time_tot.seconds)
                elif i.strftime("%Y-%m-%d") not in self.activities:
                    self.tlist.append(0)
            
            t = datetime.timedelta(seconds=0,hours=0,minutes=0)
            for s in self.activities:
                for g in self.activities[s]:
                    for f in self.activities[s][g]:
                        t = t+datetime.timedelta(hours=int(f[2].split(":")[0]),minutes=int(f[2].split(":")[1]),seconds=int(f[2].split(":")[2]))
            # print(t)
            # print(tot)
            # print(self.tlist)
            try:
                self.tot_time_all.configure(text=f"{str(t).split(':')[0]}h {str(t).split(':')[1]}m")
                handm = str(datetime.timedelta(seconds=tot.seconds)).split(":")
                self.tot_time.configure(text=f"{handm[0]}h {handm[1]}m")
                for j,m in enumerate(self.tlist):
                    eval(f"self.slider{j}").set(m/tot.seconds)
            except:
                if self.active_frame != self.guiframes["details"] or b == True:
                    for j,m in enumerate(self.tlist):
                        eval(f"self.slider{j}").set(0)
            
            self.gui_time_th = threading.Timer(30.0,self.gui_time)
            self.gui_time_th.start()
    
    def gui_create_sidebar(self):
        # ===================Frame Left=========================
        self.frame_left = customtkinter.CTkFrame(master=self.app,width=100,height=520,fg_color="#1b1b1b")
        self.frame_left.configure(corner_radius=20)
        self.frame_left.grid(row=0, column=0,padx=0,pady=15,sticky="nsw")

        # ===================Frame Left Components=========================
        logo = customtkinter.CTkImage(light_image=Image.open('images/logo.png'),
                                   dark_image=Image.open('images/logo.png'),
                                   size=(150,150)
                                   )
        cross = customtkinter.CTkImage(light_image=Image.open('images/close.png'),
                                   dark_image=Image.open('images/close.png'),
                                   size=(20,20)
                                   )
        homel = customtkinter.CTkImage(light_image=Image.open('images/home.png'),
                                   dark_image=Image.open('images/home.png'),
                                   size=(20,20)
                                   )
        detl = customtkinter.CTkImage(light_image=Image.open('images/details.png'),
                                   dark_image=Image.open('images/details.png'),
                                   size=(20,20)
                                   )
        sett = customtkinter.CTkImage(light_image=Image.open('images/settings.png'),
                                   dark_image=Image.open('images/settings.png'),
                                   size=(20,20)
                                   )
        self.tr = customtkinter.CTkLabel(self.frame_left,text="",width=190)
        self.tr.grid(row=0,column=0,pady=0,padx=0,sticky="nsew")

        self.close = customtkinter.CTkButton(self.frame_left,image=cross,text="",width=0,height=5,fg_color="#1b1b1b",
                                             hover=False,command=lambda: self.frame_left.destroy())
        self.close.grid(row=0,column=1,pady=0,padx=0,sticky="nsew")

        self.logo = customtkinter.CTkLabel(self.frame_left,image=logo,text="")
        self.logo.grid(row=1,column=0,pady=10,padx=5,sticky="nsew",columnspan=2)


        self.home_nav = customtkinter.CTkButton(self.frame_left,image=homel, text="Home",command=lambda: self.gui_home())
        self.home_nav.configure(font=("Roboto",16), fg_color="#363636", hover_color="gray5",anchor="center",width=200)
        self.home_nav.grid(row=2, column=0,pady=5,padx=10,sticky="nsew",columnspan=2)

        self.detailed = customtkinter.CTkButton(self.frame_left,image=detl, text="Details",command=lambda: self.gui_details())
        self.detailed.configure(font=("Roboto",16), fg_color="#363636", hover_color="gray5",anchor="center")
        self.detailed.grid(row=3, column=0,pady=5,padx=10,sticky="nsew",columnspan=2)

        self.settings_nav = customtkinter.CTkButton(self.frame_left,image=sett,text="Settings",command=lambda: self.gui_settings())
        self.settings_nav.configure(font=("Roboto",16), fg_color="#363636", hover_color="gray5",anchor="w")
        self.settings_nav.grid(row=4, column=0,pady=5,padx=10,sticky="nsew",columnspan=2)

    def gui_home(self):
        if self.active_frame != self.guiframes["home"]:
            try:
                eval(self.active_frame).destroy()
                self.frame_left.destroy()
            except :
                pass
            if self.active_frame == self.guiframes["details"]:
                self.gui_frame_right_home_settings()
            self.page_name.configure(text="Home")
            self.active_frame = self.guiframes["home"]

            self.home = customtkinter.CTkFrame(self.frame_center,width=570,fg_color="#101014")
            self.home.grid(row=1,column=0,padx=0,pady=0,sticky="nsew")
  
    def gui_details(self):
        # ===================Frame Center (Details) Components=========================
        self.frame_left.destroy()
        if self.active_frame != self.guiframes["details"]:
            self.details = customtkinter.CTkFrame(self.frame_center,width=570,fg_color="#1b1b1b",corner_radius=20)
            self.details.grid(row=1,column=0,padx=0,pady=0,sticky="nsew")

            self.get_total_times()
            for i,(app,time) in enumerate(reversed(self.total_time_per_app)):
                self.ta = customtkinter.CTkLabel(self.details,text=app,
                                                    font=customtkinter.CTkFont(family="Roboto", size=20,weight="normal"),
                                                    justify="left",anchor="w",width=410)
                self.ta.grid(row=i,column=0,padx=(15,0),pady=(9,8),columnspan=1)

                self.tm = customtkinter.CTkLabel(self.details,text=str(time),
                                                    font=customtkinter.CTkFont(family="Roboto", size=20,weight="normal"),
                                                    justify="left",anchor="w")
                self.tm.grid(row=i,column=1,padx=(15,0),pady=(9,8),columnspan=1)

                self.con = customtkinter.CTkButton(self.details,
                                    image=customtkinter.CTkImage(light_image=Image.open('images/continue.png'),
                                   dark_image=Image.open('images/continue.png'),size=(25,25)),
                                   text="",command=lambda app=app: self.gui_details_right_frame(app))
                self.con.configure(fg_color="#1b1b1b", hover_color="#1b1b1b",width=40)
                self.con.grid(row=i,column=2,padx=(15,0),pady=(9,8))

            self.gui_details_right_frame(app=self.total_time_per_app[len(self.total_time_per_app)-1][0])
            eval(self.active_frame).destroy()
            self.page_name.configure(text="Details")
            self.frcontainer.destroy()
            self.active_frame = self.guiframes["details"]

    def gui_details_right_frame(self,app):
        self.get_activities()
        self.det = customtkinter.CTkLabel(self.frame_right,text="Details",
                                              font=customtkinter.CTkFont(family="Roboto", size=27,weight="bold"),
                                              justify="left",anchor="w",wraplength=290)
        self.det.grid(row=0,column=0,padx=(16,19),pady=(16,0),sticky="nsew",columnspan=3)

        self.app_name = customtkinter.CTkLabel(self.frame_right,text=app,
                                              font=customtkinter.CTkFont(family="Roboto", size=12,weight="bold"),
                                              justify="left",anchor="w",wraplength=290)
        self.app_name.grid(row=1,column=0,padx=(16,19),pady=(4,0),sticky="nsew",columnspan=3)

        self.frcontainerd = customtkinter.CTkScrollableFrame(master=self.frame_right, width=300,height=400,fg_color="#1b1b1b")
        self.frcontainerd.grid(row=2, column=0,padx=(16,9),pady=(0,10),sticky="nsew")

        i=1
        for s in reversed(self.activities):
            if app in self.activities[s]:
                self.Date = customtkinter.CTkLabel(self.frcontainerd,text=s,
                                              font=customtkinter.CTkFont(family="Roboto", size=20,weight="bold"),
                                              justify="left",anchor="w")
                self.Date.grid(row=i,column=0,padx=2,pady=(17,5),sticky="nsew",columnspan=2)
                self.entry = customtkinter.CTkEntry(self.frcontainerd,width=95,fg_color="#1b1b1b",text_color="white")
                self.entry.grid(row=i+1,column=0)
                self.entry.insert(customtkinter.END,"Start Time")
                self.entry.configure(state="disabled")

                self.entry = customtkinter.CTkEntry(self.frcontainerd,width=95,fg_color="#1b1b1b",text_color="white")
                self.entry.grid(row=i+1,column=1)
                self.entry.insert(customtkinter.END,"End Time")
                self.entry.configure(state="disabled")

                self.entry = customtkinter.CTkEntry(self.frcontainerd,width=95,fg_color="#1b1b1b",text_color="white")
                self.entry.grid(row=i+1,column=2)
                self.entry.insert(customtkinter.END,"Duration")
                self.entry.configure(state="disabled")

                i=i+2
                for ts in self.activities[s][app]:
                    for j in range(3):
                        self.entry = customtkinter.CTkEntry(self.frcontainerd,width=95,fg_color="#1b1b1b",text_color="white")
                        self.entry.grid(row=i,column=j)
                        self.entry.insert(customtkinter.END,ts[j])
                        self.entry.configure(state="disabled")
                    i=i+1
                
    def gui_settings(self):
        self.frame_left.destroy()
        # ===================Frame Center (Settings) Components=========================
        if self.active_frame != self.guiframes["settings"]:
            self.settings = customtkinter.CTkFrame(self.frame_center,width=570,fg_color="#101014")
            self.settings.grid(row=1,column=0,padx=0,pady=0,sticky="nsew")

            self.general= customtkinter.CTkFrame(self.settings,width=570,height=165,fg_color="#1b1b1b",corner_radius=20)
            self.general.grid(row=0,column=0,pady=0,padx=0,sticky="nsew")
            self.general.grid_propagate(0)
            # ==================================================================================================================
            self.generalh = customtkinter.CTkLabel(self.general,text="General",
                                                font=customtkinter.CTkFont(family="Roboto", size=27,weight="normal"),
                                                justify="left",anchor="w",width=450)
            self.generalh.grid(row=0,column=0,padx=(15,0),pady=(17,0),columnspan=1)
            
            self.min_winl = customtkinter.CTkLabel(self.general,text="Minimise Window (Instead of closing the application)",
                                                font=customtkinter.CTkFont(family="Roboto", size=16,weight="normal"),
                                                justify="left",anchor="w",width=450)
            self.min_winl.grid(row=1,column=0,padx=(15,10),pady=(17,0))
            self.min_win =  customtkinter.CTkSwitch(self.general, text="", onvalue=True, offvalue=False,
                                                    command=lambda:self.settings_json_update("min_win"))
            self.min_win.grid(row=1,column=1,padx=(15,0),pady=(17,0))
            if self.settings_js["min_win"]:
                self.min_win.select()

            self.updatea = customtkinter.CTkLabel(self.general,text="Update",
                                                font=customtkinter.CTkFont(family="Roboto", size=16,weight="normal"),
                                                justify="left",anchor="w",width=450)
            self.updatea.grid(row=2,column=0,padx=(15,0),pady=(17,0))

            self.check = customtkinter.CTkButton(self.general, text="CHECK")
            self.check.configure(font=("Roboto",16), hover=False,anchor="center",width=50)
            self.check.grid(row=2, column=1,padx=(0,10),pady=(17,0))

            # ==================================================================================================================
            self.startup= customtkinter.CTkFrame(self.settings,width=570,height=165,fg_color="#1b1b1b",corner_radius=20)
            self.startup.grid(row=1,column=0,pady=(10,0),padx=0,sticky="nsew")
            self.startup.grid_propagate(0)
            
            self.startuph = customtkinter.CTkLabel(self.startup,text="Startup",
                                                font=customtkinter.CTkFont(family="Roboto", size=27,weight="normal"),
                                                justify="left",anchor="w",width=450)
            self.startuph.grid(row=0,column=0,padx=(15,0),pady=(17,0),columnspan=1)
            
            self.launchl = customtkinter.CTkLabel(self.startup,text="Launch on computer startup",
                                                font=customtkinter.CTkFont(family="Roboto", size=16,weight="normal"),
                                                justify="left",anchor="w",width=450)
            self.launchl.grid(row=1,column=0,padx=(15,10),pady=(17,0))

            self.launch =  customtkinter.CTkSwitch(self.startup, text="", onvalue=True, offvalue=False,
                                                    command=lambda:self.settings_json_update("launch_startup"))
            self.launch.grid(row=1,column=1,padx=(15,0),pady=(17,0))
            if self.settings_js["launch_startup"]:
                self.launch.select()

            self.startminl = customtkinter.CTkLabel(self.startup,text="Start minimised",
                                                font=customtkinter.CTkFont(family="Roboto", size=16,weight="normal"),
                                                justify="left",anchor="w",width=450)
            self.startminl.grid(row=2,column=0,padx=(15,10),pady=(17,0))

            self.startmin =  customtkinter.CTkSwitch(self.startup, text="", onvalue=True, offvalue=False,
                                                    command=lambda:self.settings_json_update("start_min"))
            self.startmin.grid(row=2,column=1,padx=(15,0),pady=(17,0))
            if self.settings_js["start_min"]:
                self.startmin.select()

            eval(self.active_frame).destroy()
            self.page_name.configure(text="Settings")
            if self.active_frame == self.guiframes["details"]:
                    self.gui_frame_right_home_settings()
            self.active_frame = self.guiframes["settings"]

    def gui_frame_right_home_settings(self):
        if self.active_frame == self.guiframes["details"]:
            self.det.destroy()
            self.frcontainerd.destroy()
        # ===================Frame Right Components=========================
        self.frcontainer = customtkinter.CTkFrame(master=self.frame_right,fg_color="#1b1b1b")
        self.frcontainer.grid(row=0, column=0,padx=17,pady=(17,0),sticky="nsew")

        self.heading = customtkinter.CTkLabel(self.frcontainer,text="Activity Tracking",
                                              font=customtkinter.CTkFont(family="Roboto", size=27,weight="bold"),
                                              justify="left",anchor="w")
        self.heading.grid(row=1,column=0,padx=2,sticky="nsew")

        self.date_g = customtkinter.CTkLabel(self.frcontainer,text=datetime.datetime.today().strftime("%A,%d %b"),font=("Roboto",13),anchor="w",justify="left")
        self.date_g.grid(row=2,column=0,padx=2,sticky="nsew")

        self.frame_week = customtkinter.CTkFrame(master=self.frcontainer,fg_color="#1b1b1b")
        self.frame_week.grid(row=3, column=0,padx=0,pady=5,sticky="nsew")

        self.frame_week_tot = customtkinter.CTkFrame(master=self.frcontainer,corner_radius=20,fg_color="#232323")
        self.frame_week_tot.grid(row=4, column=0,padx=0,pady=5,sticky="nsew")

        self.tm = customtkinter.CTkLabel(self.frame_week_tot,image=customtkinter.CTkImage(light_image=Image.open('images/tot-time.png'),
                                   dark_image=Image.open('images/tot-time.png'),
                                   size=(12,12)
                                   ),compound="left",
                                    text="   Total Time This Week",font=("Roboto",14),justify="left",anchor="w")
        self.tm.grid(row=0,column=0,padx=15,pady=5,columnspan=5,sticky="nsew")

        self.tot_time = customtkinter.CTkLabel(self.frame_week_tot,text="",height=10,
                                               font=customtkinter.CTkFont(family="Roboto", size=17,weight="bold"))
        self.tot_time.grid(row=1,column=0,padx=5,pady=5,columnspan=3,sticky="nsew")

        for i in range(1,8):
            if self.dates[i-1] == self.start_time:
                customtkinter.CTkLabel(self.frame_week,
                                    text=f"{self.dates[i-1].strftime('%a')}\n\n{self.dates[i-1].strftime('%d')}",
                                   font=("Roboto",15),anchor="center",justify="center",height=75,
                                   fg_color="#363636",corner_radius=10).grid(row=0,column=i-1,padx=4,pady=5,sticky="nsew")
            else:
                customtkinter.CTkLabel(self.frame_week,
                                    text=f"{self.dates[i-1].strftime('%a')}\n\n{self.dates[i-1].strftime('%d')}",
                                   font=("Roboto",15),anchor="center",justify="center",height=75,
                                   corner_radius=0).grid(row=0,column=i-1,padx=8,pady=5,sticky="nsew")
            customtkinter.CTkLabel(self.frame_week_tot,
                                text=f"{self.dates[i-1].strftime('%a')}",
                                font=("Roboto",13)).grid(row=3,column=i-1,padx=4,pady=5,sticky="nsew")
            
        self.slider0 = customtkinter.CTkProgressBar(self.frame_week_tot, orientation="vertical",height=70,
                                                    progress_color="white")
        self.slider0.grid(row=2, column=0,pady=5,padx=17,sticky="nsew")
        self.slider1 = customtkinter.CTkProgressBar(self.frame_week_tot, orientation="vertical",height=70,
                                                    progress_color="white")
        self.slider1.grid(row=2, column=1,pady=5,padx=17,sticky="nsew")
        self.slider2 = customtkinter.CTkProgressBar(self.frame_week_tot, orientation="vertical",height=70,
                                                    progress_color="white")
        self.slider2.grid(row=2, column=2,pady=5,padx=17,sticky="nsew")
        self.slider3 = customtkinter.CTkProgressBar(self.frame_week_tot, orientation="vertical",height=70,
                                                    progress_color="white")
        self.slider3.grid(row=2, column=3,pady=5,padx=17,sticky="nsew")
        self.slider4 = customtkinter.CTkProgressBar(self.frame_week_tot, orientation="vertical",height=70,
                                                    progress_color="white")
        self.slider4.grid(row=2, column=4,pady=5,padx=17,sticky="nsew")
        self.slider5 = customtkinter.CTkProgressBar(self.frame_week_tot, orientation="vertical",height=70,
                                                    progress_color="white")
        self.slider5.grid(row=2, column=5,pady=5,padx=17,sticky="nsew")
        self.slider6 = customtkinter.CTkProgressBar(self.frame_week_tot, orientation="vertical",height=70,
                                                    progress_color="white")
        self.slider6.grid(row=2, column=6,pady=5,padx=17,sticky="nsew")


        self.frame_week_all = customtkinter.CTkFrame(master=self.frcontainer,corner_radius=20,fg_color="#252525")
        self.frame_week_all.grid(row=5, column=0,padx=0,pady=5,sticky="nsew")    

        self.ta = customtkinter.CTkLabel(self.frame_week_all,image=customtkinter.CTkImage(light_image=Image.open('images/tot-time.png'),
                                   dark_image=Image.open('images/tot-time.png'),
                                   size=(12,12)
                                   ),compound="left",height=28,
                                    text="   All time usage",font=("Roboto",14),justify="left",anchor="w")
        self.ta.grid(row=0,column=0,padx=15,pady=10,columnspan=3,sticky="nsew")


        self.tot_time_all = customtkinter.CTkLabel(self.frame_week_all,text="",height=10,
                                               font=customtkinter.CTkFont(family="Roboto", size=17,weight="bold"))
        self.tot_time_all.grid(row=1,column=0,padx=5,pady=(0,22),columnspan=3,sticky="nsew")

        # next add the battery percentage if laptop or add the average time spent on an app 

        self.gui_time()

    def guiLoop(self):
        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("dark-blue")
        self.app = customtkinter.CTk(fg_color="#101014")
        self.app.geometry("1000x520")
        # https://dribbble.com/shots/19514541-Activity-Tracking-Dashboardcan take this as a example
        self.app.grid_columnconfigure((0,1,2), weight=1)
        self.app.grid_rowconfigure(0, weight=1)
        self.app.iconbitmap("images/logo.ico")
        self.app.title("App Meter")
        self.app.resizable(False,False)     

        # ===================Frame Center=========================
        self.frame_center = customtkinter.CTkScrollableFrame(master=self.app, width=420,height=520,fg_color="#101014")
        self.frame_center.configure(corner_radius=20,
                                    scrollbar_button_color=("white","#101014"),scrollbar_button_hover_color=("white","#101014"))
        self.frame_center.grid(row=0, column=0 ,padx=15,pady=15,columnspan=2,sticky="nsew")

        # ===================Frame Right=========================
        self.frame_right = customtkinter.CTkFrame(master=self.app, width=265,height=520,fg_color="#1b1b1b")
        self.frame_right.configure(corner_radius=20)
        self.frame_right.grid(row=0, column=2,padx=15,pady=15,sticky="nsew")
        self.frame_right.grid_propagate(0)

        # ===================Frame Center (All Frame) Components=========================

        self.navbar= customtkinter.CTkFrame(self.frame_center,width=570,height=53,fg_color="#1b1b1b",corner_radius=20)
        self.navbar.grid(row=0,column=0,pady=(0,10),padx=(0,0),sticky="nsew")
        self.navbar.pack_propagate(0)

        self.open = customtkinter.CTkButton(self.navbar,
                                    image=customtkinter.CTkImage(light_image=Image.open('images/open-menu.png'),
                                   dark_image=Image.open('images/open-menu.png'),size=(25,25)),
                                   text="",command=lambda: self.gui_create_sidebar())
        self.open.configure(fg_color="#1b1b1b", hover_color="gray5",width=40)
        self.open.pack(side="left",pady=10,padx=10)

        self.page_name = customtkinter.CTkLabel(self.navbar,text="Home",
                                              font=customtkinter.CTkFont(family="Roboto", size=20,weight="bold"))
        self.page_name.pack(side="left",pady=10,padx=17)

        self.pc_name = customtkinter.CTkLabel(self.navbar,text=os.environ['COMPUTERNAME'],
                                              font=customtkinter.CTkFont(family="Roboto", size=20,weight="bold"))
        self.pc_name.pack(side="right",pady=10,padx=17)

        self.gui_home()
        self.gui_frame_right_home_settings()
        

        self.gui_done = True
        if self.settings_js["min_win"]:
            self.app.protocol('WM_DELETE_WINDOW', lambda: self.window("hide"))
        if not self.settings_js["min_win"]:
            self.app.protocol('WM_DELETE_WINDOW', lambda: self.window("quit"))

        self.app.mainloop()
        # self.running = False


class Activity:
    def __init__(self,fname) -> None:
        self.fname = fname
        self.active_app = ""
        self.active_url = ""
        self.today_date = str(datetime.datetime.now()).split(" ")[0]
        self.start_time = datetime.datetime.now()
        # self.running=rnqueue

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
        self.unwanted = ["ONLINENT.EXE","SearchApp.exe","rundll32.exe","ShellExperienceHost.exe","python.exe"]
        # self.activity(queue)

    def update_json(self,key,end_time,start_time):
        time = str(end_time-start_time).split(".")[0]
        start_time =str(start_time).split(" ")[1]
        end_time =str(end_time).split(" ")[1]
        st = int(time.split(":")[2])
        if st > 3 and key not in self.unwanted and "." in key and ".tmp" not in key:
            if key in self.tracked_before:
                self.activities[self.today_date][key].insert(0,[start_time.split(".")[0],end_time.split(".")[0],time])
            elif key not in self.tracked_before:
                self.tracked_before.append(key)
                self.activities[self.today_date].update({key:[[start_time.split(".")[0],end_time.split(".")[0],time]]})
            
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
    
    def activity(self,queue):
        while queue.empty() or queue.get():
            try:
                pid,app_name = self.get_app_name()
                if app_name in self.browsernames:
                    url = self.get_url(pid,app_name)
                    if self.active_url == "":
                        self.active_url == url
                    elif self.active_app not in self.browsernames:
                        self.end_time = datetime.datetime.now()
                        self.update_json(self.active_app, self.end_time,self.start_time)
                        self.active_app = app_name
                        self.start_time = datetime.datetime.now()
                    elif self.active_url != url:
                        self.end_time = datetime.datetime.now()
                        self.update_json(self.active_url, self.end_time,self.start_time)
                        self.start_time = datetime.datetime.now()
                    self.active_url = url

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
                pass


def tkinter_app(running_queue,fname):
    app = GraphicalUserInterface(running_queue,fname)
    app.start()

def track(running_queue,fname):
    acti = Activity(fname)
    acti.activity(running_queue)

if __name__ == "__main__":
    s =str(datetime.datetime.now()).split(" ")[0]
    fname = "data/activities-"+s.split("-")[0] + "-" + s.split("-")[1]+".json"
    if not any(map(lambda x: x == fname, os.listdir("data/"))):
        jsonwr = open(fname,"w")
        json.dump({},jsonwr,indent=4)
        jsonwr.close()

    fname = "dev.json"

    running_queue = Queue()

    # Set the running state to True
    running_queue.put(True)

    tkinter_process = Process(target=tkinter_app, args=(running_queue,fname))
    # while_loop_process = Process(target=track, args=(running_queue,fname))

    tkinter_process.start()
    # while_loop_process.start()

    tkinter_process.join()
    # Set the running state to False to terminate the while loop
    running_queue.put(False)
    # while_loop_process.join()