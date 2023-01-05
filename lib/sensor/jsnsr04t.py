import machine
from utime import sleep_us

class JSNSR04T:
    __trigPin = None
    __echoPin = None
    __last_value = None

    def __init__(self, trigPin, echoPin):
        print("Setting up JSN-SR04T")
        if isinstance(trigPin, int) and isinstance(echoPin, int):
            self.__trigPin = machine.Pin(trigPin, machine.Pin.OUT)
            self.__echoPin = machine.Pin(echoPin, machine.Pin.IN)
        else:
            raise ValueError
    
    def measure(self):
        try:
            self.__trigPin.off()
            sleep_us(2)
            self.__trigPin.on()
            sleep_us(10)
            self.__trigPin.off()
        except:
            pass

        try:
            pulse_time = machine.time_pulse_us(self.__echoPin, 1, 20000) # timeout: 20.000 us -> 340cm
        except:
            pass

        if pulse_time < 0: # should never happen
            return False
        elif pulse_time == -2 or pulse_time == -1: # timeout
            print("JSN-SR04T timeout.")
            return False
        else:
            self.__last_value = pulse_time * 0.034 / 2

        print(self.__last_value)
    
    def get_value(self):
        self.measure()
        if self.__last_value is not None:
            return self.__last_value
        else:
            print("there is no valid measurement for the JSN-SR04T sensor.")
            return None