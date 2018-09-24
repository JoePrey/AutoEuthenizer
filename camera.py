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

