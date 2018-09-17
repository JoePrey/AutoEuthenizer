import cwiid 
import time 
import requests
import thread
import json
import time
import socket,struct
import fcntl
import RPi.GPIO as GPIO
import threading
from gps import *
from geopy.distance import vincenty
from collections import deque
import math
from subprocess import call
import web
import json
import math


urls = (
    '/', 'index',
    '/addLocation','addLocation',
    '/getLocation','getLocation',
    '/game','game'
)

web.clients = dict()
web.data = dict()

class RC_GAME:
    
    def __init__(self):
        print 'init'    
        
    def get_ip_address(ifname):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15]))[20:24])
    
class index:

    def GET(self):
        return "Hello, world!"

class addLocation:
    def GET(self):

        user_data = web.input()

        uid = user_data.uid
    
        print 'ADD LOCATION AS ' + uid
        
        loc = {'latitude':user_data.latitude,'longitude':user_data.longitude,'altitude':user_data.altitude,'speed':user_data.speed,'track':user_data.track,'sats':user_data.sats,'ts':user_data.ts}
                
        if(uid in web.data):
            web.data[uid].append(loc)
            print 'appending'
        else:
            web.data[uid] = deque([],20)
            print 'not found adding'
            
class getLocation:
    def GET(self):

        user_data = web.input()

        output = []

        evade = 0

        for elem in web.clients:
            print elem
            if(web.clients[elem] == 1):
                evade = elem


        for elem in web.data[evade]:
            output.append(elem)

        return json.dumps(output)
        
class game:

    def GET(self):

        user_data = web.input()
        command = user_data.command

        if(command == 'addplayer'):
            
            ip = user_data.ip

            if(ip not in web.data):
                print 'new Ip'
                web.data[ip] = deque([],20)
                playerID = len(web.clients) + 1         
                web.clients[ip] = playerID
                return playerID
                
            else: 
                print 'already a player' + ip
                return web.clients[ip]
        
        if(command=='newgame'):
            web.clients = dict()
            web.data = dict()

gpsd = None #seting the global variable

class GpsPoller(threading.Thread):
  
  def __init__(self):
    threading.Thread.__init__(self)    
    global gpsd
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    while gpsp.running:
        gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

gpsp = GpsPoller()
gpsp.start()


