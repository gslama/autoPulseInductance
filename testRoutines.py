"""
testRoutines.py
    All the test sequences
"""
import pyvisa
from win32cryptcon import CMSG_HASHED_DATA_V2
import re

import models as dbase
#from main import mainview
#from MainView import outputView
#from InstrumentInterface import rm
import globals as gb
import time
from datetime import datetime
import os
#import keyboard
from tkinter import ttk, messagebox, font
#import asyncio

#from MainView import outputView

# this code runs at startup
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print('pyVisa resources online: ', resources)


def init_test():
    """
    setup all the instruments to initial conditions
    setup function generator
    setup oscilloscope
    setup scanner
    setup power supply

    :return:
    """

    setup_signal_generator(gb.sig_gen)
    #setup_scanner()
    #setup_meter()
    setup_power_supply()
    setup_scope(gb.scope)

    #if gb.system.debugMode:
    #setup_rs_scope()
    #else:
    #    setup_tek_scope()


def setup_signal_generator(sig_gen):
    """
    setup signal generator to initial conditions
    :return:
    """

    # setup function generator

    # reset all
    #instr.write('*RST')
    sig_gen.reset()
    #instr.write("C1:BSWV WVTP, PULSE")
    sig_gen.set_waveform_type('PULSE')
    # todo  convert 1E-6 to pulse units
    period = float(gb.testInfo.pulsePeriod) * 1E-6
    #instr.write(f"C1:BSWV PERI, {period}")
    sig_gen.set_period(period)
    # todo  convert 1E-6 to pulse units
    start_width = float(gb.testInfo.pulseStart) * 1E-6
    #instr.write(f"C1:BSWV WIDTH, {start_width}")
    sig_gen.set_pulse_width(start_width)
    # set output impedance before amplitude levels because changes values
    #instr.write("C1:OUTP LOAD,50")
    sig_gen.set_output_impedance(50)
    #instr.write("C1:BSWV OFST,0V,HLEV,10V,LLEV,0V")
    #sig_gen.set_amplitude(5)
    sig_gen.set_offset(0)
    #instr.write("C1:BSWV HLEV, 5")
    sig_gen.set_high_level(5)
    #instr.write("C1:BSWV LLEV, 0")
    sig_gen.set_low_level(0)


def setup_scope(scope):
    """
    generic initial setup
    some assumptions:
    channel 1 is used for triggering from the signal generator
    channel 2 is for pulse width with 10:1 probe
    channel 3 is for current sense resistor with 50 ohm input
    channel 4 is not used
    :return:
    """

    # defie channels
    chan1 = 1
    chan2 = 2
    chan3 = gb.testInfo.currentChan
    chan4 = 4

    scope.reset()

    # channel 1 used for triggering from signal generator

    scope.set_chan_state(chan1,"ON")
    scope.set_chan_probe(chan1, 1E0)    # was 1E1
    scope.set_chan_scale(chan1, 5E0)    # was 1E1
    scope.set_chan_position(chan1, 2)
    scope.set_chan_bandwidth(1, "B20")

    # channel 2 used for gate pulse with 10:1 probe
    scope.set_chan_state(chan2,"ON")
    scope.set_chan_probe(chan2, 1E1)
    scope.set_chan_scale(chan2, 2E0)
    scope.set_chan_position(chan2, -3)
    scope.set_chan_bandwidth(chan2, "B20")

    # channel 3 used for current sense resistor
    scope.set_chan_state(chan3,"ON")
    scope.set_chan_unit(chan3, 'A')
    #scope.set_chan_probe(chan3, 1E1)
    scope.set_chan_scale(chan3, gb.testInfo.currentScale)
    scope.set_chan_position(chan3, -3)
    scope.set_chan_impedance(chan3, "FIFTY")
    scope.set_chan_coupling(chan3,"DC")
    scope.set_chan_bandwidth(chan3, "B20")

    # channel 4 not used
    #scope.set_chan_state(chan4,"OFF")

    # channel 4 used for scaled output voltage with 10:1 probe
    scope.set_chan_state(chan4,"ON")
    scope.set_chan_probe(chan4, 1E1)
    scope.set_chan_scale(chan4, 5E-1)
    scope.set_chan_position(chan4, -4)
    scope.set_chan_coupling(chan4, "DC")
    scope.set_chan_bandwidth(chan4, "B20")
    scope.set_chan_impedance(chan4, "0MEG")

    # measurements
    scope.set_meas_system("ON")

    # peak current, measurement #1
    scope.set_meas_type(1, "MAX")
    scope.set_meas_source(1, chan3)
    scope.set_meas_state(1, "ON")

    # pulse width, measurement #2
    scope.set_meas_type(2, "WID")
    scope.set_meas_source(2, chan2)
    scope.set_meas_state(2, "ON")

    # measure output divider, measurement #3
    scope.set_meas_type(3, "RMS")
    scope.set_meas_source(3, chan4)
    scope.set_meas_state(3, "ON")

    # timebase
    scope.set_timebase_scale(1E-6)
    scope.set_timebase_delay(4e-6)
    #scope.set_timebase_reference("POS")
    #scope.set_timebase_position(10)

    # acquisition
    scope.set_acquisition_type("NORM")

    # triggering
    scope.set_trigger_mode("SING")
    scope.set_trigger_source(chan1)
    scope.set_trigger_level(3.0)  # was 4
    scope.set_trigger_coupling("DC")
    scope.set_trigger_edge("FALL")



