"""
TestRoutines.py
    All the test sequences
"""
import pyvisa
from win32cryptcon import CMSG_HASHED_DATA_V2

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
    setup_meter()
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
    channel 2 is for vdss with 10:1 probe
    channel 3 is for current probe or direct into 1 Mohm
        the two current probes have different setups
        - when direct across sense resistor needs 50 ohm input
    channel 4 is used for vout with 10:1 probe
    :return:
    """

    scope.reset()

    # channel 1 used for triggering
    scope.set_chan_state(1,"ON")
    scope.set_chan_probe(1, 1E0)    # was 1E1
    scope.set_chan_scale(1, 5E0)    # was 1E1
    scope.set_chan_position(1, 2)
    scope.set_chan_bandwidth(1, "B20")

    # channel 2 used for vdss with 10:1 probe
    scope.set_chan_state(2,"ON")
    scope.set_chan_probe(2, 1E1)
    scope.set_chan_scale(2, 1E2)
    scope.set_chan_position(2, -3)
    scope.set_chan_bandwidth(2, "B20")

    # channel 3 used for current
    # default for resistor based or other
    scope.set_chan_state(3,"ON")
    scope.set_chan_unit(3, 'A')
    #scope.set_chan_probe(3, 1E1)
    scope.set_chan_scale(3, 200E-3)
    scope.set_chan_position(3, 2)
    scope.set_chan_impedance(3, "FIFTY")
    scope.set_chan_coupling(3,"DC")
    scope.set_chan_bandwidth(3, "B20")

    # determine current probe type
    if gb.testInfo.currentProbe == "P6021":
        scope.set_chan_probe(3, 1E1)
        scope.set_chan_scale(3, 1E0)
        scope.set_chan_position(3, -3)
        scope.set_chan_coupling(3, "AC")
        scope.set_chan_impedance(3, "0MEG")
    elif gb.testInfo.currentProbe == "TCP202":
        scope.set_chan_scale(3, 1E0)

    # channel 4 used for scaled output voltage with 10:1 probe
    scope.set_chan_state(4,"ON")
    scope.set_chan_probe(4, 1E1)
    scope.set_chan_scale(4, 5E-1)
    scope.set_chan_position(4, -4)
    scope.set_chan_coupling(4, "DC")
    scope.set_chan_bandwidth(4, "B20")
    scope.set_chan_impedance(4, "0MEG")

    # measurements
    scope.set_meas_system("ON")

    scope.set_meas_type(1, "MAX")
    scope.set_meas_source(1, 3)
    scope.set_meas_state(1, "ON")

    scope.set_meas_type(2, "MAX")
    scope.set_meas_source(2, 2)
    scope.set_meas_state(2, "ON")

    scope.set_meas_type(3, "RMS")
    scope.set_meas_source(3, 4)
    scope.set_meas_state(3, "ON")

    # timebase
    scope.set_timebase_scale(1E-6)
    scope.set_timebase_delay(4e-6)
    #scope.set_timebase_reference("POS")
    #scope.set_timebase_position(10)

    # triggering
    scope.set_trigger_mode("NORM")
    scope.set_trigger_source(1)
    scope.set_trigger_level(3.0)  # was 4
    scope.set_trigger_coupling("DC")
    scope.set_trigger_edge("RISE")

    # acquisition
    scope.set_acquisition_type("NORM")

def setup_tek_scope():
    """
    Setup for Tek scopes
    some assumptions:
        channel 1 is used for triggering from the signal generator
        channel 2 is for vdss with 10:1 probe
        channel 3 is for current probe or direct into 1 Mohm
            the two current probes have different setups
        channel 4 not used
    :return: 
    """
    # setup oscilloscope
    try:
        instr = rm.open_resource(gb.initValues['scopeAdr'])
    except Exception as e:
        print('oscilloscope is offline', e)
    else:
        # reset all
        instr.write('*RST')
        # setup parameters for Vout vs Ipk, Vds testing
        # setup channel one - trigger channel from oscillator
        instr.write("SELECT:CH1 ON")    #'CHAN1:STATE ON'
        instr.write("CH1:SCALE 1E1")    #'CHAN1:SCALE 1E1'
        instr.write("CH1:POSITION 2.0") #'CHAN1:POSITION 2.0'

        # setup channel 2 - Vdss 1:10 voltage probe
        instr.write("SELECT:CH2 ON")        #'CHAN2:STATE ON'
        instr.write("CH2:SCALE 1E2")        #'CHAN2:SCALE 1E1'
        instr.write("CH2:POSITION -1.0")    #'CHAN2:POSITION -1.0'

        # setup channel 3 - Ipri - current resistor assumed
        instr.write("SELECT:CH3 ON")        #'CHAN3:STATE ON'
        instr.write("CH3:SCALE 500E-3")     #'CHAN3:SCALE 200E-3'
        instr.write("CH3:COUPLING DC")      #'CHAN3:COUPING DCLIMIT'
        instr.write("CH3:IMPEDANCE FIFTY")  # doesn't have this option
        instr.write("CH3:POSITION -3.0")    #'CHAN3:POSITION -1.0'
        instr.write("CH3:BANDWIDTH TWENTY") #'CHAN3:BANDWIDTH B20'

        # determine current probe type
        #If frmSetup.optCurP6021.Value == True:
        #  instr.write("CH3:SCALE 100E-3")
        #   instr.write("CH3:COUPLING AC")
        #   instr.write("CH3:IMPEDANCE MEG")
        #   msCurFactor = 10
        #Elsif frmSetup.optCurTCP202.Value == True:
        #   instr.write("CH3:COUPLING DC")
        #   instr.write("CH3:SCALE 1E0")
        #   instr.write("CH3:IMPEDANCE FIFTY")
        #   msCurFactor = 1

        # setup channel 4
        instr.write("SELECT:CH4 OFF")   #'CHAN4:STATE OFF'

        # measurements
        instr.write("MEASUREMENT:MEAS1:TYPE MAXIMUM")   #'MEASUREMENT1:TYPE UPE'
        instr.write("MEASUREMENT:MEAS1:SOURCE CH3")     #'MEASUREMENT1:SOURCE CH3'
        instr.write("MEASUREMENT:MEAS1:STATE ON")       #'MEASUREMENT1:ENABLE ON'

        instr.write("MEASUREMENT:MEAS2:TYPE MAXIMUM")   #'MEASUREMENT2:TYPE UPE'
        instr.write("MEASUREMENT:MEAS2:SOURCE CH2")     #'MEASUREMENT2:SOURCE CH2'
        instr.write("MEASUREMENT:MEAS2:STATE ON")       #'MEASUREMENT2:ENABLE ON'

        # setup timing scale
        instr.write("HORIZONTAL:MAIN:SCALE 1E-6")       #'TIMEBASE:SCALE 1E-6'
        instr.write("HORIZONTAL:DELAY:STATE OFF")       #''
        instr.write("HORIZONTAL:TRIGGER:POSITION 10")   #'TIMEBASE:REFERENCE 10'

        # setup triggering
        instr.write("ACQUIRE:STOPAFTER RUNSTOP")        #'ACQUIRE:'
        instr.write("ACQUIRE:STATE 1")                  #'ACQUIRE:'
        instr.write("ACQUIRE:MODE SAMPLE")              #'CHANNEL1:TYPE SAMPLE'
        instr.write("TRIGGER:MAIN:MODE NORMAL")         #'TRIGGER:A:MODE NORMAL'
        instr.write("TRIGGER:MAIN:EDGE:SOURCE CH1")     #'TRIGGER:A:SOURCE CH1'
        instr.write("TRIGGER:MAIN:LEVEL 4.0")           #'TRIGGER:A:LEVEL 4.0'
        instr.write("TRIGGER:MAIN:EDGE:COUPLING DC")    #'TRIGGER:A:EDGE:COUPLING DC'
        instr.write("TRIGGER:MAIN:EDGE:SLOPE RISE")     #'TRIGGER:A:EDGE:SLOPE POSITIVE'
        instr.close()

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
        instr = rm.open_resource(gb.initValues['scannerAdr'])
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


def setup_rs_scope():
    '''
    this is used to test program using slamatech instruments
    scope: Rohde&Swartz RTB2004
    signal generator: Siglent SDG2042
    power supply: GwInstek GPP4323
    temperature:
    :return:
    '''


    # setup oscilloscope
    try:
        instr = rm.open_resource(gb.initValues['scopeAdr'])
    except Exception as e:
        print('oscilloscope is offline', e)
    else:
        # reset all
        instr.write('*RST')
        # setup parameters for Vout vs Ipk, Vds testing
        # setup channel one - trigger channel from oscillator
        instr.write('CHAN1:STATE ON')
        instr.write('PROBE1:SET:ATT:MAN 10')
        instr.write('CHAN1:SCALE 5')
        instr.write('CHAN1:POSITION 2.0')
        instr.write('CHAN1:BANDWIDTH B20')

        # setup channel 2 - Vdss 1:10 voltage probe
        instr.write('CHAN2:STATE ON')
        instr.write('PROBE1:SET:ATT:MAN 10')
        instr.write(f'CHAN2:SCALE {gb.testInfo.vdssScale}')
        instr.write('CHAN2:POSITION -2.0')
        instr.write('CHAN2:BANDWIDTH B20')

        # setup channel 3 - Ipri - current resistor assumed
        instr.write('CHAN3:STATE ON')
        instr.write(f'CHAN3:SCALE {gb.testInfo.currentScale}')
        instr.write('CHAN3:COUPING DCLIMIT')
        #instr.write("CH3:IMPEDANCE FIFTY")  # doesn't have this option
        instr.write('CHAN3:POSITION -3.0')
        instr.write('CHAN3:BANDWIDTH B20')

        # determine current probe type
        #If frmSetup.optCurP6021.Value == True:
        #   instr.write("CHAN3:SCALE 100E-3")
        #   instr.write("CHAN3:COUPLING AC")
        #instr.write("CHAN3:IMPEDANCE MEG")
        #msCurFactor = 10
        #Elsif frmSetup.optCurTCP202.Value == True:
        #   instr.write("CH3:COUPLING DC")
        #   instr.write("CH3:SCALE 1E0")
        #   instr.write("CH3:IMPEDANCE FIFTY")
        #   msCurFactor = 1

        # setup channel 4
        instr.write('CHAN4:STATE OFF')

        # measurements
        instr.write('MEASUREMENT1:MAIN UPE')
        instr.write('MEAS1:SOURCE CH3')
        instr.write('MEAS1:ENABLE ON')

        instr.write('MEASUREMENT2:MAIN UPE')
        instr.write('MEASUREMENT2:SOURCE CH2')
        instr.write('MEASUREMENT2:ENABLE ON')

        # setup timing scale
        timebase_scale = 1E-6  #normally 1E-6
        instr.write(f'TIMEBASE:SCALE {timebase_scale}')
        #instr.write("HORIZONTAL:DELAY:STATE OFF")       #''
        instr.write('TIMEBASE:REFERENCE 10')

        # setup triggering
        #instr.write("ACQUIRE:STOPAFTER RUNSTOP")        #'ACQUIRE:'
        #instr.write("ACQUIRE:STATE 1")                  #'ACQUIRE:'
        instr.write('CHANNEL1:TYPE SAMPLE')
        instr.write('TRIGGER:A:MODE NORMAL')
        instr.write('TRIGGER:A:SOURCE CH1')
        trigger_level = 3  #NORMALLY 4
        instr.write(f'TRIGGER:A:LEVEL {trigger_level}')
        instr.write('TRIGGER:A:EDGE:COUPLING DC')
        instr.write('TRIGGER:A:EDGE:SLOPE POSITIVE')
        instr.close()



def test_output(update_queue, done_event, stop_flag_callback):
    '''
    This tests the output by turning on power, and stepping the pulse width from start to stop
    while checking peak current and output voltage thresholds to stop early
    The values are read from the scope four times, the first is tossed and the last three are averaged
    Temperature is monitored to prevent a hot start
    Instruments are opened and left open to increase speed
    Failure turns of power and sig gen
    outputs a csv of each iteration and records final values to database

    reading_frame: calling instance
    :return:
    '''

    global stop_loop
    _label_test_status = None
    cancel_code = 50
    status = 0
    gb.testData.lpulseSpecific = ''

    # make a csv file name for this part
    base_path = "Design\\LTCC\\TestData"
    output_path = "Output_Test"
    bar_num = "4255Y"
    design_num = "D47"
    part_num = "27"
    directory = (f"{base_path}\\{output_path}\\{gb.testInfo.barNum}")
    output_file = (f"{gb.testInfo.barNum}{gb.testInfo.designNum}x{gb.testInfo.position}.csv")
    file_path = os.path.join(directory, output_file)

    # create the directory if it does not exist
    os.makedirs(directory, exist_ok=True)

    # check if it exists
    if os.path.exists(output_file):
        print(f"The file '{output_file}' exists.")
        # message
        response = messagebox.askyesnocancel(title="File exists", message=f"File '{output_file}' already exists. Yes overwrites, No appends. Do you want to overwrite it?")

        if response is True:
            # overwrite file
            dbase.create_output_file_header()
        elif response is False:
            # append to file
            pass
        else:
            # cancel, exit
            return cancel_code
    else:
        print(f"Creating '{output_file}'")
        # create it
        dbase.create_output_file_header()


    #try:
    #    instr_power = rm.open_resource(gb.initValues['powerAdr'])
    #except Exception as e:
    #    print('power supply is offline, ', e)
    #    messagebox.showerror(title="Testing", message="Power supply is offline")
    #    return cancel_code

    # set power supply
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

    # reducing starting width by one pulse step because loop adds one step immediately
    pulse_width = float(gb.testInfo.pulseStart)

    # reset timers
    minutes = 0
    timer_flag = False
    last_pulse_width = 0
    last_ipk = 0
    last_vout = 0
    abort_flag = False

    # determine number of loops
    # needed round() to fix float conversion
    test_steps = round((float(gb.testInfo.pulseStop) - float(gb.testInfo.pulseStart)) / float(gb.testInfo.pulseStep)) + 1
    #print(f"num of test steps: {test_steps}")

    # start main loop ==================================================
    for i in range(test_steps):
        #    check part temperature is in range
        #log_temp = float(get_temperature(instr_scan))
        log_temp = gb.meter.get_meas_temp(gb.testInfo.tempChan,'T')
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
            #log_temp = get_temperature(instr_scan)
            log_temp = float(gb.meter.get_meas_temp(gb.testInfo.tempChan,'T'))
            label_update = {'type': 'label', 'label_name': 'finaltemp', 'value': f"{log_temp:.1f}", 'color': "grey85"}
            update_queue.put(label_update)

            if stop_flag_callback():
                print("Stop flag triggered")
                abort_flag = True
                break

        # check for abort - premature end of test
        if abort_flag:
            label_update = {'type': 'label', 'label_name': 'status', 'value': "Aborted", 'color': "red"}
            update_queue.put(label_update)
            # delay so shows up on display
            time.sleep(0.2)
            done_event.set()
            return

        # update start time
        start_time = time.time()
        now = datetime.now()
        gb.testData.logTime = now.strftime("%Y-%m-%d %H:%M:%S")
        # todo replace start_temp with log_temp to save time
        #start_temp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
        start_temp = log_temp

        # start test
        gb.power.set_power_state(1, 'ON')
        label_update = {'type': 'label', 'label_name': 'status', 'value': "Testing", 'color': "yellow"}
        update_queue.put(label_update)

        # get input voltage
        # TODO vin = get_input_voltage(instr_scan)
        vin = gb.power.get_voltage(1)
        print(f'vin: {vin}')
        gb.testData.vin = vin
        # display
        label_update = {'type': 'label', 'label_name': 'voltagein', 'value': f"{gb.testData.vin:.2f}", 'color': "grey85"}
        update_queue.put(label_update)

        # pulse width sent in seconds to meter
        gb.sig_gen.set_pulse_width(round(pulse_width * pulse_units, 9))
        gb.testData.pulseWidth = pulse_width
        # display
        label_update = {'type': 'label', 'label_name': 'pulsewidth', 'value': f"{gb.testData.pulseWidth:.1f}", 'color': "grey85"}
        update_queue.put(label_update)

        #    turn on generator
        gb.sig_gen.set_output_state('ON')

        #    wait 300 ms
        time.sleep(0.3)

        # clear arrays
        tmp_vout = [0] * 4
        tmp_ipk = [0] * 4
        tmp_vdss = [0] * 4

        #    loop 4 times
        for i in range(4):
            #print(f"index: {i}")
            # get current
            tmp_ipk[i] = get_current(gb.scope)
            # get output voltage
            tmp_vout[i] = get_output_voltage(gb.scope)
            # get vdss
            tmp_vdss[i] = get_vdss(gb.scope)

        # turn off generator
        gb.sig_gen.set_output_state('OFF')

        # calc test time
        gb.testData.testTime = time.time() - start_time
        # display
        label_update = {'type': 'label', 'label_name': 'testtime', 'value': f"{gb.testData.testTime:.2f}", 'color': "grey85"}
        update_queue.put(label_update)
        print(f"test time: {gb.testData.testTime}")

        # get temperature
        # loop temperature until max is reached
        # todo restore temp loop
        # log_temp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
        '''
        # removed this becaus etest so fast the part hardly heats up
        # seems each temp reading takes 1 second
        max_temp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
        while max_temp > log_temp:
            log_temp = max_temp
            max_temp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
            #time.sleep(1)
        gb.testData.finalTemp = max_temp
        gb.testData.tempDiff = max_temp - start_temp
        '''
        gb.testData.finalTemp = gb.meter.get_meas_temp(gb.testInfo.tempChan, 'T')
        gb.testData.tempDiff = gb.testData.finalTemp - start_temp
        print(f'max_temp: {gb.testData.finalTemp}')
        # display
        label_update = {'type': 'label', 'label_name': 'finaltemp', 'value': f"{gb.testData.finalTemp:.1f}", 'color': "grey85"}
        update_queue.put(label_update)

        # average last three readings
        avg_vout = (tmp_vout[1]+tmp_vout[2]+tmp_vout[3])/3.0
        # scale by ratio
        avg_vout = avg_vout * gb.testInfo.voltageRatio
        gb.testData.vout = avg_vout
        # display
        label_update = {'type': 'label', 'label_name': 'vout', 'value': f"{gb.testData.vout:.1f}", 'color': "grey85"}
        update_queue.put(label_update)

        avg_ipk = (tmp_ipk[1]+tmp_ipk[2]+tmp_ipk[3])/3.0
        # scale to ratio and convert of amps
        #avg_ipk = avg_ipk / (gb.testInfo.currentRatio * 1E-3)
        gb.testData.ipk = avg_ipk
        # display
        label_update = {'type': 'label', 'label_name': 'ipk', 'value': f"{gb.testData.ipk:.3f}", 'color': "grey85"}
        update_queue.put(label_update)

        gb.testData.vdss = (tmp_vdss[1]+tmp_vdss[2]+tmp_vdss[3])/3.0
        # display
        label_update = {'type': 'label', 'label_name': 'vdss', 'value': f"{gb.testData.vdss:.1f}", 'color': "grey85"}
        update_queue.put(label_update)

        # display update plot
        label_update = {'type': 'plot', 'x_data': avg_ipk, 'y_data': avg_vout * 0.001, }
        update_queue.put(label_update)

        #print(f"avg_vout: {avg_vout:.3f}")
        #print(f"avg_ipk: {avg_ipk:.3f}")
        #print(f"avg_vdss: {gb.testData.vdss:.3f}")

        # check of errors
        # no primary current - arbitrarily set to 50 mA, was 50 mA
        if avg_ipk < 0.40:
            messagebox.showerror(title="Test Error", message="Primary Open. Check connections or part")
            abort_flag = True
            break

        # open secondary
        if avg_vout < 0.1:
            messagebox.showerror(title="Test Error", message="Secondary Open or Shorted. Check connections or part")
            abort_flag = True
            break

        # calculate pulse inductance of this loop in uH
        gb.testData.lpulse = (vin * pulse_width) / avg_ipk
        #label_update = {'type': 'label', 'label_name': 'lpulse', 'value': f"{gb.testData.lpulse:.2f}", 'color': "grey85"}
        #update_queue.put(label_update)

        # calculate pulse inductance at threshold point
        # capture pulsewidth, pk current and voltage with each pass until over threshold
        # then use old valve and current value to do calculation
        #last_ipk = avg_ipk
        if avg_ipk > gb.testInfo.lpulseCurrent and gb.testData.lpulseSpecific == '':
            # do calc by interpolation
            # calculate pulse inductance at target
            # first get pulse inductance at the two reading levels provided
            # Vin is the input voltage
            l_new = (vin * pulse_width) / avg_ipk
            #todo something not right here
            l_old = (vin * last_pulse_width) / last_ipk

            # second find slope and determine inductance at target
            slope = (l_new - l_old) / (avg_ipk - last_ipk)
            gb.testData.lpulseSpecific = l_old + slope * (gb.testInfo.lpulseCurrent - last_ipk)
            label_update = {'type': 'label', 'label_name': 'lpulsespec', 'value': f"{gb.testData.lpulseSpecific:.2f}",
                            'color': "grey85"}
            update_queue.put(label_update)

            # calculate output voltage at target current
            sSlope = (avg_vout - last_vout) / (avg_ipk - last_ipk)
            gb.testData.voutlp = last_vout + sSlope * (gb.testInfo.lpulseCurrent - last_ipk)
            label_update = {'type': 'label', 'label_name': 'voutlp', 'value': f"{gb.testData.voutlp:.2f}",
                            'color': "grey85"}
            update_queue.put(label_update)

        else:
            # save values
            last_pulse_width = pulse_width
            last_ipk = avg_ipk
            last_vout = avg_vout

        # write line of results to csv file for each loop interation
        dbase.append_data_output_file()

        # check to stop loop
        # max current
        if avg_ipk > float(gb.testInfo.thresholdCurrent):
            # need to stop
            break

        # max output voltage
        if avg_vout > float(gb.testInfo.thresholdVoltage):
            # need to stop
            break

        # increment pulse width
        pulse_width = pulse_width + float(gb.testInfo.pulseStep)
        if pulse_width > float(gb.testInfo.pulseStop):
            # end of test - message?
            break

        # display waiting
        label_update = {'type': 'label', 'label_name': 'status', 'value': "Waiting", 'color': "grey85"}
        update_queue.put(label_update)

        # clock out test interval between pulse steps
        start_time = time.time()
        while time.time() - start_time < float(gb.testInfo.testInterval):
            pass

        if stop_flag_callback():
            print("Stop flag triggered")
            abort_flag = True
            break

    # end of main test for loop =================================

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


