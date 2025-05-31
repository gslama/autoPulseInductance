from abc import ABC, abstractmethod

class Scope(ABC):

    def factory(name, port):
        if name == "SDS824XHD":
            from Oscilloscopes.sds824xhd import SDS824XHD
            return SDS824XHD(port)
        elif name == "TDS420A":
            from Oscilloscopes.tds420a import TDS420A
            return TDS420A(port)
        elif name == "RTB2004":
            from Oscilloscopes.rtb2004 import RTB2004
            return RTB2004(port)

    def idn(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def set_chan_state(self, chan, state):
        raise NotImplementedError

    def set_chan_probe(self, chan, scale):
        raise NotImplementedError

    def set_chan_scale(self, chan, scale):
        raise NotImplementedError

    def set_chan_position(self, chan, position):
        raise NotImplementedError

    def set_chan_bandwidth(self, chan, bandwidth):
        raise NotImplementedError

    def set_chan_coupling(self, chan, coupling):
        raise NotImplementedError

    def set_chan_impedance(self, chan, impedance):
        raise NotImplementedError

    def set_trigger_mode(self, mode):
        raise NotImplementedError

    def set_trigger_type(self, type):
        raise NotImplementedError

    def set_trigger_source(self, chan):
        raise NotImplementedError

    def set_trigger_level(self, level):
        raise NotImplementedError

    def set_trigger_slope(self, slope):
        raise NotImplementedError

    def set_trigger_coupling(self, coupling):
        raise NotImplementedError

    def set_trigger_edge(self, edge):
        raise NotImplementedError

    def set_aquire_stopafter(self, stop):
        raise NotImplementedError

    def set_aquire_state(self, state):
        raise NotImplementedError

    def set_acquisition_type(self, type):
        raise NotImplementedError

    def set_timebase_scale(self, scale):
        raise NotImplementedError

    def set_timebase_delay(self, delay):
        raise NotImplementedError

    def set_timebase_reference(self, reference):
        raise NotImplementedError

    def set_timebase_position(self, position):
        raise NotImplementedError

    def set_meas_system(self, state):
        raise NotImplementedError

    def set_meas_mode(self, type):
        raise NotImplementedError

    def set_meas_type(self, num, type):
        raise NotImplementedError

    def set_meas_source(self, num, chan):
        raise NotImplementedError

    def set_meas_state(self, num, state):
        raise NotImplementedError

    def get_meas_value(self, num):
        raise NotImplementedError

