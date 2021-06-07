

class lcdMenu:
    def __init__(self, lcdDrive, menuText, num_of_menu_items, menu_items, _callbackList, encoder, red, green, blue) -> None:   
        self.lcd = lcdDrive
        self.menuText = menuText
        self.item_num = num_of_menu_items
        self.menu_items = menu_items
        self._callbackList = _callbackList
        self.encoder = encoder
        self.red = red
        self.green = green
        self.blue = blue
        pass
    
    def menuDraw(self):
        self.red.off()
        self.blue.off()
        self.green.off()
        self.lcd.clear()
        self.lcd.set_cursor(0,0)
        self.lcd.message(self.menuText)
        self.lcd.set_cursor(0,1)
        self.enc.value = 0
    
    def menuLoop(self):
        



