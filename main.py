# -*- coding:utf-8 -*-
import gc
import uasyncio as asyncio
from controller.DatacollectorController import DatacollectorController
from module.Display import Display


class Main:
    display = None

    def __init__(self):
        self._async_loop = asyncio.get_event_loop()
        self._datacollector_controller = DatacollectorController(self)

    def setup(self):
        self._datacollector_controller.setup()
        self.display = Display(21, 22)
        sync_completed = False

        while not sync_completed:
            # sync system-time via ntp
            import time

            try:
                # https://forum.micropython.org/posting.php?mode=quote&f=15&p=29387
                # micropython offers no timezone support - only GMT
                import ntptime

                ntptime.host = "pool.ntp.org"
                ntptime.settime()
                sync_completed = True
            except Exception as e:
                print(f"Error syncing time - {e}")
            time.sleep(5)

        self._async_loop.run_until_complete(self.main())

    async def main(self):
        while True:
            self.display.drawMeasurement("Temperatur", 23.22)
            await asyncio.sleep(1)
            self.display.drawMeasurement("Swag", "100 %")
            await asyncio.sleep(1)
            self.display.drawMeasurement("Feuchte", 0.5124)
            await asyncio.sleep(1)
            self.display.drawMeasurement("daswirdzulangseinseinsein", "20 cm")
            await asyncio.sleep(1)

    def get_async_loop(self):
        return self._async_loop

    async_loop = property(get_async_loop)


if __name__ == '__main__':
    main = Main()
    try:
        main.setup()
    except Exception as e:
        print("fail in main setup")
        raise

    gc.collect()
    print("Setup completed")