class RC_GAME:

    def __init__(self):
        self.DISTANCE_TARGET = 1
        self.playerID = 0
        self.url = "http://192.168.1.130:8080/"

        self.readLevel = 1
        self.IP = self.getIP('wlan0')
        self.playing = False
        self.isPaired = False
        self.wm = None

        self.left = False
        self.right = False
        self.forward = False
        self.back = False

        self.game = None
        self.enableBlueTooth = True

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        self.signalLight = 7 

        self.forwardPIN = 12
        self.backwardsPIN = 15
        self.leftPIN = 13
        self.rightPIN = 11

        GPIO.setup(self.forwardPIN,GPIO.OUT)
        GPIO.setup(self.backwardsPIN,GPIO.OUT)
        GPIO.setup(self.leftPIN,GPIO.OUT)
        GPIO.setup(self.rightPIN,GPIO.OUT)

        self.menuIndex = 1
        self.inMenu = False
        self.writeLevel = 1
        self.readLevel = 1

        self.captureWayPoint = False
        self.isChasing = False
    def pairSignal(self,threadName,delay):

        while not self.isPaired:            
            GPIO.setup(self.signalLight,True)
            time.sleep(.2)
            GPIO.setup(self.signalLight,False)
            time.sleep(.2)
    
    def recordingSignal(self,threadName,delay):
        
          while self.record:
            
            self.wm.led = 1
            time.sleep(.1)

            self.wm.led = 2
            time.sleep(.1)

            self.wm.led = 4
            time.sleep(.1)

            self.wm.led = 8
            time.sleep(.1) 

    def chase(self,lGPS,threadName,delay):

        cGPS =  self.getGPS()

        self.isChasing = True

        distance = vincenty((cGPS['latitude'],cGPS['longitude']),(lGPS['latitude'],lGPS['longitude'])).feet

        targetHeading =  self.getHeading(lGPS['track'])
        currentHeading = self.getHeading(cGPS['track'])
        
        turning = False
        turnDirection = "NONE"

        print 'Distance: ' + str(distance)
        print lGPS
        
        while (distance > self.DISTANCE_TARGET):
            
            self.forward = True
            self.back = False
            cGPS =  self.getGPS()

            distance = vincenty((cGPS['latitude'],cGPS['longitude']),(lGPS['latitude'],lGPS['longitude'])).feet

            nextHeading = self.getHeading(cGPS['track'])

            if(nextHeading == None):
                currentHeading = "N"
                print 'BAD HEADING'
            else:
                currentHeading = nextHeading
            
            degreesTo = lGPS['track'] - cGPS['track']                

            if(abs(degreesTo) > 10):                                                      
                if(abs(degreesTo) > 160):                    
                    self.right = True
                    self.left = False
                    turning = True
                    turnDirection = "Right"
                elif(abs(degreesTo) < 160):
                    self.left = True
                    self.right = False
                    turning = True
                    turnDirection = "Left"
            else:
                self.right = False
                self.left = False
                turning = False
                turnDirection = "NONE"

            if(distance < self.DISTANCE_TARGET):
                print 'ACHIEVED TARGET'
                self.isChasing = False
                break
            if(not self.isChasing):
                print 'STOP CHASING'
                break
            
            print 'Distance:' + str(distance) + ' | Turning: ' + str(turnDirection)  + ' | CurrentHeading: ' + str(currentHeading) + ' | HEADING TO: ' + str(targetHeading)

            time.sleep(delay)

        print 'stopped chase'

        self.forward = False
        self.back = False
        self.isChasing = False
    
    def showRecordingSignal(self):
        
        self.recordingSignal = True
        thread.start_new_thread(self.recordingSignal,("signalblink",self.writeLevel,))        

    def exitMenu(self):
        self.inMenu = False
        self.menuIndex = 1

    def processControllerInput(self):

        if(not self.isChasing):

            if(self.wm.state['buttons'] & cwiid.BTN_2):
                self.back = True
                self.forward = False
            else:
                self.back = False   

            if (self.wm.state['buttons'] & cwiid.BTN_1):
                self.forward = True
                self.back = False
            else:
                self.forward = False                        

            if (self.wm.state['buttons'] & cwiid.BTN_UP):
                self.left = True
                self.right = False
            else: 
                self.left = False        

            if (self.wm.state['buttons'] & cwiid.BTN_DOWN):
                self.right = True
                self.left = False
            else: 
                self.right = False            
        #else:
        #    print 'chasing'

        if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            if(self.inMenu):                           
                self.exitMenu()
            else:
                print 'enter menu'
                self.inMenu = True           

            time.sleep(1)

        if(self.wm.state['buttons'] & cwiid.BTN_A):                    
            self.wayPoint = self.getGPS()
            print self.wayPoint

        if(self.wm.state['buttons'] & cwiid.BTN_B):
            self.isChasing = False
            print 'stop chasing'

    def processMovement(self):
        
        GPIO.output(self.forwardPIN,self.forward)
    
        GPIO.output(self.backwardsPIN,self.back)
    
        GPIO.output(self.leftPIN,self.left)
    
        GPIO.output(self.rightPIN,self.right)

        if(not self.isChasing):
            if(self.back):
                print 'Backwards'
            if(self.forward):
                print 'forward'
            if(self.left):
                print 'left'
            if(self.right):
                print 'right'                                    

    def processMenuInput(self):

        if(self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            self.menuIndex +=1
        if(self.wm.state['buttons'] & cwiid.BTN_LEFT):
            self.menuIndex -=1            

        #MIN AND MAX MENU OPTIONS
        if (self.menuIndex > 4):
            self.menuIndex = 1
        
        if(self.menuIndex <= 0):
            self.menuIndex = 4
                
        if(self.menuIndex == 3):
            self.wm.led = 4

        if(self.menuIndex == 4 ):
            self.wm.led = 8

        self.wm.led = self.menuIndex

        if(self.menuIndex == 3):
            self.wm.led = 4
        if(self.menuIndex == 4):
            self.wm.led = 8    

        if(self.wm.state['buttons'] & cwiid.BTN_1):
            print 'hit button1'
            if(self.menuIndex == 1):
                print 'capturing WAY POINT'
                self.captureWayPoint = True
                self.exitMenu()

        if(self.wm.state['buttons'] & cwiid.BTN_2):
            if(self.menuIndex == 1):
                self.captureWayPoint = False
                print 'start chase'
                thread.start_new_thread(self.chase,(self.wayPoint,"signalblink",self.writeLevel,))  
                self.exitMenu()

    def pair(self):
        
        thread.start_new_thread(self.pairSignal,("signalblink",self.writeLevel,))

        if(self.enableBlueTooth):
    
            print 'Press 1+2 on your Wiimote now...' 
            
            attempts = 1

            while not self.wm:                        

                try:

                    self.wm = cwiid.Wiimote()

                except RuntimeError:

                    print "Error opening wiimote connection" 
                    print "attempt " + str(attempts) 

                attempts +=1             
            
            self.isPaired = True                        
            self.wm.led = 1
            self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC 
            print 'PAIRED'
            GPIO.setup(self.signalLight,True)

            time.sleep(3)
    
    def start(self):

        thread.start_new_thread(self.report,(self.playerID,self.writeLevel,))
        thread.start_new_thread(self.receive,(self.playerID,self.writeLevel,))        
    
    def getIP(self,ifname):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15]))[20:24])        
    
    def getHeadingBetweenPoints(self,lat1,long1,lat2,long2):

        startLat = math.radians(float(lat1))
        startLong = math.radians(float(long1))
        endLat = math.radians(float(lat2))
        endLong = math.radians(float(long2))

        dLong = endLong - startLong

        dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))
        
        if abs(dLong) > math.pi:
             if dLong > 0.0:
                 dLong = -(2.0 * math.pi - dLong)
             else:
                 dLong = (2.0 * math.pi + dLong)

        bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0

        return bearing

    def getHeading(self, degrees):
        
        bearings = ["NE", "E", "SE", "S", "SW", "W", "NW", "N"];

        index = degrees - 22.5;

        if (index < 0):
            index += 360;
        if math.isnan(index):
            return(None)

        index = int(index / 45);

        return(bearings[index]);

    def stop(self):

        GPIO.setup(self.signalLight,False)
        
        GPIO.output(self.forwardPIN,False)
    
        GPIO.output(self.backwardsPIN,False)
    
        GPIO.output(self.leftPIN,False)
    
        GPIO.output(self.rightPIN,False)        

    def getGPS(self):

        loc = { 
                'longitude': gpsd.fix.longitude,
                'latitude':gpsd.fix.latitude ,
                'altitude':gpsd.fix.altitude,
                'speed':gpsd.fix.speed,
                'track':gpsd.fix.track,
                'sats':len(gpsd.satellites),
                'ts':time.time()
                }        

        return loc

    def startNewGame(self):
        
        ip = self.getIP('wlan0')

        instance = self.url + "game?command=addplayer&ip=" + ip
        
        print 'addplayer uid =' + str(ip)

        response = requests.get(instance,data="")

        self.playerID = int(response.text)
        
        print 'PLAYER ' + str(self.playerID) + ' JOINED GAME'
        
        self.playing = True
        
        self.start()
         
    def receive(self,threadName,delay):

        while self.playing:

            instance = self.url + "getLocation"

            response = requests.get(instance,data="")
            

            d = json.loads(response.text)
            
            for elem in d:
                self.opponent.append(elem)                

            time.sleep(delay)
    
    def report(self,threadName,delay):        
      
        loc = self.getGPS()

        while self.playing:

            instance = self.url + "addLocation?uid=" + str(self.IP)  +                '&longitude=' +  str(gpsd.fix.longitude) + '&latitude=' + str(gpsd.fix.latitude) + '&altitude=' + str(gpsd.fix.altitude) + '&speed=' + str(gpsd.fix.speed) + '&track=' + str(gpsd.fix.track) + '&sats=' + str(len(gpsd.satellites)) + '&ts=' + str(time.time())

            response = requests.get(instance,data="")

            time.sleep(delay)
                
#try:

gameInstance = RC_GAME()
gameInstance.pair()

while gameInstance.isPaired:
    
    gameInstance.processControllerInput()              

    if(gameInstance.inMenu):        
        gameInstance.processMenuInput()
    else:
        gameInstance.processMovement()        




    time.sleep(.1)

#except Exception:
#    print 'except'
#    gameInstance.stop()
    
