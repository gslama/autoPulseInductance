from abc import ABC, abstractmethod

class Meter(ABC):

    def factory(name, port):
        if name == "SDM3055":
            from Multimeters.sdm3055 import SDM3055
            return SDM3055(port)
        elif name == "HP34401A":
            from Multimeters.hp34401a import HP34401A
            return HP34401A(port)
        elif name == "USB2001TC":
            from Multimeters.usb2001tc import USB2001TC
            return USB2001TC(port)

    def idn(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def set_temp_chan(self, card, chan, type):
        raise NotImplementedError

    def set_volt_chan(self, card, chan, type):
        raise NotImplementedError

    def set_message(self, message):
        raise NotImplementedError

    def get_measurement(self):
        raise NotImplementedError

    def get_card_type(self):
        raise NotImplementedError