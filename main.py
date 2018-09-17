import os
import subprocess
import threading
import time
import RPi.GPIO as GPIO
from threading import Thread

import control
import config

#import pygame

RASPIVIDCMD = ["raspivid"]

TIMETOWAITFORABORT = 0.5

#class for controlling the running and shutting down of raspivid
class RaspiVidController(threading.Thread):
    
    def __init__(self, filePath, timeout, preview, otherOptions=None):

        threading.Thread.__init__(self)
        
        #setup the raspivid cmd
        self.raspividcmd = RASPIVIDCMD

        #add file path, timeout and preview to options
        self.raspividcmd.append("-o")
        self.raspividcmd.append(filePath)
        self.raspividcmd.append("-t")
        self.raspividcmd.append(str(0))
        if preview == False: self.raspividcmd.append("-n")

        #if there are other options, add them
        if otherOptions != None:
            self.raspividcmd = self.raspividcmd + otherOptions

        #set state to not running
        self.running = False
        
    def run(self):
        #run raspivid
        raspivid = subprocess.Popen(self.raspividcmd)
        
        #loop until its set to stopped or it stops
        self.running = True
        
        while(self.running and raspivid.poll() is None):
            time.sleep(TIMETOWAITFORABORT)
            
        
        self.running = False
    
        #kill raspivid if still running
        if raspivid.poll() == True: raspivid.kill()

    def stopController(self):
        self.running = False

def init_vid():
    global vidcontrol
    vidcontrol = RaspiVidController("/home/pi/test.h264", 10000, False, ["-fps", "25"])

def start_vid():
    global vidcontrol
    print ("Video Running!")    
    vidcontrol.start()

def stop_vid():
    global vidcontrol
    #stop the controller
    vidcontrol.stopController()
    #wait for the tread to finish if it hasn't already
    vidcontrol.join()

def start_stream():
    cmd="raspivid -fps 16 -w 640 -h 480 -o - -t 0 | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264raspivid -fps 30 -w 640 -h 480 -o - -t 99999 | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264"

    print("streaming start")
    
    STREAM  = subprocess.Popen(cmd,shell=True)

    while(STREAM.poll() is None):
        time.sleep(10)
 
   
    if STREAM.poll() == True:
        STREAM.kill()

def takeTake(type):
#iftype ="POSITIVE" whatever
    cmd = "raspistill -o file.jpg"
    # we need to do burst and change file storage location if its positive or negative
def start_control():
    ed = 1
    #test = CONTROL("ed","ed")


    gameInstance = control.rc_control("ed","ed")
    gameInstance.pair()

    while gameInstance.isPaired:
    
        gameInstance.processControllerInput()              

        if(gameInstance.inMenu):        
            gameInstance.processMenuInput()
        else:
            gameInstance.processMovement()        



        time.sleep(.1)    


#test program
if __name__ == '__main__':

   # init_vid()

    threads = []
try:
    #start_vid()
    #start the stream for the webcam
    t = Thread(target=start_stream)
    threads.append(t)
    t.start()
    
    p = Thread(target=start_control)
    threads.append(p)
    p.start()
    

    while True:
        print ("running...");
        time.sleep(5)


except KeyboardInterrupt:
    GPIO.cleanup();
    print ("Stopping raspivid controller")
    #stop_vid()
    print ("Done")
    STREAM.kill()
    t.stop()
