import time
from mojo import context
from precis import precis

log = context.log
dvMuse = context.devices.get("idevice")

def handeleOnlineEvent(event):
    global dvTP, timeline, dvRoomSensor, dvPrivacyGlass, dvBluRayIR, dvContemporarySTB, dvCamera, dvDisplay, devAudioArchitect, dvPrecis
    
    # User Interfaces
    dvTP = context.devices.get("AMX-10003")

    # timeline
    timeline = context.services.get("timeline")

    # Hardware Ports
    dvRoomSensor = dvMuse.io[0] # use 3 for testing
    dvPrivacyGlass = dvMuse.relay[0]
    dvBluRayIR = dvMuse.ir[0]

    # Serial Devices
    dvContemporarySTB = dvMuse.serial[0]

    # Module
    dvCamera = context.devices.get("dvCamera")
    dvDisplay = context.devices.get("dvSamsungQB75R")
    devAudioArchitect = context.devices.get("SoundwebLondonBLU-50-2")

    # IP Control Devices
    dvPrecis = precis("10.35.88.142", 23)

    # inits
    if dvDisplay:
        dvDisplay.module.setInstanceProperty("IP_Address","10.35.88.140")
        dvDisplay.module.setInstanceProperty("Port","1515")
        dvDisplay.module.setInstanceProperty("Poll_Time","10000")
        # dvDisplay.module.debugState.value = 4
        dvDisplay.module.reinitialize()
    if dvCamera:
        # dvMuse.serial[2].setCommParams("9600",8,1,"NONE","232")
        dvCamera.camera[0].zoomSpeed.value = 16
        dvCamera.camera[0].panSpeed.value = 16
        dvCamera.camera[0].tiltSpeed.value = 16
    # if dvContemporarySTB:
    #     dvMuse.serial[0].setCommParams("9600",8,1,"NONE","232")
    if dvPrecis:
        dvPrecis.setTP(dvTP)
        dvPrecis.connect()
    if dvBluRayIR:
        dvBluRayIR.setOnTime(100)
        
    # config
    tp = {
        "port/1/level/2":	handleVolLevel,
        "port/1/button/3":	handlePrivacyGlassToggle,
        "port/2/button/1":	handleDVD,
        "port/2/button/2":	handleLaptop1,
        "port/2/button/3":	handleTunner,
        "port/2/button/4":	handleLaptop2,
        "port/2/button/5":	handleSystemOff,
        "port/3/button/1":	handleBluRayIR,
        "port/3/button/3":	handleBluRayIR,
        "port/3/button/2":	handleBluRayIR,
        "port/3/button/4":	handleBluRayIR,
        "port/3/button/5":	handleBluRayIR,
        "port/3/button/6":	handleBluRayIR,
        "port/3/button/7":	handleBluRayIR,
        "port/3/button/44":	handleBluRayIR,
        "port/3/button/45":	handleBluRayIR,
        "port/3/button/46":	handleBluRayIR,
        "port/3/button/47":	handleBluRayIR,
        "port/3/button/48":	handleBluRayIR,
        "port/3/button/49":	handleBluRayIR,
        "port/3/button/50":	handleBluRayIR,
        "port/4/button/10":	handleSTBKey,
        "port/4/button/11":	handleSTBKey,
        "port/4/button/12":	handleSTBKey,
        "port/4/button/13":	handleSTBKey,
        "port/4/button/14":	handleSTBKey,
        "port/4/button/15":	handleSTBKey,
        "port/4/button/16":	handleSTBKey,
        "port/4/button/17":	handleSTBKey,
        "port/4/button/18":	handleSTBKey,
        "port/4/button/19":	handleSTBKey,
        "port/4/button/21":	handleSTBKey,
        "port/4/button/22":	handleSTBKey,
        "port/4/button/23":	handleSTBKey,
        "port/4/button/44":	handleSTBKey,
        "port/4/button/45":	handleSTBKey,
        "port/4/button/46":	handleSTBKey,
        "port/4/button/47":	handleSTBKey,
        "port/4/button/48":	handleSTBKey,
        "port/4/button/49":	handleSTBKey,
        "port/4/button/50":	handleSTBKey,
        "port/4/button/90":	handleSTBKey,
        "port/4/button/101":handleSTBKey,
        "port/4/button/105":handleSTBKey,
        "port/4/button/201":handleSTBChannel,
        "port/4/button/202":handleSTBChannel,
        "port/4/button/203":handleSTBChannel,
        "port/4/button/204":handleSTBChannel,
        "port/4/button/205":handleSTBChannel,
        "port/5/button/24":	handleVolUp,
        "port/5/button/25":	handleVolDown,
        "port/5/button/26":	handleSpeakerMute,
        "port/5/button/100":handleMicMute,
        "port/6/button/21":	handleCameraPreset1,
        "port/6/button/22":	handleCameraPreset2,
        "port/6/button/45":	handleCameraUp,
        "port/6/button/46":	handleCameraDown,
        "port/6/button/47":	handleCameraLeft,
        "port/6/button/48":	handleCameraRight,
        "port/6/button/116":handleCameraZoomIn,
        "port/6/button/117":handleCameraZoomOut,
    }

    # log.info(">>>>>>dvTP " + str(dvTP.__dict__))

    for key, action in tp.items():
        if action:
            isButton = (key.split('/')[2] == "button")
            isLevel = (key.split('/')[2] == "level")
            port = int(key.split('/')[1])
            id = int(key.split('/')[3])

            if isButton:
                log.info(f"Adding watch: button: {id}")
                dvTP.port[port].button[id].watch(action)
            if isLevel:
                log.info(f"Adding watch: level: {id}")
                dvTP.port[port].level[id].watch(action)

    # listerns
    timeline.expired.listen(listenTimerExpiry)
    dvRoomSensor.digitalInput.watch(listenRoomSensor)
    dvPrivacyGlass.state.watch(listenPrivacyGlass)
    dvCamera.camera[0].preset.watch(listenCameraPreset)
    devAudioArchitect.Audio.NodeRed_Output_Gain.Gain.watch(listenVolLevel)
    devAudioArchitect.Audio["Main Volume"]["Override Mute"].watch(listenSpeakerMute)
    devAudioArchitect.Audio["Mic Gain"].Mute.watch(listenMicMute)
    dvContemporarySTB.receive.listen(handleSTBResponse)

    log.info("END")


