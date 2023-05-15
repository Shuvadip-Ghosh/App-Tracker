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

tm = {}
t = datetime.timedelta(seconds=0,hours=0,minutes=0)
for s in activities:
    for g in activities[s]:
        time_tot= datetime.timedelta(seconds=0,hours=0,minutes=0)
        for f in activities[s][g]:
            time_tot = time_tot+datetime.timedelta(hours=int(f[2].split(":")[0]),minutes=int(f[2].split(":")[1]),seconds=int(f[2].split(":")[2]))
        if g in tm:
            tm[g].append(time_tot)
        else:
            tm.update({g:[time_tot]})
for a in tm:
    tt= datetime.timedelta(seconds=0,hours=0,minutes=0)
    for ts in tm[a]:
        tt =tt+ts
    tm[a] = tt
tm = dict(sorted(tm.items(), key=lambda item: item[1]))
tm = list(tm.items())
print(tm)
