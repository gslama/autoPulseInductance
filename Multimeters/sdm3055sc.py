import pyvisa
import re
from Multimeters.meter_base import Meter
from tkinter import messagebox
import time


class SDM3055SC(Meter):
    """
    Siglent dmm meter with 16 channel scanner card

    """

    def __init__(self, port):
        # gets full port name
        rm = pyvisa.ResourceManager()
        #print(rm.list_resources())

        #if 'COM' in port:
        #    port = port.split('COM')[1]
        # cannot assume serial
        #self.visa_session = rm.open_resource(f'ASRL{port}::INSTR')

        # supports RS232 up to 115200 baud, 8 bit, 1 stop, no parity
        # supports USB at 115200 baud

        # todo because using a usb to serial convertor, cannot detect instrument is off this way
        # todo port shows and responses but cannot send or receive commands
        try:
            self.visa_session = rm.open_resource(port)
            self.visa_session.timeout = 1000
            self.visa_session.read_termination = '\r\n'
            self.visa_session.write_termination = '\n'
            # try sending query
            self.visa_session.query('*IDN?')
            print(self.idn())
        except Exception as e:
            print('hipot meter offline.', e)
            # messagebox to indicate error
            messagebox.showerror('Error', 'The SDM3055-SC is offline. Check power and connections. Then close and restart.')
        else:
            self.visa_session.timeout = 5000
            self.visa_session.write('*CLS')

            # todo check - does not support *tst?
            #test = self.visa_session.query('*TST?')
            #assert test == '0', f"Initial test return fail: {test}"

            self.mode = None
            self.status = None
            self.result = None

    def reset(self):
        self.visa_session.write('*RST')
        # wait
        #self.visa_session.write('ROUT:SCAN ON')
        return

    def idn(self):
        # ,\r\n
        # model no, 12 char serial no, firmware version
        return self.visa_session.query('*IDN?')

    def get_measurement(self, chan):
        # gets data after scan
        # clean up data, ie '+2.12468981E+01 C,\n'
        reading = self.visa_session.query(f'ROUT:DATA? {chan}')
        data = reading.strip().split()[0].replace(',', '')
        print(f'get_measurement reading: {reading} data: {data}')
        return data

    def set_temp_chan(self, chan, type):
        # channel value includes slot which needs to be removed
        chan = chan % 100
        # chan = 1 to 12
        # type assumed to be thermocouple
        # type (BITS90|EITS90|JITS90|KITS90|NITS90|RITS90|SITS90|TITS90)
        if type == 'J':
            type = "JITS90"
        elif type == 'K':
            type = "KITS90"
        elif type == 'T':
            type = "TITS90"

        #self.visa_session.write(f"conf:temp tc,{type},(@{chan})")
        #self.visa_session.query(f'MEAS:TEMP? THER,{type}ITS90')
        self.visa_session.write(f"ROUT:CHAN {chan},ON,TEMP")
        self.visa_session.write(f"ROUT:TEMP:THER {type}")

    def set_volt_chan(self, slot, chan, type):
        # channel value includes slot which needs to be removed
        chan = chan % 100
        # chan = 1 to 12
        #self.visa_session.write(f"conf:volt:{type} (@{chan})")
        #self.visa_session.query(f'MEAS:VOLT:DC?')
        self.visa_session.write(f"ROUT:CHAN {chan},ON,DCV,20V,FAST")

    def set_message(self, message):
        # do not remove
        # does not have function
        pass

    def get_card_type(self, slot):
        # do not remove
        # does not have function
        pass

    def get_scan_state(self):
        #
        return self.visa_session.query('ROUT:STAT?')

    def set_scan_state(self, state):
        # ON, OFF
        self.visa_session.write(f'ROUT:SCAN {state}')

    def set_chan_config(self, chan, state="ON",mode="DCV", range="AUTO", speed="FAST"):
        # chan: 1...15
        # state: ON, OFF
        # mode: DCV,DCI,ACV,ACI,2W,4W,CAP,FRQ,CONT,DIO,TEMP
        # range:
        # speed: SLOW, FAST
        self.visa_session.write(f'ROUT:CHAN {chan},{state},{mode},{range},{speed}')

    def set_scan_range(self, low, high):
        # range 1...16
        self.visa_session.write(f'ROUT:LIMIT:HIGH {high}')
        time.sleep(0.1)
        self.visa_session.write(f'ROUT:LIMIT:LOW {low}')

    def set_scan_count(self, cycles):
        # number of scan cycles
        self.visa_session.write(f'ROUT:COUN {cycles}')

    def set_scan_active(self, state):
        # enable scan card
        # ON, OFF, 1, 0
        self.visa_session.write(f'ROUT:START {state}')

    def get_chan_temperature(self, chan):
        # test sequence to get a reading
        #self.set_scan_state('ON')
        self.set_scan_range(chan, chan)
        self.set_scan_count(1)
        #self.set_temp_chan(chan, 'T')
        self.set_scan_active('ON')
        time.sleep(3)
        return self.get_measurement(chan)

    def get_meas_temp(self, chan, type):
        # meter temperature function
        # chan is ignored
        # type (BITS90|EITS90|JITS90|KITS90|NITS90|RITS90|SITS90|TITS90)
        if type == 'J':
            type = "JITS90"
        elif type == 'K':
            type = "KITS90"
        elif type == 'T':
            type = "TITS90"
        reading = float(self.visa_session.query(f'MEAS:TEMP? THER,{type}'))
        #print(f'get_meas_temp: {reading}')
        return reading