########################################################
# Suppoting Functions
########################################################

def setMonitorState(state):
    log.info(f"setMonitorState: state:{state}")
    if state:
        if (dvDisplay.lamp[0].power.value != "ON"):
            dvDisplay.lamp[0].power.value = "ON"
            time.sleep(10)
        if (dvDisplay.sourceSelect[0].inputSelect.value != "HDMI-HDMI 1"):
            dvDisplay.sourceSelect[0].inputSelect.value = "HDMI-HDMI 1"
    else:
        dvDisplay.lamp[0].power.value = "OFF"
        dvPrecis.switch(0)


def handlePrivacyGlassToggle(e):
    log.info(f"handlePrivacyGlassToggle: id:{e.id} value:{e.value}")
    if(e.value):
        dvPrivacyGlass.state.value = not dvPrivacyGlass.state.value


def handleDVD(e):
    log.info(f"handleDVD: id:{e.id}")
    dvTP.port[1].send_command("^PGE-Main")
    dvTP.port[1].send_command("^PPN-[LPS]DVD")
    setMonitorState(True)
    dvBluRayIR.clearAndSendIr(9)
    dvPrecis.switch(3)


def handleLaptop1(e):
    log.info(f"handleLaptop1: id:{e.id}")
    dvTP.port[1].send_command("^PGE-Main")
    dvTP.port[1].send_command("^PPN-[LPS]Laptop1")
    setMonitorState(True)
    dvPrecis.switch(1)


def handleLaptop2(e):
    log.info(f"handleLaptop2: id:{e.id}")
    dvTP.port[1].send_command("^PGE-Main")
    dvTP.port[1].send_command("^PPN-[LPS]Laptop2")
    setMonitorState(True)
    dvPrecis.switch(2)


def handleTunner(e):
    log.info(f"handleTunner: id:{e.id}")
    dvTP.port[1].send_command("^PGE-Main")
    dvTP.port[1].send_command("^PPN-[LPS]Tuner")
    setMonitorState(True)
    dvContemporarySTB.send(">19\r")
    dvPrecis.switch(4)


def handleSystemOff(e):
    log.info(f"handleSystemOff: id:{e.id}")
    if(e.value):
        log.info(f"handleSystemOff: ON")
        dvTP.port[1].send_command("^PPX")
        dvTP.port[1].send_command("^PGE-Logo")
        setMonitorState(False)


