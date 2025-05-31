import pyvisa
import re
from scope_base import Scope
from tkinter import messagebox


class RTB2004(Scope):
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
            messagebox.showerror('Error', 'The RTB2004 is offline. Check power and connections. Then close and restart.')
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
        # on, off
        self.visa_session.write(f'CHAN{chan}:STATE {state.upper()}')

    def set_chan_probe(self, chan, scale):
        # probe attenuation, i.e. 1, 10, 100
        # chan here is a single digit number
        self.visa_session.write(f'PROBE{chan}:SETUP:ATT:MAN {scale}')

    def set_chan_scale(self, chan, scale):
        #
        self.visa_session.write(f'CHAN{chan}:SCALE {scale}')

    def set_chan_position(self, chan, position):
        # vertical position of waveform by divisions
        # range -5 to 5
        self.visa_session.write(f'CHAN{chan}:POSITION {position}')

    def set_chan_bandwidth(self, chan, bandwidth):
        # common -> FULL, 20M, 200M
        # RS -> FULL, B20
        if bandwidth.upper() == "20M":
            bandwidth = "B20"
        self.visa_session.write(f'CHAN{chan}:BANDWIDTH {bandwidth}')

    def set_chan_coupling(self, chan, coupling):
        # DCLIMIT, ACLIMIT, GND
        if coupling.upper() == "DC":
            coupling = "DCLIMIT"
        elif coupling.upper() == "AC":
            coupling = "ACLIMIT"
        else:
            coupling = coupling.upper()
        self.visa_session.write(f'CHAN{chan}:COUPING {coupling}')

    def set_chan_impedance(self, chan, impedance):
        # this scope only has 1 MEG inputs
        if impedance.upper() == 'FIFTY':
            # needs a feed through
            messagebox.showerror('Warning', f'Channel {chan} needs an external fifty ohm termination.')

    def set_trigger_mode(self, mode):
        # NORMAL, AUTO
        self.visa_session.write(f'TRIGGER:A:MODE {mode}')

    def set_trigger_source(self, chan):
        # CH1, CH2, CH3, CH4
        # chan here is a single digit number
        self.visa_session.write(f'TRIGGER:A:SOURCE CH{chan}')

    def set_trigger_type(self, type):
        #
        self.visa_session.write(f'')

    def set_trigger_level(self, level):
        #
        self.visa_session.write(f'TRIGGER:A:LEVEL {level}')

    def set_trigger_edge_coupling(self, coupling):
        # DC, AC
        self.visa_session.write(f'TRIGGER:A:EDGE:COUPLING {coupling}')

    def set_trigger_edge_slope(self, slope):
        # POSITIVE=RISE, NEGATIVE
        if slope.upper() == "RISE":
            slope = "POSITIVE"
        self.visa_session.write(f'TRIGGER:A:EDGE:SLOPE {slope}')

    def set_aquisition_type(self, type):
        # SAMPLE
        #self.visa_session.write(f'{type}')
        pass

    def set_timebase_scale(self, scale):
        #
        self.visa_session.write(f'TIMEBASE:SCALE {scale}')

    def set_timebase_position(self, position):
        #
        self.visa_session.write(f'TIMEBASE:REFERENCE {position}')

    def set_meas_system(self, state):
        # do not remove
        pass

    def set_meas_mode(self, type):
        # do not remove
        pass

    def set_meas_type(self, num, type):
        # UPE=MAX (upper peak value)
        if type.upper() == "MAX":
            type = "UPE"
        self.visa_session.write(f'MEAS{num}:MAIN {type}')

    def set_meas_source(self, num, chan):
        # CH1,CH2,CH3,CH4,MA1,RE1,RE2,RE3,RE4,D0...D15
        # chan here is a single digit number
        self.visa_session.write(f'MEAS{num}:SOURCE CH{chan}')

    def set_meas_state(self, num, state):
        # ON, OFF
        self.visa_session.write(f'MEAS{num}:ENABLE {state}')

    def get_meas_value(self, num):
        # get the value
        return self.visa_session.query(f'MEAS{num}:RESult:ACTual?')