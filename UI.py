
import pandas
import Adafruit_CharLCD as LCD
import board
import busio
import qwiic_twist
import time

class UI:

    def __init__(self, talkGroupFile, talkGroupCatagoriesFile) -> None:
        lcd_rs = 27  # Change this to pin 21 on older revision Raspberry Pi's
        lcd_en = 22
        lcd_d4 = 25
        lcd_d5 = 24
        lcd_d6 = 23
        lcd_d7 = 6
        lcd_red   = 4
        lcd_green = 17
        lcd_blue  = 7  # Pin 7 is CE1
        self.lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, 16, 2, lcd_red, lcd_green, lcd_blue)
        
        
        

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.twist = qwiic_twist.QwiicTwist(self.i2c)
        if self.twist.connected:
            print("Connected to UI")
        else:
            print("Could not connect to UI!")
            exit()
        

        
        self.talkGroupFile = talkGroupFile
        self.talkGroupCatagoriesFile = talkGroupCatagoriesFile
        self.talkGroups = pandas.read_csv(talkGroupFile, sep='\t', header=None, names=['TGID', 'TGNAME'])
        self.talkGroupCatagories = pandas.read_csv(talkGroupCatagoriesFile, sep=',', header=None, names=['GROUP', 'SEARCH'], dtype="string")
        self.lastHeardTG = 0
        self.prevTime = 0
        self.custom_towerSymbol = [	0,31,21,14,4,4,4,4 ]
        self.custom_sigNone = [ 0,0,14,25,21,19,14,0 ]
        self.custom_sigOne = [ 0,0,0,0,0,0,16,16 ]
        self.custom_sigTwo = [ 0,0,0,0,0,8,24,24 ]
        self.custom_sigThree = [ 0,0,0,0,4,12,28,28 ]
        self.custom_sigFour = [ 0,0,0,2,6,14,30,30 ]
        self.custom_sigFive = [ 0,0,1,3,7,15,31,31 ]
        self.custom_signalArray = [self.custom_sigNone, self.custom_sigOne, self.custom_sigTwo, self.custom_sigThree, self.custom_sigFour, self.custom_sigFive, self.custom_towerSymbol]
        for i in range(len(self.custom_signalArray)):
            self.lcd.create_char(i, self.custom_signalArray[i])

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
                self.twist.set_colour(0,0,0)
            return "NO CON"
        elif CurrentState == 1:
            self.twist.set_colour(0,255,0)
            return "IDLE"
        elif CurrentState == 2:
            self.twist.set_colour(255,255,0)
            return "DATA"
        elif CurrentState == 3:
            self.twist.set_colour(255,255,255)
            return "VOICE"
        else:
            self.twist.set_colour(0,0,0)
            return "ERROR"
        

    def UpdateDisplay(self, currentState, tgid, freq, srcaddr, bitrate, signalStrength, displayOption = 0):
        if displayOption == 0:
            self.lcd.set_cursor(0,0)
            self.lcd.message(str(srcaddr).ljust(14, ' '))
            self.lcd.message(str(signalStrength.to_bytes(1, byteorder='big')))
            self.lcd.message('\x06')
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
        self.twist.set_colour(0,0,0)
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message("Choose TG GROUP>")
        time.sleep(1)
        self.lcd.set_cursor(0,1)
        catNumLines = self.file_len(self.talkGroupCatagoriesFile)

        self.twist.count = 0
        self.twist.set_count(0)
        previousEncVal = -1
        buttonCounter = 0
        buttonPressedFlag = False
        name = ""
        while True:
            value = self.twist.get_count()
            if value != previousEncVal :
                if value < 0:
                    value = catNumLines - 1
                if value >= catNumLines:
                    value = 0
                self.lcd.set_cursor(0,1)
                name = self.talkGroupCatagories.loc[value].at['GROUP']
                tgsearchname = self.talkGroupCatagories.loc[value].at['SEARCH']
                self.lcd.message(name.ljust(16, ' '))
                previousEncVal = value

            while self.twist.is_pressed():
                buttonCounter += 1
                buttonPressedFlag = True
                time.sleep(0.01)
                if buttonCounter > 1:
                    self.twist.set_colour(0,255,0)
                if buttonCounter > 100:
                    self.twist.set_colour(255,255,0)
            
            if buttonPressedFlag:
                if buttonCounter < 100:
                    print(tgsearchname)
                    self.tgChange(tgsearchname)
                    break
                elif buttonCounter >= 100:
                    break

    def tgChange(self, groupName):
    
        self.twist.set_colour(0,0,0)
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message("Choose TG      >")
        self.lcd.set_cursor(0,1)
        
        tgidList = []

        tgNumLines = self.file_len(self.talkGroupFile)

        self.twist.set_count(0)
        previousEncVal = -1
        buttonCounter = 0
        buttonPressedFlag = False
        time.sleep(1)
        SpinningCursor = ['\\', '|', '/', '-']
        while True:
            value = self.twist.get_count()
            if value != previousEncVal :
                if value < 0:
                    value = tgNumLines - 1
                if value >= tgNumLines:
                    value = 0
                self.lcd.set_cursor(0,1)
                name = self.tgId2Name(self.count2tgid(value))
                if groupName in name:
                    self.lcd.message(str(name).ljust(16, ' '))
                    previousEncVal = value
                else:
                    self.twist.set_count(-1)
                    name = self.tgId2Name(self.count2tgid(self.twist.get_value()))
                    if groupName in name:
                        pass
                    else:
                        self.twist.set_value(self.twist.get_value() + 2)
                        name = self.tgId2Name(self.count2tgid(self.twist.get_value()))
                        if groupName in name:
                            pass
                        else:
                            self.twist.set_value(self.twist.get_value() + 1)
                    self.lcd.message(SpinningCursor[self.twist.get_value() % 4].ljust(16, ' '))
                    

            while self.button.is_pressed:
                buttonCounter += 1
                buttonPressedFlag = True
                time.sleep(0.01)
                if buttonCounter > 1:
                    self.twist.set_colour(0,255,0)
                if buttonCounter > 100:
                    self.twist.set_colour(255,255,0)
                if buttonCounter > 200:
                    self.twist.set_colour(255,255,255)

            if buttonPressedFlag:
                buttonPressedFlag = False;
                if buttonCounter > 1:
                    print(tgidList)
                    if buttonCounter < 100:
                        if self.count2tgid(value) not in tgidList:
                            tgidList.append(self.count2tgid(value))
                            buttonCounter = 0
                            self.twist.set_count(0)
                            time.sleep(0.05)
                            self.twist.set_colour(0,0,0)

                    elif buttonCounter >= 100 and buttonCounter < 200:
                        f = open("wl.wlist", 'a')
                        for id in tgidList:
                            f.write(str(id) + "\n\r")
                        f.close()
                        self.lcd.set_cursor(0,0)
                        self.lcd.message("Saved TG List\nStarting Radio...")
                        self.twist.set_colour(0,0,0)
                        time.sleep(0.5)
                        break
                    
                    elif buttonCounter >= 200:
                        for x in  range(5):
                            self.twist.set_colour(255,255,255)
                            time.sleep(0.05)
                            self.twist.set_colour(0,0,0)
                            time.sleep(0.05)
                        f = open("wl.wlist", 'w')
                        f.write("")
                        f.close()
                        self.lcd.set_cursor(0,0)
                        tgidList = []
                        self.lcd.message("WHITE LIST\nCLEARED")
                        time.sleep(1)
                        buttonCounter = 0
                        self.lcd.clear()
                        self.lcd.set_cursor(0,0)
                        self.lcd.message("Choose TG      >")
                        self.lcd.set_cursor(0,1)
                        name = self.tgId2Name(self.count2tgid(self.twist.get_count()))
                        self.lcd.message(str(name).ljust(16, ' '))

    def currentTg(self):
        whiteList = pandas.read_csv('wl.wlist', sep=',', header=None, names=['TG'], dtype="string")
        fileLen = self.file_len('wl.wlist')
        value = self.twist.get_count()
        previousEncVal = 0
        value = self.twist.get_count()
        self.twist.set_count(0)
        buttonCounter = 0
        while True:
            value = self.twist.get_count()
            if value != previousEncVal :
                if value < 0:
                    value = fileLen - 1
                if value >= fileLen:
                    value = 0
                self.lcd.set_cursor(0,1)
                name = self.tgId2Name(whiteList.loc[value].at['TG'])
                self.lcd.message(str(name).ljust(16, ' '))
                previousEncVal = value
            while self.twist.is_pressed():
                buttonCounter += 1
                time.sleep(0.01)
                if buttonCounter > 1:
                    self.twist.set_colour(0,255,0)

            if buttonCounter > 1:
                break


    def menu(self):
        menuOption = ["<   SET TGID   >", "< CURRENT TGID >", "<   LCD  RGB   >", "<   DISPLAY    >"]
        self.twist.set_colour(0,0,0)
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message("Menu")
        self.lcd.set_cursor(0,1)
        self.twist.set_count(0)
        prevcount = -1
        buttonCounter = 0
        time.sleep(0.5)
        while True:
            if self.twist.get_count() != prevcount:
                count = self.twist.get_count()
                self.lcd.set_cursor(0,1)
                self.lcd.message(menuOption[count])
                prevcount = count
            while self.twist.is_pressed():
                buttonCounter += 1
                time.sleep(0.01)
                if buttonCounter > 1:
                    self.twist.set_colour(0,255,0)
                elif buttonCounter > 100:
                    self.twist.set_colour(255,255,0)
            
            if buttonCounter > 1 and buttonCounter < 100:
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
            if buttonCounter > 100:
                break
    
