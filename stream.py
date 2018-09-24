import threading
import subprocess
import time
import shlex

RASPISTREAMMD = ["raspivid"]

TIMETOWAITFORABORT = 5.0

#class for controlling the running and shutting down of raspivid
class RaspiStreamController(threading.Thread):
    
    def __init__(self, fps,width,height,timeout,port,access,demux):

        threading.Thread.__init__(self)
        
        #setup the raspivid cmd
    
        self.raspistreamcmd = RASPISTREAMMD
        
        self.raspivid = None

        #add file path, timeout and preview to options
        #cmd="raspivid -fps 16 -w 640 -h 480 -o - -t 0 | cvlc stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264"
        self.raspistreamcmd.append(" -fps ")
        self.raspistreamcmd.append(fps)
        
        self.raspistreamcmd.append(" -w ")
        self.raspistreamcmd.append(width)
        
        self.raspistreamcmd.append(" -h ")
        self.raspistreamcmd.append(height)
        
        
        self.raspistreamcmd.append(" -o 0 ")

        self.raspistreamcmd.append(" -t ")
        self.raspistreamcmd.append(timeout)
        
        self.raspistreamcmd.append(" | cvlc stream:///dev/stdin --sout '#standard{access=")
        self.raspistreamcmd.append(access)
        
        self.raspistreamcmd.append(",mux=ts,dst=:")
        self.raspistreamcmd.append(port)
        
        self.raspistreamcmd.append("}' :demux=")
        self.raspistreamcmd.append(demux)        
                
        
        #set state to not running
        self.running = False
    
    def grabSnapShot(self,filename):
        raspivid = subprocess.Popen("raspivid -fps 16 -w 640 -h 480 -o - -t 0 | cvlc stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
        
    def run(self):
        #run raspivid
        
        self.raspivid = subprocess.Popen("raspivid -fps 16 -w 640 -h 480 -o - -t 0 | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        
        #loop until its set to stopped or it stops
        self.running = True
        
        while(self.running and self.raspivid.poll() is None):
            
            print("Streaming...")
            time.sleep(TIMETOWAITFORABORT)
            
        
        self.running = False
    
        #kill raspivid if still running
        if self.raspivid.poll() == True: self.raspivid.kill()

    def stopController(self):
        self.running = False
        print("Stopping Stream!")
        if self.raspivid.poll() == True: self.raspivid.kill()