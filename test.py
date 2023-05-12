import datetime
import json
start_time = datetime.datetime.now()
dates = [start_time + datetime.timedelta(days=i) for i in range(0 - start_time.weekday(), 7 - start_time.weekday())]
print(dates)

# if "2023-05-12" == str(datetime.datetime(2023, 5, 12, 20, 54, 41, 295820)).split(" ")[0]:
#     print("yes")

# jsonobj = open("dev.json","r")
# activities = json.load(jsonobj)
# jsonobj.close()

# if str(dates[3]).split(" ")[0] in activities:
#     print("Yes")
# t = datetime.timedelta(seconds=0,hours=0,minutes=0)
# for s in activities:
#     time_tot= datetime.timedelta(seconds=0,hours=0,minutes=0)
#     for g in activities[s]:
#         for f in activities[s][g]:
#             time_tot = time_tot+datetime.timedelta(hours=int(f[2].split(":")[0]),minutes=int(f[2].split(":")[1]),seconds=int(f[2].split(":")[2]))
#     t= t+time_tot
#     print(time_tot)
# print(t)
