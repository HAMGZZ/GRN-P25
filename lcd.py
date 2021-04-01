import serial
import time
ser = serial.Serial('/dev/ttyS0', 96000)

def lcdInit():
    time.sleep(0.1)
    ser.write(bytearray([0xFE, 0x01, 0xFE, 0x0C]))
    
def lcd_string(string):
    ser.write(string.encode())

def lcd_clear():
    ser.write(bytearray([0xFE, 0x01]))

def lcd_setCursor(x):
    ser.write(bytearray([0xFE, 0x80, x]))