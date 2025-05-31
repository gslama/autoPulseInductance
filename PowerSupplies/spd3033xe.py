import pyvisa
import re
from PowerSupplies.power_supply_base import PowerSupply
from tkinter import messagebox


class SPD3033XE(PowerSupply):
    """
    dmm meter with 8 chan scanner card

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
            self.visa_session.timeout = 5000
            self.visa_session.read_termination = '\n'
            self.visa_session.write_termination = '\n'
            # try sending query
            self.visa_session.query('*IDN?')
            print(self.idn())
        except Exception as e:
            print('hipot meter offline.', e)
            # messagebox to indicate error
            messagebox.showerror('Error', 'The SPD3033XE is offline. Check power and connections. Then close and restart.')
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

    def idn(self):
        # ,\r\n
        # model no, 12 char serial no, firmware version
        return self.visa_session.query('*IDN?')

    def set_power_state(self, chan, state):
        # chan = CH1, CH2
        # state = on, off
        self.visa_session.write(f"OUTP CH{chan},{state.upper()}")

    def set_voltage(self, chan, voltage):
        self.visa_session.write(f"CH{chan}:VOLT {voltage}")

    def get_voltage(self, chan):
        # chan = CH1,CH2
        value = self.visa_session.query(f"MEAS:VOLT? CH{chan}")
        return float(value)

    def set_current(self, chan, current):
        self.visa_session.write(f"CH{chan}:CURR {current}")

    def get_current(self, chan):
        # chan = CH1,CH2
        value = self.visa_session.query(f"MEAS:CURR? CH{chan}")
        return float(value)

