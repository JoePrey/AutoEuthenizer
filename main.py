
import os
import sys
import subprocess
import threading
import time
import RPi.GPIO as GPIO
from threading import Thread
#import cwiid
import datetime

import control
import config
import stream
import utilities

gameInstance = None
streamcontrol = None
TIME_TO_TERM_RASPIVID = 10

CLEAN = False

def start_control():
    gameInstance = control.rc_control("ed","ed")
    gameInstance.pair()
    
    gameInstance.run()
    
def takepic(type):
    
    fname = "/home/pi/project/" + str(type) + "/" + str(datetime.date.today()) + str(datetime.datetime.now()) + ".jpg"
    fname = fname.replace(" ", "_")
    #md = "raspistill -o " + fname
    cmd = "raspistill -vf -o " + fname
    print(cmd)
    pic = subprocess.Popen(cmd,shell=True)

def CleanupOrphanProcesses(threadNames):
    start = time.time()
    oldThreads = 0
    elapsed_time = 0
    
    for t in threadNames:
        oldThreads+=utilities.killthreads(t,False)    
        
    
    while oldThreads > 0 and elapsed_time < TIME_TO_TERM_RASPIVID:
        #elapsed_time = time.time() - t        
        #utilities.clearConsole()
    
        print("Cleaning: " + str(oldThreads))
        
        for t in threadNames:
            oldThreads=utilities.killthreads(t,True)
            
        elapsed_time = time.time() - start
        
        time.sleep(1)
        
    if(oldThreads > 0):
        print("Gave up cleaning those threads recommend reboot...")
    else:
        print("No Threads to kill for: " + str(threadNames))
        
    time.sleep(1)
    
    elapsed_time = time.time() - start
    
        
menu = [['pic',takepic],['stream',stream]]
  

if __name__ == '__main__':

    threads = []

    start = time.time()


try:
    #start_vid()
    #start the stream for the webcam

    

    
    #t = Thread(targket=start_stream)
    #threads.append(t)
    #t.start()
    
    #p = Thread(target=start_control)
    #threads.append(p)
    #p.start()
    name = ""
    while True and name!="QUIT":
        utilities.clearConsole()
        print(menu)
        name = raw_input("Input Command::")
        

        if(str(name)=="pic"):
            takepic("positive")
        elif(str(name)=="clean"):
            CleanupOrphanProcesses(['raspistill','raspivid'])
        elif(str(name)=="reboot"):
            os.system("reboot")
        elif(str(name)=="stream"):
            if(streamcontrol):
                streamcontrol.stopController()
                streamcontrol.join()
            else:
                streamcontrol = stream.RaspiStreamController(16,640,480,0,"8090","http","h264")
                streamcontrol.start()
        
        time.sleep(3)
            
    print("quit")
    

except KeyboardInterrupt:
    GPIO.cleanup();
    
    streamcontrol.stopController()    
    streamcontrol.join()
    
    gameInstance.kill()
           
    quit()
