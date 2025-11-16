
import re
from Thermometers.thermometer_base import Thermometer
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import DigitalPortType, ULRange, DigitalIODirection, TempScale
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import InterfaceType

from time import sleep
import time

import globals as gb


class USB2001TC(Thermometer):
    """
    This device uses a USB interface
    The device uses 'Instcal' to setup a board num and the thermocouple type.
    This device is single chan

    """

    def __init__(self, port):

        try:
            self.initMmcDaq(port)
        except Exception as e:
            print('thermometer offline.', e)
            # messagebox to indicate error
            messagebox.showerror('Error', 'The USB-2001-TC is offline. Check power and connections. Then close and restart.')
        else:
            # todo check - does not support *tst?
            #test = self.visa_session.query('*TST?')
            #assert test == '0', f"Initial test return fail: {test}"

            self.mode = None
            self.status = None
            self.result = None


    def get_measurement(self, boardNum, channel = 0):
        try:
            # Get temperature from the specified channel
            temp_c =  ul.t_in(boardNum, channel, TempScale.CELSIUS)
            #print(f"Temperature on channel {channel}: {temp_c:.2f} °C")
        except Exception as e:
            print(f"Error reading temperature: {e}")

        # return formatted
        return float(f"{temp_c:.2f}")

    """
    def set_temp_chan(self, chan, type):
        # chan = 1 to 16, 20, 40 depends on card
        # type = j, k, t,
        # create chan from slot number and chan

        self.visa_session.write(f"conf:temp tc,{type},(@{chan})")
    """

    def initMmcDaq(self, port):
        # By default, the example detects and displays all available devices and
        # selects the first device listed. Use the dev_id_list variable to filter
        # detected devices by device ID (see UL documentation for device IDs).
        # If use_device_detection is set to False, the board_num variable needs to
        # match the desired board number configured with Instacal.
        use_device_detection = True
        dev_id_list = []
        #boardNum = int(gb.initValues['thermoAdr']) #- doesn't work - not subscriptable
        boardNum = int(port)
        #boardNum = 1
        channel = 0

        try:
            if use_device_detection:
                self.config_first_detected_device(boardNum, dev_id_list)

            daq_dev_info = DaqDeviceInfo(boardNum)


            print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
                  daq_dev_info.unique_id, ')\n', sep='')

            dio_info = daq_dev_info.get_dio_info()

            try:
                # Get temperature from the specified channel
                temp_c = ul.t_in(boardNum, channel, TempScale.CELSIUS)

                print(f"Temperature on channel {channel}: {temp_c:.2f} °C")

            except Exception as e:
                print(f"Error reading temperature: {e}")

            # Flash the green pass LED

        except Exception as e:
            print('\n', e)
            return True


    def config_first_detected_device(self, board_num, dev_id_list=None):
        """Adds the first available device to the UL.  If a types_list is specified,
        the first available device in the types list will be add to the UL.

        Parameters
        ----------
        board_num : int
            The board number to assign to the board when configuring the device.

        dev_id_list : list[int], optional
            A list of product IDs used to filter the results. Default is None.
            See UL documentation for device IDs.
        """
        ul.ignore_instacal()
        devices = ul.get_daq_device_inventory(InterfaceType.ANY)
        if not devices:
            raise Exception('Exception Error: No DAQ devices found')

        print('Found', len(devices), 'DAQ device(s):')
        for device in devices:
            print('  ', device.product_name, ' (', device.unique_id, ') - ',
                  'Device ID = ', device.product_id, sep='')

        device = devices[0]
        if dev_id_list:
            device = next((device for device in devices
                           if device.product_id in dev_id_list), None)
            if not device:
                err_str = 'Error: No DAQ device found in device ID list: '
                err_str += ','.join(str(dev_id) for dev_id in dev_id_list)
                raise Exception(err_str)

        # Add the first DAQ device to the UL with the specified board number
        ul.create_daq_device(board_num, device)