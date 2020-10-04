# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 08:49:35 2019

@author: GFI
"""
import time
import asyncio
import logging
#from solar2.charge import ChargeEV
from solar2.definitions.logger_config import FILEHANDLER, Filter


NAME = 'solar2'
logger = logging.getLogger(NAME)
logger.setLevel(logging.DEBUG)
logger.addHandler(FILEHANDLER)
FILTER = Filter(NAME)
logger.addFilter(FILTER)

__version__ = '1.0.0'


class SolarStatus():
    def __init__(self, sleeptime=1):
        self._state = True
        self._sleeptime = sleeptime

    async def state_change(self):
        await asyncio.sleep(self)
        self._state = not self._state

    async def state(self):
        return self._state


class CarStatus():
    def __init__(self, sleeptime=1):
        self._state = True
        self._sleeptime = sleeptime

    async def state_change(self):
        await asyncio.sleep(self._sleeptime)
        self._state = not self._state

    async def state(self):
        return self._state


async all_tasks():
    solarstatus = SolarStatus()
    results = await asyncio.gather(solarstatus.state_change(),
    main())


async def main():
    stime = time.time()

    while time.time() - stime < 5:
        await asyncio.sleep(.5)
        print(solarstatus._state)
        print('aaa')
        print(tasks)

    for task in tasks:
        print(task)
        task.cancel()


if __name__ == '__main__':
    print(f'main v{__version__}')
#    loggerDict = logging.root.manager.loggerDict
#    loggers = [name for name in loggerDict if 'solar' in name]
#    logger.critical(loggers)
    # ev.run()
    print(res)
    asyncio.run(main_loop())
