# -*- coding:utf-8 -*-
import gc
import uasyncio as asyncio
from controller.DatacollectorController import DatacollectorController

class Main:
    def __init__(self):
        self._async_loop = asyncio.get_event_loop()
        self._datacollector_controller = DatacollectorController(self)

    def setup(self):
        self._datacollector_controller.setup()
        self._async_loop.run_until_complete(self.main())

    async def main(self):
        while True:
            print("doing nothing?")
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
        print(e)

    gc.collect()
    print("Setup completed")