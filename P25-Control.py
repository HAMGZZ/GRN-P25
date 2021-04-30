# 26/03/2021 Lewis Hamilton
#place inside apps folder

import os
import subprocess
import time
import signal
import sys
import board
import busio
import pandas
from gpiozero import LED
from gpiozero import Button
from encoder import Encoder

import Adafruit_CharLCD as LCD

lcd_rs = 27  # Change this to pin 21 on older revision Raspberry Pi's
lcd_en = 22
lcd_d4 = 25
lcd_d5 = 24
lcd_d6 = 23
lcd_d7 = 18
lcd_red   = 4
lcd_green = 17
lcd_blue  = 7  # Pin 7 is CE1


lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, 16, 2, lcd_red, lcd_green, lcd_blue)



CurrentState = 0
tgid = 10049        # tgid of incomming transmission
distgid = 10049
freq = 0        # frequency of incomming transmission
srcaddr = 0     # src address of incoming transmission
op25 = 0        #Var for OP25 program
tgname = ""
numberOfLines = 0
red = LED(12)
green = LED(16)
blue = LED(20)
button = Button(13)
enc = Encoder(26,19)

def signal_handler(sig, frame):
    global op25
    print('\n\rExiting')
    op25.kill()
    ex = subprocess.call("./exit.sh", shell = False)
    sys.exit(0)

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def tgId2Name(id):
    grn = pandas.read_csv('grn.tsv', sep='\t', header=None, names=['TGID', 'TGNAME'])
    return grn.loc[grn[grn['TGID'] == id].index[0]].at['TGNAME']

def count2tgid(count):
    grn = pandas.read_csv('grn.tsv', sep='\t', header=None, names=['TGID', 'TGNAME'])
    return grn.loc[count].at['TGID']

def set_color(r, g, b):
    if r > 1:
        red.on()
    else:
        red.off()
    if g > 1:
        green.on()
    else:
        green.off()
    if b > 1:
        blue.on()
    else:
        blue.off()


def tgChange():
    global op25
    global tgid
    global distgid
    global CurrentState
    CurrentState = 0
    op25.terminate()
    set_color(0,0,0)
    counter = 0
    tgidList = []
    count = 0;
    enc.value = 0;
    prevcount = -1;
    while True:
        count = enc.getValue()
        if(count < 0):
            count = numberOfLines - 1
        if(count > numberOfLines):
            count = 0
        if(count != prevcount):
            lcd.set_cursor(0,0)
            name = tgId2Name(count2tgid(count))
            lcd.message(str(name).ljust(16, ' '))
            prevcount = count

        while button.is_pressed:
            counter += 1
            time.sleep(0.01)
            if counter > 1:
                set_color(255,0,0)
            if counter > 100:
                set_color(255,255,0)
            if counter > 300:
                set_color(255,255,255)

        if counter > 1:
            if counter < 100:
                set_color(255,0,0)
                tgidList.append(count2tgid(count))
                counter = 0
                time.sleep(0.05)
                set_color(0,0,0)
                distgid = count2tgid(count)

            elif counter >= 100 and counter < 300:
                set_color(255,255,255)
                f = open("wl.wlist", 'a')
                for id in tgidList:
                    f.write(str(id) + "\n\r")
                f.close()
                set_color(0,0,0)
                time.sleep(0.5)
                UpdateDisplay()
                break
            
            elif counter >= 300:
                for x in  range(5):
                    set_color(255,255,255)
                    time.sleep(0.05)
                    set_color(0,0,0)
                    time.sleep(0.05)
                f = open("wl.wlist", 'w')
                f.write("")
                f.close()
                lcd.set_cursor(0,0)
                lcd.message("WHITE LIST\nCLEARED")
                time.sleep(1)
                counter = 0
                lcd.clear()
                lcd.set_cursor(0,0)
                name = tgId2Name(count2tgid(count))
                lcd.message(str(name).ljust(16, ' '))

                

    
    op25 = subprocess.Popen("./startop25.sh", shell = False)

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


def CurrentStateString():
    global CurrentState
    if CurrentState == 0:
        set_color(0,0,0)
        return "NO CON"
    elif CurrentState == 1:
        set_color(0,255,0)
        return "IDLE"
    elif CurrentState == 2:
        set_color(255,0,0)
        return "ACTIVE"
    elif CurrentState == 3:
        set_color(0,0,255)
        return "VOICE"
    else:
        return "ERROR"
    
def UpdateDisplay():
    lcd.set_cursor(0,0)
    lcd.message(tgId2Name(distgid).ljust(11, ' ')+str(freq).rjust(5, ' '))
    lcd.set_cursor(0,1)
    lcd.message(str(srcaddr).ljust(10, ' ')+CurrentStateString().rjust(6, ' '))



def main():
    global op25
    global numberOfLines
    lcd.set_color(1,1,1)
    signal.signal(signal.SIGINT, signal_handler)
    op25 = subprocess.Popen("./startop25.sh", shell = False)
    print(op25.pid)
    print("Currnt tg = " + str(tgid))
    lcd.clear()
    numberOfLines = file_len("grn.tsv")
    prevState = -1

    while True:
        try:
            readFile()
        except:
            time.sleep(0.1)
        print("FREQ: " + str(freq) + "  TGID: " + str(tgid) + "  ADDRESS: " + str(srcaddr) + "  STATE: " + CurrentStateString())
        if CurrentState != prevState:
            UpdateDisplay()
            prevState = CurrentState

        if button.is_pressed:
            set_color(0,0,0)
            lcd.clear()
            lcd.message("Change TGID List")
            time.sleep(1)
            lcd.clear()
            tgChange()


if __name__ == '__main__':

    try:
      main()
    except KeyboardInterrupt:
      pass
    