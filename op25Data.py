
from signal import signal
import time

class Data:
    def __init__(self) -> None:    
        self.tgid = 0
        self.freq = 0
        self.srcaddr = 0
        self.CurrentState = 0
        self.distgid = 0
        self.dataRate = 0
        self.signalStrength = 0
        self.updateTimeFrame = 0
        self.previousDataRate = 0
        self.isCon = False

    def updateData(self):
        try:
            f1 = open("/tmp/ramdisk/p25Data.gzz", 'r')
            lines = f1.readlines()
            if int(lines[0]) != 0:
                self.distgid = int(lines[0])
            self.tgid = int(lines[0])
            self.freq = float(lines[2])
            f1.close

            f2 = open("/tmp/ramdisk/p25DataSrc.gzz", 'r')
            lines = f2.readlines()
            self.srcaddr = int(lines[0])
            f2.close;

            f3 = open("/tmp/ramdisk/p25DataRate.gzz", 'r')
            lines = f3.readlines()
            self.dataRate = int(lines[0])
            f3.close


            if time.time - self.updateTimeFrame >= 2:
                self.updateTimeFrame = time.time
                difference = self.dataRate - self.previousDataRate
                self.previousDataRate = self.dataRate
                # Check if we got even 1 packet to turn on con led
                if difference > 0:
                    self.isCon = True
                #Map data rate to a signal strength number 
                if difference > 30:
                    self.signalStrength = 5
                elif difference > 20:
                    self.signalStrength = 4
                elif difference > 15:
                    self.signalStrength = 3
                elif difference > 10:
                    self.signalStrength = 2
                elif difference > 5:
                    self.signalStrength = 1
                else:
                    self.signalStrength = 0
                print(difference)
                print(self.isCon)
        except:
            pass
        if not self.isCon:
            self.CurrentState = 0
        else:
            self.CurrentState = 1
        if self.tgid != 0 or (self.srcaddr != 0 and self.tgid == 0):
            self.CurrentState = 2
        if self.srcaddr != 0 and self.tgid != 0:
            self.CurrentState = 3