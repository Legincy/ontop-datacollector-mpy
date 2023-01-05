from machine import Pin, SoftI2C
import lib.ssd1306 as ssd1306

class Display():
    display = None
    __view = None

    def __init__(self, pin_sda, pin_scl):
        self.width = 128
        self.height = 64
        self.i2c = SoftI2C(sda=Pin(pin_sda), scl=Pin(pin_scl))
        
        # i2c-address is default (0x3C)
        self.display = ssd1306.SSD1306_I2C(self.width, self.height, self.i2c)
        self.display.fill(0)
        self.display.show()

    def __wifi(self, dbm):
        if dbm is None or dbm == 0:
            xpos = self.width - 8*8 # "No Wifi!"-> 8 chars * 8 pixels
            ypos = 0
            self.display.fill_rect(xpos, ypos, int(self.width / 2), 8, 0)
            self.display.text('No WiFi!', xpos, ypos)
        else:
            charcount = len(str(abs(dbm))) # convert dbm measurement to char to get digit-count
            
            xpos = int(self.width / 2)
            ypos = 0

            if charcount == 1:
                xpos += 2*8
            elif charcount == 2:
                xpos += 1*8
            elif charcount == 3:
                pass
            else:
                return False

            self.display.fill_rect(int(self.width / 2), ypos, int(self.width / 2), 8, 0)  # second half of header
            self.display.text('{} dBm'.format(dbm), xpos, ypos)

    def __clock(self, time):
        if time is None:
            time = "00:00"

        time.localtime
        
        xpos = 0
        ypos = 0

        self.display.fill_rect(0, 0, int(self.width / 2), 8, 0) # first half of header
        self.display.text(time, xpos, ypos)

    def header(self, time, dbm):
        self.__clock(time) # draws clock component
        self.__wifi(dbm) # draws wifi component
        
        self.display.fill_rect(0, 8, self.width, 3, 0) # 3 pixel cleared area
        self.display.hline(0, 9, self.width, 1) # 1 pixel line, centered in cleared area

        self.display.show()

    def drawMeasurement(self, text, value):
        text = "{}:".format(text[0:15]) # only use first 15 chars of text, because it would overflow the display otherwise
        value = str(value)

        self.display.fill_rect(0, 11, self.width, self.height - 11, 0) # clear whole area below separator-line
        self.display.text(text, max(0, int(self.width / 2 - len(text) / 2 * 8)), 24, 1) # position in the center, never go below x=0
        self.display.text(value, max(0, int(self.width / 2 - len(value) / 2 * 8)), 42, 1)

    def getView(self):
        return self.__view