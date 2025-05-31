import pyvisa
import re
from Oscilloscopes.scope_base import Scope
from tkinter import messagebox
import time


class SDS824XHD(Scope):
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
            messagebox.showerror('Error', 'The SDS824XHD is offline. Check power and connections. Then close and restart.')
        else:
            self.visa_session.timeout = 5000
            self.visa_session.write('*RST')

            # todo check - does not support *tst?
            #test = self.visa_session.query('*TST?')
            #assert test == '0', f"Initial test return fail: {test}"

            self.mode = None
            self.status = None
            self.result = None

    def reset(self):
        self.visa_session.write('*RST')
        self.visa_session.write('DISP:PERS OFF')

    def idn(self):
        # \r\n
        # model no, 12 char serial no, firmware version
        return self.visa_session.query('*IDN?')

    def set_chan_state(self, chan, state):
        # aka switch
        # chan here is a single digit number
        self.visa_session.write(f'CHAN{chan}:SWIT {state}')

    def set_chan_unit(self, chan, unit):
        # V, A
        self.visa_session.write(f'CHAN{chan}:UNIT {unit}')


    def set_chan_probe(self, chan, scale):
        # chan here is a single digit number
        self.visa_session.write(f'CHAN{chan}:PROB VAL,{scale}')

    def set_chan_scale(self, chan, scale):
        #
        # chan here is a single digit number
        self.visa_session.write(f'CHAN{chan}:SCAL {scale}')

    def set_chan_position(self, chan, position):
        # aka offset - here its position * scale
        # chan here is a single digit number
        # read scale
        scale = self.visa_session.query(f'CHAN{chan}:SCAL?')
        time.sleep(0.1)
        self.visa_session.write(f'CHAN{chan}:OFFSET {position * float(scale)}')
        #print(f'CHAN{chan}:OFFSET: {self.visa_session.query(f'CHAN{chan}:OFFSET?')}')

    def set_chan_aquisition_type(self, chan, type):
        # SAMPLE
        # chan here is a single digit number
        self.visa_session.write(f'CHAN{chan}:TYPE {type}')

    def set_chan_bandwidth(self, chan, bandwidth):
        # FULL, 20M, 200M
        # chan here is a single digit number
        if bandwidth == "B20":
            bandwidth = "20M"
        self.visa_session.write(f'CHAN{chan}:BWL {bandwidth}')

    def set_chan_coupling(self, chan, coupling):
        # DC, AC, GND
        # chan here is a single digit number
        self.visa_session.write(f'CHAN{chan}:COUP {coupling}')

    def set_chan_impedance(self, chan, impedance):
        # ONEMeg, FIFTy
        # chan here is a single digit number
        if impedance.upper() == "MEG":
            impedance = 'ONEMEG'
        self.visa_session.write(f'CHAN{chan}:IMP {impedance.upper()}')

    def set_trigger_mode(self, mode):
        # NORM,
        self.visa_session.write(f'TRIG:MODE {mode}')

    def set_trigger_type(self, type):
        # EDGE,
        self.visa_session.write(f'TRIG:TYPE {type}')

    def set_trigger_source(self, chan):
        #C1, C2, C3, C4
        # chan here is a single digit number
        self.visa_session.write(f'TRIG:EDGE:SOUR C{chan}')

    def set_trigger_level(self, level):
        # voltafe
        self.visa_session.write(f'TRIG:EDGE:LEV {level}')

    def set_trigger_coupling(self, coupling):
        # AC, DC
        self.visa_session.write(f'TRIG:EDGE:COUP {coupling}')

    def set_trigger_edge_coupling(self, coupling):
        # DC, AC
        self.visa_session.write(f'TRIG:EDGE:COUPLING {coupling}')

    def set_trigger_edge(self, slope):
        # RISE,
        self.visa_session.write(f'TRIG:EDGE:SLOPE {slope}')

    def set_aquire_stopafter(self, stop):
        # do not remove
        #self.visa_session.write(f'{stop}')
        pass

    def set_aquire_state(self, state):
        # do not remove
        #self.visa_session.write(f'{state}')
        pass

    def set_acquisition_type(self, type):
        # NORM
        self.visa_session.write(f'ACQUIRE:TYPE {type}')

    def set_timebase_scale(self, scale):
        #
        self.visa_session.write(f'TIM:SCAL {scale}')

    def set_timebase_delay(self, delay):
        #
        self.visa_session.write(f'TIM:DEL {delay}')

    def set_timebase_reference(self, reference):
        # DEL, POS
        self.visa_session.write(f'TIM:REF {reference}')

    def set_reference_position(self, position):
        # percent of horizontal scale
        self.visa_session.write(f'TIM:REF:POS {position}')

    def set_timebase_position(self, position):
        # combine commands
        self.set_timebase_reference('POS')
        self.set_reference_position(position)

    def set_meas_system(self, state):
        # on, off
        self.visa_session.write(f'MEAS {state}')
        self.visa_session.write(f'MEAS:MODE ADV')

    def set_meas_type(self, num, type):
        # PKPK,MAX,MIN,TOP,MEAN,DUTY,WID,PER,etc
        self.visa_session.write(f'MEAS:ADV:P{num}:TYPE {type}')

    def set_meas_source(self, num, chan):
        # C1,C2,C3,C4, others
        # chan here is a single digit number
        self.visa_session.write(f'MEAS:ADV:P{num}:SOUR C{chan}')

    def set_meas_state(self, num, state):
        # ON,OFF
        self.visa_session.write(f'MEAS:ADV:P{num} {state}')

    def get_meas_value(self, num):
        # get the value
        return self.visa_session.query(f'MEAS:ADV:P{num}:VAL?')