def setup_scanner():
    """
    
    :return: 
    """

    txt_temp_chan = 105     #frmSetup.txtTempChan.Text
    txt_vin_chan = 101      #frmSetup.txtVinChan.Text
    txt_vout_chan = 102     #frmSetup.txtVoutChan.Text

    # setup scanner
    # will still need scanner to measure temperature and voltage
    try:
        instr = rm.open_resource(gb.initValues.scannerAdr)
    except Exception as e:
        print('scanner is offline', e)
    else:
        # reset all
        instr.write('*RST')
        #setup temperature channel
        instr.write(f"conf:temp tc,{gb.testInfo.tempType},(@{gb.testInfo.tempChan})")
        #setup Vin channel
        instr.write(f"conf:volt:dc (@{gb.testInfo.vinChan})")
        #setup Vout channel
        instr.write(f"conf:volt:dc (@{gb.testInfo.voutChan})")
        instr.close()

def setup_meter():
    """
    setup multimeter
    :return: 
    """

    # reset all
    gb.meter.reset()
    #gb.meter.set_scan_state('ON')
    # scanner channels use hp convention with one digit card number followed by two digit chan number
    # siglent routines extract chan number since they have no card number
    #gb.meter.set_volt_chan(0, 102,'DCV')
    #gb.meter.set_volt_chan(0, 103,'DCV')
    #gb.meter.set_temp_chan(104,'T')



def setup_power_supply():
    """
    
    :return: 
    """

    # setup power supply

    # reset all
    #instr.write('*RST')
    gb.power.reset()

    # CH1 - main
    # set to 15V, 2A output default
    gb.power.set_voltage(1, gb.testInfo.vin)
    gb.power.set_current(1, gb.testInfo.currentLimit)

    # CH2 - auxiliary
    gb.power.set_voltage(1, gb.testInfo.vaux)
    gb.power.set_current(1, gb.testInfo.iaux)

    #instr.write(':OUTP1:OCP:STAT ON')
    gb.power.set_power_state(1, 'ON')