def handleBluRayIR(e):
    log.info(f"handleBluRayIR: id:{e.id}")
    key = {
        1:	1,	# play
        2:	2,	# stop
        3:	3,	# pause
        4:	4,	# ffwd
        5:	5,	# rrwd
        6:	6,	# sfwd
        7:	7,	# srev
        44:	44,	# menu
        45:	45,	# up
        46:	46,	# down
        47:	47,	# left
        48:	48,	# right
        49:	49,	# select
        50:	50,	# exit
    }
    keyStr = key.get(int(e.id), None)
    if keyStr and e.value:
        log.info(f"sending dvBluRayIR >> {keyStr}")
        dvBluRayIR.clearAndSendIr(keyStr)


def handleSTBKey(e):
    log.info(f"handleSTBKey: id:{e.id}")
    key = {
        10: "KK=10",	# digit_0
        11: "KK=11",	# digit_1
        12: "KK=12",	# digit_2
        13: "KK=13",	# digit_3
        14: "KK=14",	# digit_4
        15: "KK=15",	# digit_5
        16: "KK=16",	# DIGIT_6
        17: "KK=17",	# DIGIT_7
        18: "KK=18",	# DIGIT_8
        19: "KK=19",	# DIGIT_9
        21: "KK=110",	# enter # same as select
        22: "KK=22",	# channel+
        23: "KK=23",	# channel-
        44: "KK=105",	# menu
        45: "KK=108",	# up
        46: "KK=109",	# down
        47: "KK=107",	# left
        48: "KK=106",	# right
        49: "KK=110",	# select
        50: "KK=111",	# exit
        90: "KK=99",    # dash
        101:"KK=100",   # info
        105:"KK=63",    # guide
    }
    keyStr = key.get(int(e.id), None)
    if keyStr and e.value:
        log.info(f"sending dvContemporarySTB >> {keyStr}")
        dvContemporarySTB.send(">1" + keyStr + "\r")


def handleSTBChannel(e):
    log.info(f"handleSTBChannel: id:{e.id}")
    key = {
        201: "TC=122.1", # CNN
        202: "TC=123.1", # Fox News
        203: "TC=124.1", # MSNBC
        204: "TC=125.1", # Bloomberg
        205: "TC=126.1", # Weather
    }
    keyStr = key.get(int(e.id), None)
    if keyStr and e.value:
        log.info(f"sending dvContemporarySTB >> {keyStr}")
        dvContemporarySTB.send(">1" + keyStr + "\r")


def handleVolUp(e):
    log.info(f"handleVolUp: id:{e.id}")
    if e.value:
        devAudioArchitect.Audio.NodeRed_Output_Gain["Bump Up"].value = "On"
    else:
        devAudioArchitect.Audio.NodeRed_Output_Gain["Bump Up"].value = "Off"


def handleVolDown(e):
    log.info(f"handleVolDown: id:{e.id}")
    if e.value:
        devAudioArchitect.Audio.NodeRed_Output_Gain["Bump Down"].value = "On"
    else:
        devAudioArchitect.Audio.NodeRed_Output_Gain["Bump Down"].value = "Off"


def handleSpeakerMute(e):
    log.info(f"handleSpeakerMute: id:{e.id}")
    if e.value:
        state = devAudioArchitect.Audio["Main Volume"]["Override Mute"].value
        if state == "Unmuted":
            devAudioArchitect.Audio["Main Volume"]["Override Mute"].value = "Muted"
        elif state == "Muted":
            devAudioArchitect.Audio["Main Volume"]["Override Mute"].value = "Unmuted"


def handleMicMute(e):
    log.info(f"handleMicMute: id:{e.id}")
    if e.value:
        state = devAudioArchitect.Audio["Mic Gain"].Mute.value
        if state == "Unmuted":
            devAudioArchitect.Audio["Mic Gain"].Mute.value = "Muted"
        elif state == "Muted":
            devAudioArchitect.Audio["Mic Gain"].Mute.value = "Unmuted"


def handleVolLevel(e):
    log.info(f"handleVolLevel: id:{e.id} value:{e.value}")
    # Note: this is only for display, no action needed.
    # minDevVal = -80
    # maxDevVal = 10
    # tpVal = e.value

    # devVal = int((tpVal*(maxDevVal-minDevVal)/255) + minDevVal)
    # log.info(f"handleVolLevel: devVal{devVal}")
    # devAudioArchitect.Audio.NodeRed_Output_Gain.Gain.value = devVal


