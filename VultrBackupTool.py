import requests,time,json,sys,datetime

def cll(): # clear last line
    sys.stdout.write("\033[F")

def vr(r): # validate response
    if r.status_code!=200:
        d=json.loads(r.text)
        print(f"error [{d['status']}]: {d['error']}")

def getdt():
    dt=datetime.datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# enter api token
token=input("Enter API Token: ")
headers={"Authorization":f"Bearer {token}"}
cll()
print("Enter API Token: "+"*"*(len(token)-4)+token[-4:])

# check account
print("Validating API Token... ",end='')
r=requests.get("https://api.vultr.com/v2/account",headers=headers)
vr(r)
print("\n")
cll()
d=json.loads(r.text)
print("API Token validated ✓")
print(f"Welcome {d['account']['name']} !\n")

# get instances
print("Listing instances... ",end='')
r=requests.get("https://api.vultr.com/v2/instances",headers=headers)
vr(r)
print("\n")
cll()
print("Instances: ")
d=json.loads(r.text)
instances=[]
for dd in d["instances"]:
    instances.append(dd['id'])
    print(f"{dd['label']} : {dd['id']}")

while 1:
    instance_id=input("Enter Instance ID of the instance to take automatic backup: ")
    if not instance_id in instances:
        print("Invalid Instant ID!")
    else:
        break

description=input("\nEnter Snapshot Description (You are recommended to add a '(Auto)' tag): ")

print("\nOK! The script will start running in 10 seconds... You can leave it running alone!\n")
time.sleep(10)

while 1:
    newid=""
    while 1:
        print("Creating snapshot... ",end='')
        # create snapshot
        r=requests.post("https://api.vultr.com/v2/snapshots",data=json.dumps({"instance_id":instance_id,"description":description}),headers=headers)
        if r.status_code!=201:
            d=json.loads(r.text)
            print(f"error [{d['status']}]: {d['error']}")
            print("Retrying after 30 seconds...")
            time.sleep(30)
            cll()
            continue
        else:
            print('\n')
            cll()
            d=json.loads(r.text)
            newid=d["snapshot"]["id"]
            print(f"Snapshot created (ID: {newid})")
            break

    # wait for complete
    print(f"Waiting for completion ({getdt()})...")
    while 1:
        cll()
        print(f"Waiting for completion ({getdt()})...",end='')
        r=requests.get(f"https://api.vultr.com/v2/snapshots/{newid}",headers=headers)
        vr(r)
        print('\n')
        d=json.loads(r.text)
        if d["snapshot"]["status"]=="complete":
            cll()
            print(f"Snapshot creation completed at {getdt()} !\n")
            print("Listing snapshots...")
            # delete old snapshot
            r=requests.get("https://api.vultr.com/v2/snapshots",headers=headers)
            d=json.loads(r.text)
            vr(r)
            print('\n')
            cll()
            print("Snapshots: ")
            for dd in d["snapshots"]:
                print(f"{dd['description']} : {dd['id']}", end='')
                if dd["description"]==description and dd["id"]!=newid:
                    print("(just deleted)")
                    requests.delete(f"https://api.vultr.com/v2/snapshots/{dd['id']}",headers=headers)
                else:
                    print("\n")
            cll()
            print("Old snapshot(s) deleted!\n")
            break

        time.sleep(60) # check again each minute
        
    print("Sleeping...")
    time.sleep(43200) # take snapshot each 12 hours
    cll()