import socket,struct,signal,subprocess,os
import os


def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')            


    
def get_ip_address(ifname):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])

def killthreads(threadName,kill):
    
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    
    out, err = p.communicate()
    
    ret = 0
    

    for line in out.splitlines():
        if threadName in str(line):
            print(line)
            pid = int(line.split(None, 1)[0])
            
            ret +=1
    
            if(kill):
                os.kill(pid, signal.SIGKILL)
                print ("Killing" + str(line))
    return ret                
            
        