def handleCameraPreset1(e):
    log.info(f"handleCameraPreset1: id:{e.id}")
    if e.value:
        dvCamera.camera[0].preset.value = 1


def handleCameraPreset2(e):
    log.info(f"handleCameraPreset2: id:{e.id}")
    if e.value:
        dvCamera.camera[0].preset.value = 2


def handleCameraUp(e):
    log.info(f"handleCameraUp: id:{e.id}")
    if e.value:
        dvCamera.camera[0].tiltRamp.value = "UP"
    else:
        dvCamera.camera[0].tiltRamp.value = "STOP"


def handleCameraDown(e):
    log.info(f"handleCameraDown: id:{e.id}")
    if e.value:
        dvCamera.camera[0].tiltRamp.value = "DOWN"
    else:
        dvCamera.camera[0].tiltRamp.value = "STOP"


def handleCameraLeft(e):
    log.info(f"handleCameraLeft: id:{e.id}")
    if e.value:
        dvCamera.camera[0].panRamp.value = "LEFT"
    else:
        dvCamera.camera[0].panRamp.value = "STOP"


def handleCameraRight(e):
    log.info(f"handleCameraRight: id:{e.id}")
    if e.value:
        dvCamera.camera[0].panRamp.value = "RIGHT"
    else:
        dvCamera.camera[0].panRamp.value = "STOP"


def handleCameraZoomIn(e):
    log.info(f"handleCameraZoomIn: id:{e.id}")
    if e.value:
        dvCamera.camera[0].zoomRamp.value = "IN"
    else:
        dvCamera.camera[0].zoomRamp.value = "STOP"


def handleCameraZoomOut(e):
    log.info(f"handleCameraZoomOut: id:{e.id}")
    if e.value:
        dvCamera.camera[0].zoomRamp.value = "OUT"
    else:
        dvCamera.camera[0].zoomRamp.value = "STOP"


def listenTimerExpiry(e):
    log.info(f"listenTimerExpiry: id:{e.id}")
    setMonitorState(False)
    timeline.stop()


def listenRoomSensor(e):
    log.info(f"listenRoomSensor: id:{e.id}")
    if e.value: #Room Occupied
        timeline.stop()
        setMonitorState(False)
    else:
        timeline.start([10000])


def listenCameraPreset(e):
    log.info(f"listenCameraPreset: id:{e.id} value:{e.newValue}")
    dvTP.port[6].channel[21].value = (e.newValue == 1)
    dvTP.port[6].channel[22].value = (e.newValue == 2)


def listenPrivacyGlass(e):
    log.info(f"listenPrivacyGlass: id:{e.id} value:{e.newValue}")
    dvTP.port[1].channel[3].value = e.newValue


def listenVolLevel(e):
    log.info(f"listenVolLevel: id:{e.id} value:{e.newValue}")
    minDevVal = -80
    maxDevVal = 10
    devVal = e.newValue

    tpVal = int(255*(devVal -minDevVal)/(maxDevVal-minDevVal))
    log.info(f"listenVol: tpVal{tpVal}")
    dvTP.port[1].level[2].value = tpVal


def listenSpeakerMute(e):
    log.info(f"listenSpeakerMute: id:{e.id} value:{e.newValue}")
    state = e.newValue
    if state == "Unmuted":
        dvTP.port[5].channel[26].value = False
    elif state == "Muted":
        dvTP.port[5].channel[26].value = True

    
def listenMicMute(e):
    log.info(f"listenMicMute: id:{e.id} value:{e.newValue}")
    state = e.newValue
    if state == "Unmuted":
        dvTP.port[5].channel[100].value = False
    elif state == "Muted":
        dvTP.port[5].channel[100].value = True


def handleSTBResponse(e):
    global majorChannel, minorChannel
    data = e.arguments.get("data").decode("utf-8")
    # log.info(f"handleSTBResponse: data:{data}")

    try:
        majorChannel
        minorChannel
    except NameError:
        majorChannel = ""
        minorChannel = ""

    if("1TU" in data):
        if majorChannel != data[4:7]:
            majorChannel = data[4:7]
            dvTP.port[1].send_command("^TXT-400,0," + majorChannel)
        
        if minorChannel != data[11:14]:
            minorChannel = data[11:14]


#################################
# MAIN
#################################
dvMuse.online(handeleOnlineEvent)

