"""
InstrumentInterface
    All functions related to talking to test instruments

"""
import time
import pyvisa
from pyvisa.errors import VisaIOError
from time import sleep
from tkinter import messagebox
import globals as gb


global calFlag

# this code runs at startup
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print('pyVisa resources online: ', resources)

def get_resource_manager():
    return pyvisa.ResourceManager()

def list_resources(resources):
    # Loop through each resource and try to query *IDN?
    for resource in resources:
        try:
            # Open the resource
            instr = rm.open_resource(resource)
            # Query the *IDN? command to get instrument identification
            idn = instr.query("*IDN?")
            print(f"Resource: {resource}, IDN: {idn}")
            instr.close()
        except Exception as e:
            print(f"Could not query {resource}: {e}")


def initGpib():
    """
    initilaize anything with GPIB
    should get connected instrument list
    reset each instrument
    *RST; *CLS; *OPC?
    SYST:ERR?
    SYST:SERR?

    :return:
    """
    # this should be global to the module
    global rm

    #rm = pyvisa.ResourceManager()
    #resources = rm.list_resources()
    #print('pyVisa resources online: ', resources)

def getInstrumentIdn(instrAdr):
    """
    get instrument identification string

    Parameters
        instrAdr: str
            instrAdr needs to be full visa string 'GPIB0::5::INSTR'
    Returns
        identification string from instrument
    """

    try:
        instr = rm.open_resource(instrAdr, read_termination='\n')
        #instr.timeout = 5000
    except Exception as e:
        print('instrument IDN: ' + instrAdr + '  offline, ', e)
        return True
    else:
        instrStatus = instr.query('*IDN?')
        print(instrStatus)
        instr.close()
    return


def getHipotIdn(instrAdr):
    """
    get hipot identification by reading screen
    does not support *IDN? query
    initial turn on screen of instrument give name, model, version
    Parameters
        instrAdr: str
            instrAdr needs to be full visa string 'GPIB0::5::INSTR'
    Returns
        identification string from instrument
    """

    try:
        instr = rm.open_resource(instrAdr, read_termination='\n')
        #instr.timeout = 5000
    except Exception as e:
        print(f'instrument: {instrAdr} offline, {e}')
        return True
    else:
        instrStatus = instr.query('?K')
        print(f'IDN: {instrStatus}')
        # instrRead = (instr.query('READ?'))
        instr.close()
    return

def scpiSend(instrAdr, command):
    """
    sends commands string to instrument

    parameters
        instrAdr: str
            instrAdr needs to be full visa string 'GPIB0::5::INSTR'
        command: str
            command string
    returns
        nothing
    """

    try:
        instr = rm.open_resource(instrAdr)
    except VisaIOError as e:
        print('instrument ' + instrAdr + '  offline, ',e)
    else:
        instrStatus = instr.write(command)
        #if print(instrStatus):
        instr.close()
    return

def scpiRead(instrAdr, reading):
    """
    instrAdr needs to be full visa string 'GPIB0::5::INSTR'

    parameters
        instrAdr:
        reading:
    returns
    """

    try:
        instr = rm.open_resource(instrAdr)
    except Exception as e:
        print('instrument ' + instrAdr + '  offline, e')
    else:
        instrRead = (instr.query('READ?'))
        instr.close()
    return instrRead