def test_pulse(update_queue, done_event, stop_flag_callback, preheat_on):
    '''
    This tests the output by turning on power, and using a single long pulse to get
    peak current and time to calculate inductance
    Temperature is monitored to prevent a hot start
    Instruments are opened and left open to increase speed
    Failure turns off power and sig gen

    reading_frame: calling instance
    :return:
    '''

    global stop_loop
    _label_test_status = None
    cancel_code = 50
    status = 0
    gb.testData.lpulseSpecific = ''

    # set power supply on
    power_set()

    # setup pulse generator
    # format period and start_width
    # lets assume us for units
    if gb.testInfo.pulseUnits == 'us':
        pulse_units = 1E-6
    elif gb.testInfo.pulseUnits == 'ms':
        pulse_units = 1E-3
    elif gb.testInfo.pulseUnits == 's':
        pulse_units = 1
    else:
        pulse_units = 1

    pulse_width = float(gb.testInfo.pulseStop)

    # check part temperature is in range
    # log_temp = float(get_temperature(instr_scan))
    #log_temp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
    log_temp = gb.thermo.get_measurement(1)
    while (log_temp < gb.testInfo.minTemp or log_temp > gb.testInfo.maxTemp):
        # display
        # if too cold wait by checking every 2 seconds
        if log_temp < gb.testInfo.minTemp:
            label_update = {'type': 'label', 'label_name': 'status', 'value': "Too Cold", 'color': "sky blue"}
            update_queue.put(label_update)
        # if too hot wait by checking every 2 seconds
        if log_temp > gb.testInfo.maxTemp:
            label_update = {'type': 'label', 'label_name': 'status', 'value': "Too Hot", 'color': "red"}
            update_queue.put(label_update)

        # wait 2 seconds
        time.sleep(2)
        # log_temp = get_temperature(instr_scan)
        #log_temp = float(gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T'))
        log_temp = gb.thermo.get_measurement(1)
        label_update = {'type': 'label', 'label_name': 'finaltemp', 'value': f"{log_temp:.1f}", 'color': "grey85"}
        update_queue.put(label_update)

        if stop_flag_callback():
            print("Stop flag triggered")
            abort_flag = True
            break

    # preheat sequence
    abort_flag = False
    if gb.testInfo.preheat:
        # status
        label_update = {'type': 'label', 'label_name': 'status', 'value': "PreHeat", 'color': "yellow"}
        update_queue.put(label_update)

        # turn on signal generator
        gb.sig_gen.set_output_state('ON')

        # wait a half second to stabelize
        time.sleep(0.5)

        # monitor temperature until target
        #gb.testData.finalTemp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
        gb.testData.finalTemp = gb.thermo.get_measurement(1)
        while gb.testData.finalTemp < gb.testInfo.setTemp:
            # display
            label_update = {'type': 'label', 'label_name': 'finaltemp', 'value': f"{gb.testData.finalTemp:.1f}",
                            'color': "grey85"}
            update_queue.put(label_update)
            #gb.testData.finalTemp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
            gb.testData.finalTemp = gb.thermo.get_measurement(1)

            # check for abort - premature end of test
            if stop_flag_callback():
                print("Stop flag triggered")
                abort_flag = True

            if abort_flag:
                label_update = {'type': 'label', 'label_name': 'status', 'value': "Aborted", 'color': "red"}
                update_queue.put(label_update)
                # turn stuff off
                gb.sig_gen.set_output_state('OFF')
                gb.power.set_power_state(1, 'OFF')
                # delay so shows up on display
                time.sleep(0.2)
                done_event.set()
                return

        # turn off signal generator
        gb.sig_gen.set_output_state('OFF')

        # clear status
        label_update = {'type': 'label', 'label_name': 'status', 'value': "Testing", 'color': "gray85"}
        update_queue.put(label_update)

    # update start time
    start_time = time.time()

    # start main loop ==================================================
    for i in range(3):

        if stop_flag_callback():
            print("Stop flag triggered")
            abort_flag = True

        # check for abort - premature end of test
        if abort_flag:
            label_update = {'type': 'label', 'label_name': 'status', 'value': "Aborted", 'color': "red"}
            update_queue.put(label_update)
            # delay so shows up on display
            time.sleep(0.2)
            done_event.set()
            return

        # start test
        gb.power.set_power_state(1, 'ON')
        label_update = {'type': 'label', 'label_name': 'status', 'value': "Testing", 'color': "yellow"}
        update_queue.put(label_update)

        # get input voltage
        # TODO vin = get_input_voltage(instr_scan)
        vin = gb.power.get_voltage(1)
        #print(f'vin: {vin}')
        gb.testData.vin = vin
        # display
        label_update = {'type': 'label', 'label_name': 'voltagein', 'value': f"{gb.testData.vin:.2f}", 'color': "grey85"}
        update_queue.put(label_update)

        # debug scope status
        #result = gb.scope.get_trigger_mode()
        #print (f'trigger mode: {result}')
        #result = gb.scope.get_trigger_status()
        #print (f'trigger status: {result}')

        # set scope to one shot
        # check trigger status
        if 'Stop' in gb.scope.get_trigger_status():
            gb.scope.set_trigger_mode('SINGLE')

        #gb.scope.set_trigger_mode('SINGLE')
        if 'SING' not in gb.scope.get_trigger_mode():
            gb.scope.set_trigger_mode('SINGLE')
            print("set single")

        # debug delay
        time.sleep(1)

        # pulse width sent in seconds to meter
        gb.sig_gen.set_pulse_width(round(pulse_width * pulse_units, 9))
        gb.testData.pulseWidth = pulse_width

        # turn on generator
        gb.sig_gen.set_output_state('ON')

        # wait 200 ms to charge capacitor
        time.sleep(0.2)

        # get pulse width
        result = gb.scope.get_meas_value(2)
        if "*" in result:
            # error
            gb.sig_gen.set_output_state('OFF')
            abort_flag = True
            print('Failed to get pulse width')
            break
        else:
            # get pulse width from scope
            #meas_pulse_width = float(gb.scope.get_meas_value(2))
            # under some conditions this returned empty
            meas_pulse_width = read_measurement_float(gb.scope.get_meas_value, 2, retries=10, delay=0.05)
            # get current from scope
            #meas_ipk = float(gb.scope.get_meas_value(1))
            meas_ipk = read_measurement_float(gb.scope.get_meas_value, 1, retries=10, delay=0.05)

            # reset trigger because at first trigger not enough cycles have passed to charge the capacitor
            gb.scope.set_trigger_mode('SINGLE')
            # get output voltage from scope
            # had to add retries because was returning empty the first few calls
            #meas_vout = float(gb.scope.get_meas_value(3))
            meas_vout = read_measurement_float(gb.scope.get_meas_value, 3, retries=10, delay=0.05)
            print(f'Vout: {meas_vout * float(gb.testInfo.voltageRatio)}')

        # turn off generator
        gb.sig_gen.set_output_state('OFF')

        # calc test time
        gb.testData.testTime = time.time() - start_time
        # display
        label_update = {'type': 'label', 'label_name': 'testtime', 'value': f"{gb.testData.testTime:.2f}", 'color': "grey85"}
        update_queue.put(label_update)
        #print(f"test time: {gb.testData.testTime}")

        # get temperature
        #gb.testData.finalTemp = gb.scanner.get_meas_temp(gb.testInfo.tempChan, 'T')
        gb.testData.finalTemp = gb.thermo.get_measurement(1)
        #print(f'max_temp: {gb.testData.finalTemp}')
        # display
        label_update = {'type': 'label', 'label_name': 'finaltemp', 'value': f"{gb.testData.finalTemp:.1f}", 'color': "grey85"}
        update_queue.put(label_update)

        # display actual pulse width
        # display
        label_update = {'type': 'label', 'label_name': 'pulsewidth', 'value': f"{1E6*meas_pulse_width:.2f}", 'color': "grey85"}
        update_queue.put(label_update)

        # todo left off here
        # scale by ratio
        avg_vout = meas_vout * gb.testInfo.voltageRatio
        gb.testData.vout = avg_vout
        # display
        label_update = {'type': 'label', 'label_name': 'vout', 'value': f"{gb.testData.vout:.1f}", 'color': "grey85"}
        update_queue.put(label_update)

        # scale to ratio and convert of amps
        meas_ipk = meas_ipk / (float(gb.testInfo.currentRatio) * 1E-3)
        gb.testData.ipk = meas_ipk
        # display
        label_update = {'type': 'label', 'label_name': 'ipk', 'value': f"{gb.testData.ipk:.3f}", 'color': "grey85"}
        update_queue.put(label_update)

        # todo - display pulse width?

        #print(f"meas_vout: {meas_vout:.3f}")
        #print(f"meas_ipk: {meas_ipk:.3f}")

        # check for minimum pulse width of 1.5 us to break out
        if meas_pulse_width > 1.5E-6:
            break

    # end of main test for loop =================================

    # check for errors
    # minimum pulse width - value based on empirical testing
    #print(f"i: {i}, meas_pulse_width: {meas_pulse_width}")
    if meas_pulse_width:
        if meas_pulse_width < 1.5E-6:
            messagebox.showerror(title="Test Error", message="Pulse width too short. Check connections or part")
            abort_flag = True
            #return

        # no primary pulse current - arbitrarily set to 400 mA
        elif meas_ipk < 0.40:
            messagebox.showerror(title="Test Error", message="Primary Open. Check connections or part")
            abort_flag = True
            #return

    # pulse current within expected range - +/- 10% of target
    # current probe description as current value - need to extract it
    # example probe = "1.5 A (0.604R)"
    match = re.search(r"[-+]?\d*\.?\d+", gb.testInfo.currentProbe)
    if match:
        target_ipk = float(match.group())
        print(f"probe: {gb.testInfo.currentProbe}, target ipk: {target_ipk}")
    else:
        target_ipk = 0

    # ipeakLo and ipeakHi are tolerance multipliers to the target value
    #print(isinstance(target_ipk, float))
    #print(isinstance(gb.initValues.ipeakLo, float))
    #print(isinstance(gb.initValues.ipeakHi, float))
    if meas_ipk < target_ipk * float(gb.initValues.ipeakLo) or meas_ipk > target_ipk * float(gb.initValues.ipeakHi):
        messagebox.showerror(title="Test Error", message=f"Peak current {meas_ipk:.3f} A out of range {target_ipk * float(gb.initValues.ipeakLo):.3f} A to {target_ipk * float(gb.initValues.ipeakHi):.3f} A. Change tolerance or trim sense resistor.")
        abort_flag = True
        #return

    # open secondary
    #if meas_vout < 0.1:
    #    messagebox.showerror(title="Test Error", message="Secondary Open or Shorted. Check connections or part")
    #    abort_flag = True
        #return

    if stop_flag_callback():
        print("Stop flag triggered")
        abort_flag = True
        #break

    # shut down test
    shutdown_test()

    # check for abort - premature end of test
    if abort_flag:
        # display fail
        label_update = {'type': 'label', 'label_name': 'status', 'value': "Aborted", 'color': "red"}
        update_queue.put(label_update)
        # needs a delay here so label can update
        #time.sleep(0.2)
        done_event.set()
        return


    # calculate pulse inductance in uH
    gb.testData.lpulse = (vin * meas_pulse_width) / meas_ipk
    label_update = {'type': 'label', 'label_name': 'lpulse', 'value': f"{1E6*gb.testData.lpulse:.2f}", 'color': "grey85"}
    update_queue.put(label_update)

    '''
    # check minimum output voltage
    if avg_vout < (gb.testLimits['outputVoltmin']):
        gb.testData.status = 5
        status = 5
        # message fail low
        label_update = {'type': 'label', 'label_name': 'status', 'value': "TR-Fail", 'color': "red"}
        update_queue.put(label_update)        #elif gb.testData.status == 0 or gb.testData.status == 1:
    else:
        # promote from undefined to good part, or from bad part(5) to good part?
        gb.testData.status = 1
        status = 1
        label_update = {'type': 'label', 'label_name': 'status', 'value': "TR-Pass", 'color': "green"}
        update_queue.put(label_update)
    '''

    # delay to allow mainview to update
    time.sleep(1)
    print("end of thread")
    done_event.set()
    return


