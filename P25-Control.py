# 26/03/2021 Lewis Hamilton
#place inside apps folder

import os
import subprocess
import time
import signal
import sys
import UI


CurrentState = 0
tgid = 0        # tgid of incomming transmission
freq = 0        # frequency of incomming transmission
srcaddr = 0     # src address of incoming transmission
op25 = 0        # Var for OP25 program
dataRate = 0    # Used to calculate the rate of information comming in and thus the signal strength as well.

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


def updateData():
    global tgid
    global freq
    global srcaddr
    global CurrentState
    global distgid
    global dataRate

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

    f3 = open("/tmp/ramdisk/p25DataRate.gzz", 'r')
    lines = f1.readlines()
    dataRate = int(lines[0])
    f3.close
    if freq == 0:
        CurrentState = 0
    else:
        CurrentState = 1
    if tgid != 0 or (srcaddr != 0 and tgid == 0):
        CurrentState = 2
    if srcaddr != 0 and tgid != 0:
        CurrentState = 3




def main():
    print("LEWIS HAMILTON 2021 - P25 Receiver - Aimed at the NSW GRN")
    global op25
    global CurrentState
    global dataRate
    global srcaddr
    global freq
    signal.signal(signal.SIGINT, signal_handler)

    op25 = subprocess.Popen("./startop25.sh", shell = False) # Start op25 subprocess

    print("OP25 PID = " + str(op25.pid))

    ui = UI.UI('grn.tsv', 'groupList.csv')
    
    
    while True:
        try:
            updateData()
        except:
            time.sleep(0.1)
        #print("FREQ: " + str(freq) + "  TGID: " + str(tgid) + "  ADDRESS: " + str(srcaddr) + "  STATE: " + CurrentStateString())


        ui.UpdateDisplay(CurrentState, tgid, freq, srcaddr, dataRate)
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
    