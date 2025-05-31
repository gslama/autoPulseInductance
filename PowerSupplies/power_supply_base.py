from abc import ABC, abstractmethod

class PowerSupply(ABC):

    def factory(name, port):
        if name == "SPD3033XE":
            from PowerSupplies.spd3033xe import SPD3033XE
            return SPD3033XE(port)
        elif name == "GPP4323":
            from PowerSupplies.gpp4323 import GPP4323
            return GPP4323(port)

    def idn(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def set_power_state(self, chan, state):
        raise NotImplementedError

    def set_voltage(self, chan, voltage):
        raise NotImplementedError

    def get_voltage(self, chan):
        raise NotImplementedError

    def set_current(self, chan, current):
        raise NotImplementedError

    def get_current(self, chan):
        raise NotImplementedError

    def set_over_voltage_protection(self, chan, voltage):
        raise NotImplementedError

    def set_over_current_protection(self, chan, current):
        raise NotImplementedError