def shutdown_test():
    '''
    turn off test instruments gracefully
    :return:
    '''

    # turn off siggen
    gb.sig_gen.set_output_state('OFF')
    # turn off power
    gb.power.set_power_state(1, 'OFF')
    return



def power_set():
    """
    set voltage and current
    :param instr:
    :return:
    """

    gb.power.set_voltage(1, gb.testInfo.vin)
    gb.power.set_current(1, gb.testInfo.currentLimit)
    return


def get_temperature(instr):
    '''
    hp34970a

    :return:
    '''

    # chan example 105
    #print(f"MEAS:TEMP? TC,{gb.testInfo.tempType},(@{gb.testInfo.tempChan})")
    temp = instr.query(f"MEAS:TEMP? TC,{gb.testInfo.tempType},(@{gb.testInfo.tempChan})")

    #print(f"Temp: {temp}")
    #instr.close()
    return float(temp)


def get_input_voltage(instr):
    '''
    hp34970a
    :return:
    '''
    # chan example 102
    volt = instr.query(f"MEAS:VOLT:DC? (@{gb.testInfo.vinChan})")
    #print(f"Input Volt: {volt}")
    #instr.close()
    return float(volt)


def get_output_voltage(instr):
    '''
    hp34970a
    :return:
    '''
    # chan example 103
    #voltage = instr.query(f"MEAS:VOLt:DC? (@{gb.testInfo.voutChan})")
    #print(f"Output Volt: {voltage}")
    #instr.close()

    voltage = instr.get_meas_value(3)
    print(f'vout: {voltage}')
    return float(voltage)


