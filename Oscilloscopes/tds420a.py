import pyvisa
import re
from scope_base import Scope
from tkinter import messagebox


class TDS420A(Scope):
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
            self.visa_session.timeout = 1000
            self.visa_session.read_termination = '\r\n'
            self.visa_session.write_termination = '\n'
            # try sending query
            self.visa_session.query('*IDN?')
            print(self.idn())
        except Exception as e:
            print('oscilloscope offline.', e)
            # messagebox to indicate error
            messagebox.showerror('Error', 'The TDS420A is offline. Check power and connections. Then close and restart.')
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

    def set_chan_state(self, chan, state):
        # ON, OFF
        self.visa_session.write(f'SELECT:CH{chan} {state}')

    def set_chan_scale(self, chan, scale):
        #
        self.visa_session.write(f'CH{chan}:SCALE {scale}')

    def set_chan_position(self, chan, position):
        #
        self.visa_session.write(f'CH{chan}:POSITION {position}')

    def set_chan_bandwidth(self, chan, bandwidth):
        # common -> FULL, 20M, 200M
        # tek ->  FULL, TWENTY
        if bandwidth.upper() == "20M":
            bandwidth = "TWENTY"
        self.visa_session.write(f'CH{chan}:BANDWIDTH {bandwidth}')

    def set_chan_coupling(self, chan, coupling):
        #
        self.visa_session.write(f'CH{chan}:COUPLING {coupling}')

    def set_chan_impedance(self, chan, impedance):
        # MEG, FIFTY
        # chan here is a single digit number
        self.visa_session.write(f'CH{chan}:IMPEDANCE {impedance.upper()}')

    def set_trigger_mode(self, mode):
        #
        self.visa_session.write(f'TRIGGER:MAIN:MODE {mode}')

    def set_trigger_type(self, type):
        # do not remove
        #self.visa_session.write(f'')
        pass

    def set_trigger_source(self, chan):
        #
        self.visa_session.write(f'TRIGGER:MAIN:EDGE:SOURCE CH{chan}')

    def set_trigger_level(self, level):
        #
        self.visa_session.write(f'TRIGGER:MAIN:LEVEL {level}')

    def set_trigger_coupling(self, coupling):
        #
        self.visa_session.write(f'TRIGGER:MAIN:EDGE:COUPLING {coupling}')

    def set_trigger_edge_slope(self, slope):
        # RISE,
        self.visa_session.write(f'TRIGGER:A:EDGE:SLOPE {slope}')

    def set_aquire_stopafter(self, stop):
        #
        self.visa_session.write(f'ACQUIRE:STOPAFTER {stop}')

    def set_aquire_state(self, state):
        #
        self.visa_session.write(f'ACQUIRE:STATE {state}')

    def set_aquisition_type(self, type):
        # NORM=SAMPLE
        if type == "NORM":
            type = "SAMPLE"
        self.visa_session.write(f'ACQUIRE:MODE {type}')

    def set_timebase_scale(self, scale):
        #
        self.visa_session.write(f'HORIZONTAL:MAIN:SCALE {scale}')

    def set_timebase_delay(self, delay):
        # do not remove
        # self.visa_session.write()
        pass

    def set_timebase_reference(self, reference):
        # do not remove
        # self.visa_session.write()
        pass

    def set_timebase_position(self, position):
        # percent of screen
        self.visa_session.write(f'HORIZONTAL:TRIGGER:POSITION {position}')

    def set_meas_system(self, state):
        # do not remove
        #self.visa_session.write()
        pass

    def set_meas_type(self, num, type):
        #
        self.visa_session.write(f'MEAS:MEAS{num}:TYPE {type}')

    def set_meas_source(self, num, chan):
        #
        self.visa_session.write(f'MEAS:MEAS{num}:SOURCE CH{chan}')

    def set_meas_state(self, num, state):
        #
        self.visa_session.write(f'MEAS:MEAS{num}:STATE {state}')


    def get_meas_value(self, num):
        # get the value
        return self.visa_session.query(f'MEASU:MEAS{chan}:VAL?')