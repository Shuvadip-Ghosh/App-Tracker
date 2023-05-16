import datetime
import json
# start_time = datetime.datetime.now()
# dates = [start_time + datetime.timedelta(days=i) for i in range(0 - start_time.weekday(), 7 - start_time.weekday())]
# print(dates)

# if datetime.timedelta(seconds=10,hours=0,minutes=20) > datetime.timedelta(seconds=0,hours=0,minutes=19):
    # print("yes")

jsonobj = open("dev.json","r")
activities = json.load(jsonobj)
jsonobj.close()

# if str(dates[3]).split(" ")[0] in activities:
#     print("Yes")

app= "Code.exe"
t = datetime.timedelta(seconds=0,hours=0,minutes=0)
time_tot= datetime.timedelta(seconds=0,hours=0,minutes=0)
for s in activities:
    if app in activities[s]:
        for f in activities[s][app]:
            print(tuple(f))
            time_tot = time_tot+datetime.timedelta(hours=int(f[2].split(":")[0]),minutes=int(f[2].split(":")[1]),seconds=int(f[2].split(":")[2]))

print(time_tot)
