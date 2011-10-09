
import os
import sys
import commands
import subprocess

class Error(Exception):
    pass

def fatal(s):
    print >> sys.stderr, "FATAL: " + str(s)
    sys.exit(1)

def warning(s):
    print >> sys.stderr, "WARNING: " + str(s)

def mkdir(path):
    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

def system(command, *args):
    command = command + " " + " ".join([commands.mkarg(arg) for arg in args])
    err = os.system(command)
    if err:
        raise Error("command failed: " + command,
                    os.WEXITSTATUS(err))

def system_pipe(command, pipein, quiet=False):
    if quiet:
        p = subprocess.Popen(command,
                             stdin = subprocess.PIPE,
                             stdout = subprocess.PIPE,
                             #stderr = subprocess.PIPE,
                             close_fds = True)
    else:
        p = subprocess.Popen(command,
                             stdin = subprocess.PIPE,
                             close_fds = True)
        
    out, err =  p.communicate(pipein)
    return out, err

def getstatus(command):
    (s,o) = commands.getstatusoutput(command)
    return s

def getoutput(command, raise_err=True):
    (err, out) = commands.getstatusoutput(command)
    if err and raise_err:
        raise Error("command failed: " + command, err)
    
    return out

def is_mounted(dir):
    mounts = file("/proc/mounts").read()
    if mounts.find(dir) != -1:
        return True
    return False

def mount(device, mountp, options=None):
    if not is_mounted(device):
        print "mounting: " + device
        if options:
            system("mount", device, mountp, options)
        else:
            system("mount", device, mountp)

def umount(device):
    if is_mounted(device):
        print "umounting: " + device
        system("umount", "-f", device)

