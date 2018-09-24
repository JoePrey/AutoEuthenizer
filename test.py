import socket,struct,signal,subprocess,os



p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
out, err = p.communicate()

for line in out.splitlines():
    if "raspivid" in str(line):
        print(line)
        pid = int(line.split(None, 1)[0])
        
        os.kill(pid, signal.SIGKILL)
    
        
