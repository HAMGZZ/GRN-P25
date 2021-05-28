
import pandas
import Adafruit_CharLCD as LCD
from gpiozero import LED
from gpiozero import Button
from encoder import Encoder
import time

class UI:

    def __init__(self, talkGroupFile, talkGroupCatagoriesFile) -> None:
        lcd_rs = 27  # Change this to pin 21 on older revision Raspberry Pi's
        lcd_en = 22
        lcd_d4 = 25
        lcd_d5 = 24
        lcd_d6 = 23
        lcd_d7 = 18
        lcd_red   = 4
        lcd_green = 17
        lcd_blue  = 7  # Pin 7 is CE1
        self.lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, 16, 2, lcd_red, lcd_green, lcd_blue)
        self.red = LED(12)
        self.green = LED(16)
        self.blue = LED(20)
        self.button = Button(13)
        self.enc = Encoder(26,19)
        self.talkGroupFile = talkGroupFile
        self.talkGroupCatagoriesFile = talkGroupCatagoriesFile
        self.talkGroups = pandas.read_csv(talkGroupFile, sep='\t', header=None, names=['TGID', 'TGNAME'])
        self.talkGroupCatagories = pandas.read_csv(talkGroupCatagoriesFile, sep='\t', header=None, names=['GROUP'])
        self.lastHeardTG = 0
        self.prevTime = 0
    
    def tgId2Name(self, id):
        try:
            if id is not (None or 0):
                self.lastHeardTG = id
                return self.talkGroups.loc[self.talkGroups[self.talkGroups['TGID'] == id].index[0]].at['TGNAME']
            elif self.lastHeardTG is not None:
                return self.talkGroups.loc[self.talkGroups[self.talkGroups['TGID'] == self.lastHeardTG].index[0]].at['TGNAME']
        except:
            return " "

    def count2tgid(self, count):  
        return self.talkGroups.loc[count].at['TGID']
    
    def CurrentStateString(self, CurrentState):
        if CurrentState == 0:
            currTime = time.time_ns()
            if currTime - self.prevTime > 5000:
                self.prevTime = currTime
                self.red.off()
                self.green.toggle()
                self.blue.off()
            return "NO CON"
        elif CurrentState == 1:
            self.red.off()
            self.green.on()
            self.blue.off()
            return "IDLE"
        elif CurrentState == 2:
            self.red.on()
            self.green.on()
            self.blue.off()
            return "ACTIVE"
        elif CurrentState == 3:
            self.red.on()
            self.green.on()
            self.blue.on()
            return "VOICE"
        else:
            self.red.off()
            self.green.off()
            self.blue.off()
            return "ERROR"
        

    def UpdateDisplay(self, currentState, tgid, freq, srcaddr, bitrate = 0, displayOption = 0):
        if displayOption == 0:
            self.lcd.set_cursor(0,0)
            self.lcd.message(str(srcaddr).ljust(10, ' ') + str(bitrate).rjust(6, ' '))
            self.lcd.set_cursor(0,1)
            self.lcd.message(self.tgId2Name(tgid).ljust(10, ' ') + self.CurrentStateString(currentState).rjust(6, ' '))
        elif displayOption == 1:
            self.lcd.set_cursor(0,0)
            self.lcd.message(self.tgId2Name(tgid).ljust(11, ' ') + str(freq).rjust(5, ' '))
            self.lcd.set_cursor(0,1)
            self.lcd.message(str(srcaddr).ljust(10, ' ') + self.CurrentStateString().rjust(6, ' '))
        elif displayOption == 3:
            self.lcd.set_cursor(0,0)
            self.lcd.message(str(srcaddr).ljust(10, ' ') + str(bitrate).rjust(6, ' '))
            self.lcd.set_cursor(0,1)
            self.lcd.message(self.tgId2Name(tgid).ljust(10, ' ') + str(freq).rjust(6, ' '))
    
    def file_len(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def tgMenu(self):
        self.red.off()
        self.blue.off()
        self.green.off()
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message("Choose TG GROUP>")
        time.sleep(1)
        self.lcd.set_cursor(0,1)
        catNumLines = self.file_len(self.talkGroupCatagoriesFile)

        self.enc.value = 0
        previousEncVal = -1
        buttonCounter = 0
        buttonPressedFlag = False
        while True:
            if self.enc.getValue() < 0:
                self.enc.value = catNumLines - 1
            elif self.enc.getValue() > catNumLines:
                self.enc.value = 0
            if self.enc.getValue() != previousEncVal:
                self.lcd.set_cursor(0,1)
                encVal = self.enc.getValue()
                name = self.talkGroupCatagories.loc[encVal].at['GROUP']
                self.lcd.msg(name.ljust(16, ' '))
                previousEncVal = encVal

            while self.button.is_pressed:
                buttonCounter += 1
                buttonPressedFlag = True
                time.sleep(0.01)
                if buttonCounter > 1:
                    self.green.on()
                if buttonCounter > 100:
                    self.red.on()
            
            if buttonPressedFlag:
                if buttonCounter < 100:
                    self.tgChange()
                    break
                elif buttonCounter >= 100:
                    break

    def tgChange(self, groupName):
    
        self.red.off()
        self.blue.off()
        self.green.off()
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message("Choose TG GROUP>")
        self.lcd.set_cursor(0,1)
        
        tgidList = []

        tgNumLines = self.file_len(self.talkGroupFile)

        self.enc.value = 0
        previousEncVal = -1
        buttonCounter = 0
        buttonPressedFlag = False
        time.sleep(1)

        while True:
            if self.enc.getValue() < 0:
                self.enc.value = tgNumLines - 1
            if self.enc.getValue() > tgNumLines:
                self.enc.value = 0
            if self.enc.getValue() != previousEncVal:
                count = self.enc.getValue()
                self.lcd.set_cursor(0,1)
                name = self.tgId2Name(self.count2tgid(count))
                if groupName in name:
                    self.lcd.message(str(name).ljust(16, ' '))
                    previousEncVal = count
                else:
                    self.enc.value += 1

            while self.button.is_pressed:
                buttonCounter += 1
                buttonPressedFlag = True
                time.sleep(0.01)
                if buttonCounter > 1:
                    self.green.on()
                if buttonCounter > 100:
                    self.red.on()
                if buttonCounter > 200:
                    self.blue.on()
                print(counter)

            if buttonPressedFlag:
                buttonPressedFlag = False;
                if buttonCounter > 1:
                    print(tgidList)
                    if buttonCounter < 100:
                        if self.count2tgid(count) not in tgidList:
                            tgidList.append(self.count2tgid(count))
                            buttonCounter = 0
                            self.enc.value = 0
                            time.sleep(0.05)
                            self.red.off()

                    elif buttonCounter >= 100 and buttonCounter < 200:
                        f = open("wl.wlist", 'a')
                        for id in tgidList:
                            f.write(str(id) + "\n\r")
                        f.close()
                        self.lcd.set_cursor(0,0)
                        self.lcd.message("Saved TG List\nStarting Radio...")
                        self.red.off()
                        self.blue.off()
                        self.green.off()
                        time.sleep(0.5)
                        break
                    
                    elif buttonCounter >= 200:
                        for x in  range(5):
                            self.red.on()
                            self.blue.on()
                            self.greeb.on()
                            time.sleep(0.05)
                            self.red.off()
                            self.blue.off()
                            self.green.off()
                            time.sleep(0.05)
                        f = open("wl.wlist", 'w')
                        f.write("")
                        f.close()
                        self.lcd.set_cursor(0,0)
                        tgidList = []
                        self.lcd.message("WHITE LIST\nCLEARED")
                        time.sleep(1)
                        counter = 0
                        self.lcd.clear()
                        self.lcd.set_cursor(0,0)
                        name = self.tgId2Name(self.count2tgid(self.enc.value))
                        self.lcd.message(str(name).ljust(16, ' '))

    def menu(self):
        menuOption = ["<   SET TGID   >", "< CURRENT TGID >", "<   LCD  RGB   >", "<   DISPLAY    >"]
        self.red.off()
        self.blue.off()
        self.green.off()
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message("Menu")
        self.lcd.set_cursor(0,1)
        self.enc.value = 0
        prevcount = -1
        time.sleep(0.5)
        while True:
            if self.enc.getValue() < 0:
                self.enc.value = len(menuOption) - 1
            if self.enc.getValue() > len(menuOption) - 1:
                self.enc.value = 0
            if self.enc.getValue() != prevcount:
                count = self.enc.getValue()
                self.lcd.set_cursor(0,1)
                self.lcd.message(menuOption[count])
                prevcount = count
            if self.button.is_pressed:
                if  count == 0:
                    self.tgMenu()
                    break
                elif count == 1:
                    self.currentTg()
                    break
                elif count == 2:
                    self.setRGB()
                    break
                elif count == 3:
                    self.setDisplay()
                    break
    