var serverAddress = "http://localhost:8080";

//function to create a dynamic list of gpus
function showGpus(data){
    for (let i = 0; i < Object.keys(data.gpu).length; i++){
        $("#gpuData").append("<div id=\"gpu" + i + "\"></div>")
        $("#gpu"+ i).append("<div id=\"gpu" + i + "Name\">" + data.gpu[i].vendor + " " + data.gpu[i].product + "</div>")
    }
};

//function inserting data from the web server into the web interface
function exportData(data){
    $("#hostname").text(data.system.hostname);
    $("#kernelVersion").text(data.system.os + " " + data.system.kernelVersion);
    $("#architecture").text(data.system.architecture);
    $("#locale").text(data.system.locale);
    $("#cpuName").text(data.cpu.modelName);
    $("#cpuCores").text(data.cpu.cores);
    $("#cpuThreads").text(data.cpu.threads);
    $("#cpuBoostFreq").text(data.cpu.boostFreq + "MHz");
    $("#cpuCurrentFreq").text(data.cpu.currentFreq + "MHz");
    $("#cpuFreqBar").attr("value", data.cpu.usage)
    for (let i = 0; i < Object.keys(data.drives).length; i++){
        if (data.drives[i].mountpoint === null){
            $("#driveData").append("<div id=\"drive" + i + "\">" + data.drives[i].name + "</div>")
        }
        else{
            $("#driveData").append("<div id=\"drive" + i + "\">" + data.drives[i].name + "(" + data.drives[i].mountpoint.substring(data.drives[i].mountpoint.search(/(?<=\/)[^/]+$/gm)) + ")" + "</div>")
        }
        if (data.drives[i].removable == true){
            $("#drive" + i).append("<img src=\"icons/usb.svg\">")
        }
        if (data.drives[i].usage !== "None"){
            $("#drive" + i).append("<progress id=\"drive" + i +"Prog\" min=\"0\" max=\"100\" value=\"" + data.drives[i].usage + "\"></progress>")
        }
    }
    $("#cpuV").text(data.cpu.virtualization);
    $("#cpuNuma").text(data.cpu.numaNodes);
    $("#cpuVendor").text(data.cpu.vendorID);
    showGpus(data)
};

fetch(serverAddress + "/data")
    .then(response => response.json())
    .then(data => exportData(data))