from abc import ABC, abstractmethod

class Thermometer(ABC):

    def factory(name, port):
        if name == "USB2001TC":
            from Thermometers.usb2001tc import USB2001TC
            return USB2001TC(port)
        elif name == "SDM3055":
            from Thermometers.sdm3055 import SDM3055
            return SDM3055(port)

    def idn(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def set_temp_chan(self, card, chan, type):
        raise NotImplementedError

    def get_measurement(self):
        raise NotImplementedError

