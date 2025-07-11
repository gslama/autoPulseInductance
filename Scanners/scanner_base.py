from abc import ABC, abstractmethod

class Scanner(ABC):

    def factory(name, port):
        if name == "SDM3055SC":
            from Scanners.sdm3055sc import SDM3055SC
            return SDM3055SC(port)
        elif name == "HP34970A":
            from Scanners.hp34970a import HP34970A
            return HP34970A(port)

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
        raise NotImplemented