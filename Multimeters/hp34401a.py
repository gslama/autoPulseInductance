import pyvisa
from Multimeters.meter_base import Meter
from tkinter import messagebox


class HP34401A(Meter):
    """
    the classic hp34401a multimeter 6-1/2 digits
    original uses gpib or rs-232

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
            print('meter offline.', e)
            # messagebox to indicate error
            messagebox.showerror('Error', 'The HP34401A is offline. Check power and connections. Then close and restart.')
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

    def config_meas(self, type, range = 'AUTO'):
        # measure a voltage
        # type = ac, dc
        # range = 0.1, 1, 10, 100, 1000, auto default
        if range == 'AUTO':
            range = ""
        self.visa_session.write(f'CONF:VOLT{type} {range}')

    def get_measurement(self):
        # initiate and get reading
        return self.visa_session.query("READ?")

    def set_volt_chan(self, type):
        # type = ac, dc
        self.visa_session.write(f"conf:volt:{type}")

    def set_message(self, message):
        # limited to 13 characters, A-Z, 0-9,
        self.visa_session.write(f"disp:text '{message}'")

