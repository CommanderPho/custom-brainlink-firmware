import pyvjoy
import math
from gamecube import *
import time

DEBUG = True
GC_BUTTONS = ("a", "b", "x", "y", "z", "start", "l", "r")

def toVJoystick(joy, state, buttons=GC_BUTTONS):
    joy.data.lButtons = sum(1<<i for i in range(len(buttons)) if getattr(state, buttons[i]))
    joy.data.wAxisX = state.joyX-128
    joy.data.wAxisY = 128-state.joyY
    joy.data.wAxisZRot = state.cX
    joy.data.wAxisYRot = state.cY
    joy.data.wSlider = 255-state.shoulderRight
    joy.data.wDial = 255-state.shoulderLeft
    joy.update()
    
    rid = joy.rID
    
    vector = [0,0]
    if state.dUp:
        vector[1] += 1
    elif state.dRight:
        vector[0] += 1
    elif state.dDown:
        vector[1] -= 1
    elif state.dLeft:
        vector[0] -= 1
        
    if vector[0] == 0 and vector[1] == 0:
        pov1 = -1
    else:
        pov1 = (-9000+(100*int(math.floor(0.5+180/math.pi * math.atan2(vector[1],-vector[0]))))) % 36000
        
    joy._sdk.SetContPov(pov1,rid,1)
    
    pov2 = -1
    px = state.cX - 128
    py = state.cY - 128
    if px*px + py*py >= 10*10:
        pov2 = (-9000+int(math.floor(0.5+100*180/math.pi * math.atan2(py,-px)))) % 36000
        
    joy._sdk.SetContPov(pov2,rid,2)
    
if __name__ == '__main__':
    import sys
    import serial
    import os
    import atexit
    
    def err(message):
        if DEBUG: print(message)

    port = "com3"    
    maps = {}
    delay = 5

    for item in sys.argv[1:]:
        if item in maps:
            map = maps[item]
        else:
            try:
                delay = int(item)
            except:
                port = item
                print (port)
        
    print("Connecting to serial")
    ser = serial.Serial(port, baudrate=115200, timeout=0.2)

    def disable():
        print("Exiting tovjoystick")
        ser.write(b'*#0')
        time.sleep(0.5)
        ser.reset_input_buffer()
        ser.close()
        os.system(r'"c:\Program Files\vJoy\x64\vJoyConfig" enable off')
    
    print("Enabling vjoystick")
    os.system(r'"c:\Program Files\vJoy\x64\vJoyConfig" 2 -f -a X Y RY RZ Sl0 Sl1 -b 16 -p 2')
    os.system(r'"c:\Program Files\vJoy\x64\vJoyConfig" enable on')
    atexit.register(disable)
    
    print("Running")

    joy = pyvjoy.VJoyDevice(2)
    processGameCubeController(ser, delay, lambda s0,s1: toVJoystick(joy, s1))