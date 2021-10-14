import subprocess as sp
import json
import re

#function converting lscpu json output to usable json output
def garbageToUsableJson(data, key):
    usableJson = {}
    for i in range(len(data[key])):
        usableJson[data[key][i-1]["field"]] = data[key][i-1]["data"]
    return usableJson

#function to get the systems locale (used to translate lscpu, ...)
def getLocale():
    return sp.getoutput("locale | grep LANG=").replace("LANG=","")[0:5]

#function converting lscpu from multiple languages into one(english) to make it more usable
def unifyLscpu(data, locale):
    if locale == "en_US":
        return {
            "architecture": data["Architecture:"],
            "cpuOpModes": data["CPU op-mode(s):"],
            "byteOrder": data["Byte Order:"],
            "addressSizes": data["Address sizes:"],
            "cpus": data["CPU(s):"],
            "onlineCpus": data["On-line CPU(s) list:"],
            "threadsPerCore": data["Thread(s) per core:"],
            "coresPerSocket": data["Core(s) per socket:"],
            "sockets": data["Socket(s):"],
            "numaNodes": data["NUMA node(s):"],
            "vendorId": data["Vendor ID:"],
            "cpuFamily": data["CPU family:"],
            "model": data["Model:"],
            "modelName": data["Model name:"],
            "stepping": data["Stepping:"],
            "frequencyBoost": data["Frequency boost:"],
            "cpuFreq": data["CPU MHz:"],
            "cpuMaxFreq": data["CPU max MHz:"],
            "cpuMinFreq": data["CPU min MHz:"],
            "bogoMips": data["BogoMIPS:"],
            "virtualization": data["Virtualization:"],
            "l1dCache": data["L1d cache:"],
            "l1iCache": data["L1i cache:"],
            "l2Cache": data["L2 cache:"],
            "l3Cache": data["L3 cache:"]
        }
    elif locale == "de_DE":
        return {
            "architecture": data["Architektur:"],
            "cpuOpModes": data["CPU Operationsmodus:"],
            "byteOrder": data["Byte-Reihenfolge:"],
            "addressSizes": data["Adressgrößen:"],
            "cpus": data["CPU(s):"],
            "onlineCpus": data["Liste der Online-CPU(s):"],
            "threadsPerCore": data["Thread(s) pro Kern:"],
            "coresPerSocket": data["Kern(e) pro Socket:"],
            "sockets": data["Sockel:"],
            "numaNodes": data["NUMA-Knoten:"],
            "vendorId": data["Anbieterkennung:"],
            "cpuFamily": data["Prozessorfamilie:"],
            "model": data["Modell:"],
            "modelName": data["Modellname:"],
            "stepping": data["Stepping:"],
            "cpuFreq": data["CPU MHz:"],
            "cpuMaxFreq": data["Maximale Taktfrequenz der CPU:"],
            "cpuMinFreq": data["Minimale Taktfrequenz der CPU:"],
            "bogoMips": data["BogoMIPS:"],
            "virtualization": data["Virtualisierung:"],
            "l1dCache": data["L1d Cache:"],
            "l1iCache": data["L1i Cache:"],
            "l2Cache": data["L2 Cache:"],
            "l3Cache": data["L3 Cache:"]
        }

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

def getData():
    #getting data for hostname, kernel Version, operating system, cpu and gpu
    hostName = sp.getoutput("uname -n")
    kernelRelease = sp.getoutput("uname -r")
    os = sp.getoutput("uname -o")
    cpuData = unifyLscpu(garbageToUsableJson(json.loads(sp.getoutput("lscpu --json")), "lscpu"), getLocale())
    cpuUsage = sp.getoutput("top -bn 2 -d 0.01 | grep '^%Cpu' | tail -n 1 | gawk '{print $2+$4+$6}'")
    gpuData = json.loads(sp.getoutput("lshw -json -C display 2>/dev/null"))
    drives = getDrivesAsDict(json.loads(sp.getoutput("lsblk -blOJ")))
    
    dictData = {
    "system": {
        "hostname": hostName,
        "os": os,
        "kernelVersion": kernelRelease,
        "architecture": cpuData["architecture"],
        "locale": getLocale()
    },
    "cpu": {
        "modelName": cpuData["modelName"],
        "cores": int(cpuData["coresPerSocket"]),
        "threads": int(cpuData["cpus"]),
        "threadsPerCore": int(cpuData["threadsPerCore"]),
        "baseFreq": round(float(cpuData["cpuMinFreq"].replace(",", "."))),
        "boostFreq": round(float(cpuData["cpuMaxFreq"].replace(",", "."))),
        "usage": int(cpuUsage),
        "currentFreq": round(float(cpuData["cpuFreq"].replace(",", "."))),
        "virtualization": cpuData["virtualization"],
        "numaNodes": int(cpuData["numaNodes"]),
        "vendorID": cpuData["vendorId"]
    },
    "gpu": gpuData,
    "drives": drives
    }
    jsonData = json.dumps(dictData)
    return jsonData