def scanner_message(instr, message):
    '''
    dispLAy a message in scanner screen
    :param message:
    :return:
    '''

    # chan example 103
    volt = instr.write(f"disp:text '{message}'")
    #instr.close()
    return


def get_current(instr):
    '''
    scope measurement 1
    uses sense resistor or probe
    form_setup has input for value
    assumes measurement 1 using channel 3
    uses 0.332 ohms || 50 ohms for 2.7A = 0.328 mV/div
    uses 0.604 ohms || 50 ohms for 1.5A = 0.597 mV/div
    :return:
    '''
    #if gb.system.debugMode:
        # call r&s
    #current = instr.query("MEAS1:RESult:ACTual? UPE")
    current = instr.get_meas_value(1)
    print(f'ipk: {current}')
    #print(f"Ipeak: {current}")
    #else:
       # call tek
    #    get_current = instr.query("MEAS:MEAS1:VAL?")

    return float(current)


def get_vdss(instr):
    '''
    scope measurement 2
    form_setup has input for value
    :return:
    '''
    #if gb.system.debugMode:
    # call r&s
    #vdss = instr.query("MEAS2:RESult:ACTual? UPE")
    vdss = instr.get_meas_value(2)
    #print(f"Vdss: {vdss}")
    #else:
    #    # call tek
    #    vdss = instr.query("MEASU:MEAS2:VAL?")

    return float(vdss)


