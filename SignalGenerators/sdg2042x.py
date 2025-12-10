import pyvisa
import re
from SignalGenerators.signal_gen_base import SignalGenerator
from tkinter import messagebox


class SDG2042X(SignalGenerator):
    """
    This only uses channel 1

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
            self.visa_session.read_termination = '\n'
            self.visa_session.write_termination = '\n'
            # try sending query
            self.visa_session.query('*IDN?')
            print(self.idn())
        except Exception as e:
            print('meter offline.', e)
            # messagebox to indicate error
            messagebox.showerror('Error', 'The SDG2042X is offline. Check power and connections. Then close and restart.')
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

    def set_output_state(self, state):
        # on, off
        self.visa_session.write(f"C1:OUTP {state.upper()}")

    def set_waveform_type(self, type):
        # sine, square, ramp, pulse, noise, arb, dc, prbs, iq
        self.visa_session.write(f"C1:BSWV WVTP, {type.upper()}")

    def set_frequency(self, frequency):
        # Hz
        self.visa_session.write(f"C1:BSWV FRQ, {frequency}")

    def set_period(self, period):
        #
        self.visa_session.write(f"C1:BSWV PERI, {period}")

    def set_duty(self, duty):
        # 0-100%
        self.visa_session.write(f"C1:BSWV DUTY, {duty}")

    def set_pulse_width(self, width):
        #
        self.visa_session.write(f"C1:BSWV WIDTH, {width}")

    def set_amplitude(self, amplitude):
        #
        self.visa_session.write(f"C1:BSWV AMP,{amplitude}V")

    def set_offset(self, offset):
        #
        self.visa_session.write(f"C1:BSWV OFST,{offset}V")

    def set_high_level(self, level):
        #
        self.visa_session.write(f"C1:BSWV HLEV,{level}V")

    def set_low_level(self, level):
        #
        self.visa_session.write(f"C1:BSWV LLEV,{level}V")

    def set_output_impedance(self, impedance):
        # 50, HZ
        self.visa_session.write(f"C1:OUTPUT LOAD, {impedance}")

    def set_output_invert(self, state):
        # ON, OFF
        self.visa_session.write(f"C1:INVT {state}")