# 26/03/2021 Lewis Hamilton
#place inside apps folder

import os
import subprocess
import time
import signal
import sys
import board
import busio
import sparkfun_qwiictwist
import pandas

import Adafruit_CharLCD as LCD

lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 2
lcd_columns = 16
lcd_rows = 2


lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)



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
    counter = 0
    tgidList = []
    frontPan.count = 0;
    while True:
        count = frontPan.count
        lcd.set_cursor(0,0)
        name = tgId2Name(count2tgid(count))
        lcd.message(str(name).ljust(16, ' '))

        while frontPan.pressed:
            counter += 1
            time.sleep(0.01)
            if counter > 1:
                frontPan.set_color(255,0,0)
            if counter > 300:
                frontPan.set_color(255,255,0)
            if counter > 500:
                frontPan.set_color(255,255,255)

        if counter > 1:
            if counter < 300:
                frontPan.set_color(255,0,0)
                tgidList.append(count2tgid(count))
                counter = 0
                time.sleep(0.05)
                frontPan.set_color(0,0,0)

            elif counter >= 300 and counter < 500:
                frontPan.set_color(255,255,255)
                f = open("wl.wlist", 'w')
                for id in tgidList:
                    f.write(str(id) + "\n\r")
                f.close()
                frontPan.set_color(0,0,0)
                break
            
            elif counter >= 500:
                for x in  range(5):
                    frontPan.set_color(255,255,255)
                    time.sleep(0.05)
                    frontPan.set_color(0,0,0)
                    time.sleep(0.05)
                f = open("wl.wlist", 'w')
                f.write("")
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


def CurrentStateString():
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
    lcd.set_cursor(0,0)
    lcd.message(tgId2Name(tgid).ljust(10, ' ')+str(freq).rjust(6, ' '))
    lcd.message(str(srcaddr).ljust(10, ' ')+CurrentStateString().rjust(6, ' '))



def main():
    global op25
    signal.signal(signal.SIGINT, signal_handler)
    op25 = subprocess.Popen("./startop25.sh", shell = False)
    print(op25.pid)
    print("Currnt tg = " + str(tgid))

    while not frontPan.connected:
        lcd.clear()
        lcd.message("Front Panel not connected")

    lcd.clear()

    while True:
        try:
            readFile()
        except:
            time.sleep(0.5)
        print("FREQ: " + str(freq) + "  TGID: " + str(tgid) + "  ADDRESS: " + str(srcaddr) + "  STATE: " + CurrentStateString())
        UpdateDisplay()
        if frontPan.pressed:
            frontPan.set_color(0,0,0)
            lcd.clear()
            lcd.message("Change TGID List")
            time.sleep(1)
            lcd.lear()
            tgChange()


if __name__ == '__main__':

    try:
      main()
    except KeyboardInterrupt:
      pass
    