import time, math, re

_NUM_RE = re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?')

def _parse_float(raw):
    if raw is None:
        return None
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode(errors='ignore')
    s = str(raw).strip()
    if not s or '*' in s or s.lower() in {'nan', 'inf', '+inf', '-inf'}:
        return None
    m = _NUM_RE.search(s)  # handles values like "1.234 V"
    if not m:
        return None
    try:
        val = float(m.group(0))
        return val if math.isfinite(val) else None
    except ValueError:
        return None

def read_measurement_float(getter, *getter_args, retries=20, delay=0.05, backoff=1.5):
    """
    Calls `getter(*getter_args)` until a finite float is returned or retries are exhausted.
    Raises RuntimeError on failure.
    """
    last = None
    for _ in range(retries):
        last = getter(*getter_args)
        val = _parse_float(last)
        if val is not None:
            return val
        time.sleep(delay)
        delay *= backoff  # gentle backoff
        #print(f'Retries for get scope measurements: {_}')
    raise RuntimeError(f"Failed to get numeric measurement after {retries} tries (last={last!r}).")






###########################################################

# code to run functions in this file for testing the process

def start_function_generator(instr, period, start_width):
    """

    :return:
    """

    instr.write("C1:BSWV WVTP, PULSE")
    instr.write(f"C1:BSWV PERI, {period}")
    instr.write(f"C1:BSWV WIDTH, {start_width}")

    #instr.write("C1:BSWV FRE, 50000") - alternate
    #instr.write("C1:BSWV DUTY, 25") - alternate
    #instr.write("C1:BSWV HLEV, 5")
    #instr.write("C1:BSWV LLEV, 0")
    #instr.write("C1:BSWV AMP, 5") - alternate
    #instr.write("C1:BSWV OFST, 2.5") - alternate


# updater_module.py

class LabelManager:
    def __init__(self):
        self.labels = {}

    def register_label(self, name, label):
        """Register a label by name."""
        self.labels[name] = label

    def update_label(self, name, new_text, new_color):
        """Update a label by name."""
        if name in self.labels:
            self.labels[name].config(text=new_text, background=new_color)

# Create a global instance of LabelManager
#label_manager = LabelManager()


