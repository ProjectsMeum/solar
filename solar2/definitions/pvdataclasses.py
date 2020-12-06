# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Module containing different dataclasses with some default values.
Default values can be adapted to specific requirements.

"""
import os
import asyncio
import json
import logging
from functools import cached_property
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta
from .access_data import HOME, E3DC_IP

__version__ = '1.0.2'
print(f'pvdataclasses.py v{__version__}')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@dataclass(frozen=False)
class PVStatus():
    '''Class to store state variables of PV system'''

    dtime: datetime = 0
    pv: int = 0
    pv1: int = 0
    pv2: int = 0
    soc: int = 0
    netz: int = 0
    akku: int = 0
    haus: int = 0
    ok: bool = False

    def __post_init__(self):
        '''initialize PVStatus'''
        self.pv = self.pv1 + self.pv2


@dataclass(frozen=False)
class Values():
    '''
    Trigger change only if state change is stable over all values

    maxlength of deque determines the how many times conditions must be met
    before triggering start or stop charging
    '''

    maxlength = 5
    values: deque = field(default=deque([False] * maxlength, maxlength))

    def __post_init__(self):
        '''Initialize empty value deque'''
        self.values = self.values.copy()

    def alltrue(self):
        '''Return True if all fields True'''
        return all(self.values)

    def allfalse(self):
        '''Return False if all fields False'''
        return not any(self.values)

    def anytrue(self):
        '''Return True if any value is True'''
        return any(self.values)


@dataclass(frozen=False)
class ChargeConfig():
    '''Values and variables for system charging'''

    _defaults_path: str = 'solar2/definitions/'
    _defaults_file: str = 'newdefaults.json'
    _fname: str = 'PV2_%Y_%m_%d.csv'
    _path: str = 'solar2/data/'
    _st_mtime: float = 0
    _check_update_time: int = 10
    keep_alive: bool = False
    _log_to_file: bool = True
    soc_minimum_start: float = 20
    soc_minimum_stop: float = 20
    charge_state: bool = False
    old_netz_status: bool = False
    check_intervall: int = 60
    state: PVStatus = PVStatus()
    evathome_distance: float = 200  # in meter
    netz_vals: Values = Values()
    coll_vals: Values = Values()
    check_internet_timeout = 300  # in seconds
    e3dc_time_last_connection: float = 0
    e3dc_error_minimum_time: float = 15 * 60  # in seconds

    __version__: str = '0'

    def __post_init__(self):
        try:
            loop = asyncio.get_running_loop()
            assert loop.is_running()
        except RuntimeError:
            logger.info('No running eventloop')
        else:
            self.keep_alive = True
            logger.info('ChargeConfig.check_updates started')
            task = asyncio.create_task(self.check_updates(),
                                       name='DefaultsValuesUpdates')


    @cached_property
    def fname(self):
        fname = ''.join([self._defaults_path, self._defaults_file])
        return os.path.normpath(fname)

    async def check_updates(self):
        while self.keep_alive:
            self._update_default_values()
            await asyncio.sleep(self.check_intervall)

    def _update_default_values(self) -> None:
        '''
        Read updated values if available
        '''
        try:
            assert os.stat(self.fname).st_mtime != self._st_mtime
            print('assert ok')
            self._st_mtime = os.stat(self.fname).st_mtime
            with open(self.fname, 'rb') as file:
                new_values = json.loads(file.read())
            # update charge defaults
            charge_keys = set(self.__dict__.keys()) & set(new_values.keys())
            for key in charge_keys:
                setattr(self, key, new_values[key])
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning('FileNotFoundError: %s', fname)
            print('FileNotFound')
        except AssertionError as err:
            print('unchanged', err)
            pass # file not changed
        except Exception as err:
            print('critical')
            logger.critical(err, exc_info=True)
            raise


@dataclass(frozen=False)
class ModbusDefaults():
    '''E3DC IP address, collect intervall and data fields to retain.'''

    _tcp_ip: str = E3DC_IP
    keys: list = field(default_factory=list)

    def __post_init__(self):
        '''defines values to keep'''
        self.keys = [40068, 40076, 40070, 40074, 40072, 40083, 40082]
        self.keys = [40036, 40052, 40068, 40076, 40070, 40074, 40072,
                     40083, 40082, 40084]


@dataclass(frozen=False)
class CarDefaults():
    '''Values and variables for system driving'''

    home: tuple
    _defaults_last_update: datetime = datetime(2019, 1, 1, 8, 0)
    _defaults_update_intervall: timedelta = timedelta(seconds=120)
    _athome_km: float = 0.200  # in kilometer
    _km2seconds_factor: float = 60
    seconds_btw_updates: int = 5 * 60
    ev_trials: int = 5
    evsoc_std: int = 70
    evsoc_limit_low: int = 80
    evstart_power_low: int = -3000
    evstop_power_low: int = 6000
    evsoc_limit_high: int = 90
    evstart_power_high: int = -7000
    evstop_power_high: int = 5000
    fname_charging_status: str = 'solar/data/charging_flag.csv'
    last_charge_limit_soc: int = 0
    charging_flag: bool = False
    sleep_between_func: int = 1
    __version__: str = ''


@dataclass(frozen=False)
class CarData(CarDefaults):
    '''State values of car'''

    timestamp: int = 0
    battery_level: int = 0
    charge_limit_soc: int = 0
    charge_limit_soc_max: int = 100
    charge_limit_soc_min: int = 50
    charge_limit_soc_std: int = 0
    charge_port_latch: str = ''
    charging_state: str = ''
    display_name: str = ''
    gps_as_of: int = 0
    latitude: float = 0
    longitude: float = 0
    native_latitude: float = 0
    native_longitude: float = 0
    odometer: float = 0
    power: int = 0
    shift_state: str = ''
    speed: float = 0
    state: str = ''
    time_to_full_charge: float = 0
    timestamp: int = 0
    vehicle_id: int = 0
    vin: str = ''
    data_ok: bool = False


    @property
    def location(self):
        '''Tuple with location'''
        return (self.latitude, self.longitude)

    @property
    def charging(self):
        '''True if car is charging'''
        return self.charging_state == 'Charging'


if __name__ == '__main__':
    p = PVStatus()
    v = Values()
    d = ChargeDefaults()
    m = ModbusDefaults()
    c = CarData(HOME)
    cd = CarDefaults(HOME)
    cd._defaults_update_intervall = timedelta(seconds=1)
    cd.defaults_update_values()
