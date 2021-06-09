import time

class lcdMenu:
    def __init__(self, lcdDrive, menuText, num_of_menu_items, menu_items, encoder, red, green, blue) -> None:   
        self.lcd = lcdDrive
        self.menuText = menuText
        self.item_num = num_of_menu_items
        self.menu_items = menu_items
        self._callbackList = _callbackList
        self.encoder = encoder
        self.red = red
        self.green = green
        self.blue = blue
        self.loop = True
        pass
    
    def menuDraw(self):
        self.red.off()
        self.blue.off()
        self.green.off()
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message(self.menuText)
        self.lcd.set_cursor(0,1)
        self.encoder.value = 0
    
    def menuLoop(self):
        prevEncoderCount = 0
        buttonCounter = 0
        encoderCount = 0
        while self.loop:
            if self.encoder.getValue() < 0:
                self.encoder.value = self.item_num - 1
            if self.encoder.getValue() > self.item_num - 1:
                self.encoder.value = 0
            if self.encoder.getValue() != prevEncoderCount:
                encoderCount = self.encoder.getValue()
                self.lcd.set_cursor(0,1)
                self.lcd.message(self.menu_items[encoderCount])
                prevEncoderCount = encoderCount
            while self.button.is_pressed:
                buttonCounter += 1
                time.sleep(0.01)
                if buttonCounter > 1:
                    self.green.on()         #SELECT
                elif buttonCounter > 100:
                    self.red.on()           #BACK
                elif buttonCounter > 200:
                    self.blue.on()          #BACK / CLEAR
            if buttonCounter > 1 and buttonCounter < 100:
                return [1,encoderCount]
            elif buttonCounter > 100 and buttonCounter < 200:
                return [2, encoderCount]
            elif buttonCounter > 200:
                return [3, encoderCount]



