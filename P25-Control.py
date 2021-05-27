# 26/03/2021 Lewis Hamilton
#place inside apps folder

import os
import subprocess
import time
import signal
import sys
import board
import busio
import UI





CurrentState = 0
tgid = 10049        # tgid of incomming transmission
distgid = 10049
freq = 0        # frequency of incomming transmission
srcaddr = 0     # src address of incoming transmission
op25 = 0        #Var for OP25 program
tgname = ""
numberOfLines = 0

def signal_handler(sig, frame):
    global op25
    print('\n\rExiting')
    killp25()
    ex = subprocess.call("./exit.sh", shell = False)
    sys.exit(0)

def get_pid(name):
    return subprocess.check_output(["pidof", "-s",name])

def killp25():
    os.kill(int(get_pid("python2")), signal.SIGKILL)


def readFile():
    global tgid
    global freq
    global srcaddr
    global CurrentState
    global distgid
    f1 = open("/tmp/ramdisk/p25Data.gzz", 'r')
    lines = f1.readlines()
    if int(lines[0]) != 0:
        distgid = int(lines[0])
    tgid = int(lines[0])
    freq = float(lines[2])
    f1.close
    f2 = open("/tmp/ramdisk/p25DataSrc.gzz", 'r')
    lines = f2.readlines()
    srcaddr = int(lines[0])
    f2.close;

    if freq == 0:
        CurrentState = 0
    else:
        CurrentState = 1
    if tgid != 0 or (srcaddr != 0 and tgid == 0):
        CurrentState = 2
    if srcaddr != 0 and tgid != 0:
        CurrentState = 3




def main():
    global op25
    signal.signal(signal.SIGINT, signal_handler)
    op25 = subprocess.Popen("./startop25.sh", shell = False)
    print(op25.pid)
    print("Currnt tg = " + str(tgid))
    prevState = -1
    ui = UI.UI()
    while True:
        
        try:
            readFile()
        except:
            time.sleep(0.1)
        #print("FREQ: " + str(freq) + "  TGID: " + str(tgid) + "  ADDRESS: " + str(srcaddr) + "  STATE: " + CurrentStateString())


        if CurrentState != prevState:
            ui.UpdateDisplay(CurrentState, tgid, freq, srcaddr)
            prevState = CurrentState

        if ui.button.is_pressed:
            killp25()
            time.sleep(0.5)
            ui.menu()
            time.sleep(0.5)
            op25 = subprocess.Popen("./startop25.sh", shell = False)


if __name__ == '__main__':

    try:
      main()
    except KeyboardInterrupt:
      pass
    