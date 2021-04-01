# 26/03/2021 Lewis Hamilton
#place inside apps folder

import os
import subprocess
import time
import signal
import sys
import lcd
import board
import busio
import sparkfun_qwiictwist
import pandas



CurrentState = 0
tgid = 0
freq = 0
srcaddr = 0
op25 = 0
tgname = ""

i2c = busio.I2C(board.SCL, board.SDA)

frontPan = sparkfun_qwiictwist.Sparkfun_QwiicTwist(i2c)


def signal_handler(sig, frame):
    global op25
    print('\n\rExiting')
    op25.kill()
    ex = subprocess.call("./exit.sh", shell = False)
    sys.exit(0)

def tgId2Name(id):
    grn = pandas.read_csv('grn.tsv', sep=' ', header=None, names=['TGID', 'TGNAME'])
    return grn.loc[grn[grn['TGID'] == id].index[0]].at['TGNAME']

def count2tgid(count):
    grn = pandas.read_csv('grn.tsv', sep=' ', header=None, names=['TGID', 'TGNAME'])
    return grn.loc[count].at['TGID']


def tgChange():
    global op25
    global tgid
    op25.terminate()
    frontPan.set_color(0,0,0)
    while True:
        count = frontPan.count
        lcd.lcd_setCursor(0)
        name = tgId2Name(count2tgid(count))
        lcd.lcd_string(name)
        
        if frontPan.pressed:
            tgid = count2tgid(count)
            f = open("wl.wlist")
            f.write(str(tgid) + "\n\r");
            f.close()
            break
        
    op25 = subprocess.Popen("./startop25.sh", shell = False)

def readFile():
    global tgid
    global freq
    global srcaddr
    global CurrentState
    f1 = open("/tmp/ramdisk/p25Data.gzz", 'r')
    lines = f1.readlines()
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


def CurrentState():
    global CurrentState
    if CurrentState == 0:
        frontPan.set_color(0,0,0)
        return "NO CON"
    elif CurrentState == 1:
        frontPan.set_color(0,255,0)
        return "IDLE"
    elif CurrentState == 2:
        frontPan.set_color(255,0,0)
        return "ACTIVE"
    elif CurrentState == 3:
        frontPan.set_color(0,0,255)
        return "VOICE"
    else:
        return "ERROR"
    
def UpdateDisplay():
    lcd.lcd_setCursor(0)
    lcd.lcd_string(str(tgname).ljust(10, ' ')+str(freq).rjust(6, ' '))
    lcd.lcd_string(str(srcaddr).ljust(10, ' ')+CurrentState().rjust(6, ' '))



def main():
    signal.signal(signal.SIGINT, signal_handler)
    lcd.lcdInit()
    op25 = subprocess.Popen("./startop25.sh", shell = False)
    print(op25.pid)
    print("Currnt tg = " + str(tgid))

    while not frontPan.connected:
        lcd.lcd_clear()
        lcd.lcd_string("Front Panel not connected")

    lcd.lcd_clear()

    while True:
        try:
            readFile()
        except:
            time.sleep(0.5)
        print("FREQ: " + str(freq) + "  TGID: " + str(tgid) + "  ADDRESS: " + str(srcaddr) + "  STATE: " + CurrentState())
        UpdateDisplay()
        if frontPan.pressed:
            tgChange()


if __name__ == '__main__':

    try:
      main()
    except KeyboardInterrupt:
      pass
    