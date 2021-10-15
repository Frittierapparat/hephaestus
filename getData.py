import subprocess as sp
import json
import re

#function to get the systems locale (used to translate lscpu, ...)
def getLocale():
    return sp.getoutput("locale | grep LANG=").replace("LANG=","")[0:5]

#function removing loop devices from lsblk output and returning it
#in a more usable format
def getDrivesAsDict(data):
    dict = {}
    data = data["blockdevices"]
    for i in range(len(data)):
        if re.search("loop[0-9]*", data[i]["name"]):
            pass
        elif not(re.search("raid[0-9]*", data[i]["type"]) or re.search("disk", data[i]["type"])):
            dict[len(dict)] = {
                "name": data[i]["name"],
                "removable": data[i]["rm"],
                "size": data[i]["size"],
                "usage": str(data[i]["fsuse%"]).replace("%", ""),
                "read-only": data[i]["ro"],
                "type": data[i]["type"],
                "mountpoint": data[i]["mountpoint"]
            }
    return dict

def getCpuData(data):
    return {
        "modelName": re.search("(?<=model name\t: ).*", data).group(),
        "cores": int(re.search("(?<=cpu cores\t: ).*", data).group()),
        "threads": int(re.search("(?<=siblings\t: ).*", data).group()),
        "threadsPerCore": int(re.search("(?<=siblings\t: ).*", data).group()) / int(re.search("(?<=cpu cores\t: ).*", data).group()),
        "baseFreq": int(sp.getoutput("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq")) / 1000,
        "boostFreq": int(sp.getoutput("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq")) / 1000,
        "currentFreq": int(sp.getoutput("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")) / 1000,
        "usage": int(sp.getoutput("top -bn 2 -d 0.01 | grep '^%Cpu' | tail -n 1 | gawk '{print $2+$4+$6}'")),
        "virtualization": re.search("vmx|svm", data).group(),
        "numaNodes": int(sp.getoutput("find /sys/devices/system/node/node*/ -maxdepth 0").count("\n")) +1,
        "vendorId": re.search("(?<=vendor_id\t: ).*", data).group()
    }

def getData():
    #getting data for hostname, kernel Version, operating system, cpu and gpu
    hostName = sp.getoutput("uname -n")
    kernelRelease = sp.getoutput("uname -r")
    os = sp.getoutput("uname -o")
    architecture = sp.getoutput("uname -m")
    cpuData = getCpuData(sp.getoutput("cat /proc/cpuinfo"))
    gpuData = json.loads(sp.getoutput("lshw -json -C display 2>/dev/null"))
    drives = getDrivesAsDict(json.loads(sp.getoutput("lsblk -blOJ")))
    
    dictData = {
    "system": {
        "hostname": hostName,
        "os": os,
        "kernelVersion": kernelRelease,
        "architecture": architecture,
        "locale": getLocale()
    },
    "cpu": {
        "modelName": cpuData["modelName"],
        "cores": int(cpuData["cores"]),
        "threads": int(cpuData["threads"]),
        "threadsPerCore": int(cpuData["threadsPerCore"]),
        "baseFreq": (cpuData["baseFreq"]),
        "boostFreq": cpuData["boostFreq"],
        "usage": cpuData["usage"],
        "currentFreq": round(float(cpuData["currentFreq"])),
        "virtualization": cpuData["virtualization"],
        "numaNodes": int(cpuData["numaNodes"]),
        "vendorID": cpuData["vendorId"]
    },
    "gpu": gpuData,
    "drives": drives
    }
    jsonData = json.dumps(dictData)
    return jsonData