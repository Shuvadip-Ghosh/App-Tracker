from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId
from pywinauto.application import Application
import time

time.sleep(3)
window = GetForegroundWindow()
tid, pid = GetWindowThreadProcessId(window)

# chrome

# app = Application(backend="uia").connect(process=pid, time_out=10)
# dlg = app.top_window()
# url = dlg.child_window(title="Address and search bar", control_type="Edit").get_value()
# print(url)

# edge 

# app = Application(backend='uia').connect(process=pid, found_index=0)
# dlg = app.top_window()
# wrapper = dlg.child_window(title="App bar", control_type="ToolBar")
# url = wrapper.descendants(control_type='Edit')[0].get_value()
# print(url)