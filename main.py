# -*- coding:utf-8 -*-
import gc
import uasyncio as asyncio
from controller.DatacollectorController import DatacollectorController

gc.collect()


class Main:
    def __init__(self):
        self._async_loop = asyncio.get_event_loop()
        self._datacollector_controller = DatacollectorController(self)

    def setup(self):
        self._datacollector_controller.setup()
        self._async_loop.run_until_complete(self.main())

    async def main(self):
        while True:
            await asyncio.sleep(1)

    def get_async_loop(self):
        return self._async_loop

    async_loop = property(get_async_loop)


if __name__ == '__main__':
    main = Main()
    main.setup()
