import RPi.GPIO as GPIO
import config
import utilities
from threading import Thread
import cwiid 

util = utilities.utils()


class rc_control:
    
    def __init__(self,name,author):
    
        self.name = name
        self.author = author
        
        #self.IP = util.get_ip_address('wlan0')
        self.forwardPIN = 12
        self.enableBlueTooth = True
        self.backwardsPIN = 15
        self.leftPIN = 13
        self.rightPIN = 11
        self.signalLight = 7        
        
        self.isPaired = False
        self.wm = None

        self.left = False
        self.right = False
        self.forward = False
        self.back = False

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
            
  
    def pairSignal(self,threadName,delay):

        while not self.isPaired:            
            GPIO.setup(self.signalLight,True)
            time.sleep(.2)
            GPIO.setup(self.signalLight,False)
            time.sleep(.2) 
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
                print ('enter menu')
                self.inMenu = True           

            time.sleep(1)

        if(self.wm.state['buttons'] & cwiid.BTN_A):                    
            self.wayPoint = self.getGPS()
            #print self.wayPoint

        if(self.wm.state['buttons'] & cwiid.BTN_B):
            self.isChasing = False
            print ('stop chasing')

    def processMovement(self):
        
        GPIO.output(self.forwardPIN,self.forward)
    
        GPIO.output(self.backwardsPIN,self.back)
    
        GPIO.output(self.leftPIN,self.left)
    
        GPIO.output(self.rightPIN,self.right)

        if(not self.isChasing):
            if(self.back):
                print ('Backwards')
            if(self.forward):
                print ('forward')
            if(self.left):
                print ('left')
            if(self.right):
                print ('right')                                    

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
            print ("hit button1")
            if(self.menuIndex == 1):
                print ('capturing WAY POINT')
                self.captureWayPoint = True
                self.exitMenu()

        if(self.wm.state['buttons'] & cwiid.BTN_2):
            if(self.menuIndex == 1):
                self.captureWayPoint = False
                print ('start chase')
                thread.start_new_thread(self.chase,(self.wayPoint,"signalblink",self.writeLevel,))  
                self.exitMenu()

    def pair(self):
        
        #Thread.start_new_thread(self.pairSignal,("signalblink",self.writeLevel,))
        
        Thread(target=self.pairSignal)

        if(self.enableBlueTooth):
    
            print ('Press 1+2 on your Wiimote now...')
            
            attempts = 1

            while not self.wm:                        

                try:

                    self.wm = cwiid.Wiimote()

                except RuntimeError:

                    print ("Error opening wiimote connection")
                    print ("attempt " + str(attempts)) 

                attempts +=1             
            
            self.isPaired = True                        
            self.wm.led = 1
            self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC 
            print ('PAIRED')
            GPIO.setup(self.signalLight,True)

            time.sleep(3)

