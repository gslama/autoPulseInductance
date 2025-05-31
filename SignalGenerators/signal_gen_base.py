from abc import ABC, abstractmethod

class SignalGenerator(ABC):
    """
    This only uses one channel
    """

    def factory(name, port):
        if name == "HP8112A":
            from SignalGenerators.hp8112a import HP8112A
            return HP8112A(port)
        elif name == "SDG2042X":
            from SignalGenerators.sdg2042x import SDG2042X
            return SDG2042X(port)

    def idn(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def set_output_state(self, state):
        raise NotImplementedError

    def set_waveform_type(self, type):
        raise NotImplementedError

    def set_frequency(self, frequency):
        raise NotImplementedError

    def set_period(self, period):
        raise NotImplementedError

    def set_duty(self, duty):
        raise NotImplementedError

    def set_pulse_width(self, width):
        raise NotImplementedError

    def set_amplitude(self, amplitude):
        raise NotImplementedError

    def set_offset(self, offset):
        raise NotImplementedError

    def set_low_level(self, level):
        raise NotImplementedError

    def set_high_level(self, level):
        raise NotImplementedError

    def set_output_impedance(self, impedance):
        raise NotImplementedError