# 26/03/2021 Lewis Hamilton
#place inside apps folder

import os
import subprocess
import time
import signal
import sys
import UI
import op25Data

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


def main():
    print("LEWIS HAMILTON 2021 - P25 Receiver - Aimed at the NSW GRN")
    global op25
    signal.signal(signal.SIGINT, signal_handler)

    op25 = subprocess.Popen("./startop25.sh", shell = False) # Start op25 subprocess

    print("OP25 PID = " + str(op25.pid))

    data = op25Data.Data()
    ui = UI.UI('grn.tsv', 'groupList.csv')
    
    
    while True:
        data.updateData()
        ui.UpdateDisplay(data.CurrentState, data.tgid, data.freq, data.srcaddr, data.dataRate, data.signalStrength)
        print("BUTTON? ")
        print(ui.twist.is_pressed())
        if ui.twist.is_pressed() == True:
            print("ENTERING MENU")
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
    