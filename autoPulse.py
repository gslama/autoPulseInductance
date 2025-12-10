# autoPulseInductance

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# preferred use is 'import module' or 'from module import functions'
# requires prefixing functions with module name as in module.function()

import os
import sys
import ctypes

import json
import mainView
import tkinter as tk
from tkinter import ttk, messagebox, font
import globals as gb  # loads init files

from Oscilloscopes.scope_base import Scope
from SignalGenerators.signal_gen_base import SignalGenerator
from PowerSupplies.power_supply_base import PowerSupply
from Multimeters.meter_base import Meter

"""
the app                 
reads init file and calls main window
"""

# todo remove
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# command line options
if '--show-console' not in sys.argv:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# define window
root = tk.Tk()
root.title("AutoPulseInductance")
#root.iconbitmap(resource_path('oscilloscope.ico'))
root.geometry("800x400+200+200")
root.resizable(width=False, height=False)

# define colors
button_font = ('SimSun', 10, 'bold')
button_color = '0c0c0c'
root_color = '#778899'
text_color ='#f8f8f8'
frame_color = '#dcdcdc'
#root.config(bg=root_color)

# load instruments
gb.scope = Scope.factory(gb.initValues.scopeMeter, gb.initValues.scopeAdr)
gb.sig_gen = SignalGenerator.factory(gb.initValues.sigGen, gb.initValues.sigGenAdr)
gb.meter = Meter.factory(gb.initValues.meterUnit, gb.initValues.meterAdr)
gb.power = PowerSupply.factory(gb.initValues.powerUnit, gb.initValues.powerAdr)

# create an instance of input view
mainview = mainView.outputView(root)
#mainview.config(bg=root_color)

# place input view frame
mainview.grid(sticky=(tk.E + tk.W + tk.N + tk.S))
# inputView(self).grid(sticky=(tk.E + tk.W + tk.N + tk.S))
mainview.columnconfigure(0, weight=1)


if __name__ == '__main__':
    root.mainloop()
