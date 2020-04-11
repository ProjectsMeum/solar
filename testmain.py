# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 08:49:35 2019

@author: annet
"""
import logging
from solar.charge import ChargeEV
from solar.car import Car
from solar.definitions.logger_config import FILEHANDLER, Filter
from solar.definitions.access_data import EMAIL, PW, VIN, HOME

NAME = 'solar'
logger = logging.getLogger(NAME)
logger.setLevel(logging.DEBUG)
logger.addHandler(FILEHANDLER)
FILTER = Filter(NAME)
logger.addFilter(FILTER)


__version__ = 'x.x.x'

if __name__ == '__main__':
    print(f'main v{__version__}')
    car = Car(EMAIL, PW, VIN, HOME)
    # car.update_car_if()
    # ev = ChargeEV()
    # loggerDict = logging.root.manager.loggerDict
    # loggers = [name for name in loggerDict if 'solar' in name]
    # logger.critical(loggers)
    # ev.run()
