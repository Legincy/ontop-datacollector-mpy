# HW-390 Soil Moisture Sensor / STEMMA Soil Sensor
from machine import ADC

class HW390():
    __pin = None
    __adc = None
    __last_value = None

    # pin must be of machine.Pin type.
    def __init__(self, pin):
        self.__pin = pin
        self.__adc = ADC(pin)

    def measure(self):
        try:
            adcraw = self.__adc.read_u16()
            print(adcraw)
            print("")
        except:
            print("ADC could not be read.")
            raise

        if adcraw is None:
            self.__last_value = None
            print("ADC could not be read.")
            return False
        elif adcraw == 0:
            self.__last_value = None
            print("ADC returns 0, which is very unlikely. Is the sensor connected correctly?")
            return False
        elif adcraw > (2**16 - 100):
            self.__last_value = None
            print("Value pretty high. Is the sensor connected correctly?")
            return False
        else:
            self.__last_value = adcraw / (2**16) * 100 # norm to 100 (not percent, data are not evaluated that way)

    def get_data(self):
        self.measure()
        return self.__last_value