"""
mainView.py
    All the screen interfaces


"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import queue
import time
import win32com.client as win32
import os
import bisect

import testRoutines
import globals as gb
from testRoutines import test_pulse
from models import Database
dbase = Database()

# declare instance of dbase class
#dbase=models.DataBase()

# global
#stop_loop = False

# Example using a dictionary
update_label = {'type': 'label', 'label': '','value': '', 'color': 'white'}
update_plot = {'type': 'plot', 'x_data': 0, 'y_data': 0}


class MainWindow(tk.Frame):
    def __init__(self):
        Frame.__init__(self)
        # self.master = master
        self.init_window()



class outputView(tk.Frame):
    """ The main start view """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        # handle "X" button
        self.parent.protocol("WM_DELETE_WINDOW", self.close_window)
        self.additional_params = kwargs
        self.queue = queue.Queue()
        self.done_event = threading.Event()

        self.stop_loop = False
        # Bind Escape to parent window (not the Frame itself)
        self.parent.bind("<Escape>", self.handle_escape)

        # self.testInformation = testInfo()
        self.partList = ()
        self.results = dict()

        self.status_box = StatusBox(self, height=3, max_lines=100)
        self.status_box.grid(column=1, columnspan=3,row=8, padx=5, pady=5, sticky='ew')
        self.status_box.grid_remove()

        # add menus
        # create widgets
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Exit", command=self.close_window)

        optionsmenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Edit", menu=optionsmenu)
        optionsmenu.add_command(label="Settings", command=self.settings_window)
        optionsmenu.add_command(label="Show GPIB Addresses", command=self.gpib_addressing)
        optionsmenu.add_command(label="Debug", command=self.debug_mode)

        helpmenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Instructions", command=self.show_instructions)

        # bar number
        self.barno = tk.StringVar()
        self.barno.set('8850Y')
        ttk.Label(self, text="Bar Number").grid(column=0, row=0, sticky="e", padx=5, pady=(10, 0))
        self.barno_entry = ttk.Entry(self, width=10, textvariable=self.barno, validate='focusout',
                                     validatecommand=self.check_bar_no, font=("TkDefaultFont", 10, "bold"))
        self.barno_entry.grid(column=1, row=0, sticky="we", pady=(10, 0))
        #self.barno_entry.bind("<FocusOut>", self.checkBarNo)
        self.barno_entry.focus()

        # part number
        self.partno = tk.StringVar()
        self.partno.set('950xx')
        ttk.Label(self, text="Part Number").grid(column=2, row=0, padx=5, pady=(5,0),sticky="e")
        self.partno_entry = ttk.Entry(self, width=10, takefocus=0, textvariable=self.partno, font=("TkDefaultFont", 10, "bold"))
        self.partno_entry.grid(column=3, row=0, sticky="we",pady=(5, 0))
        self.partno_entry.config(state="disabled")

        # serial number
        self.serialLabel = ttk.Label(self, text='Serial No.')
        self.serialLabel.grid(column=4, row=0, padx=5, pady=(5, 0), sticky="w")
        self.serialNum = tk.StringVar()
        self.serialNum.set('0')
        ttk.Entry(self, width=6, takefocus=0, textvariable=self.serialNum, font=("TkDefaultFont", 10, "bold")).grid(column=5, row=0, sticky="w", padx=5, pady=5)

        # test status
        self.teststatus = tk.StringVar()
        self.teststatus.set('Idle')
        #test_output().set_label_test_status(self.teststatus)
        self.statusLabel = ttk.Label(self, text=self.teststatus.get(), anchor="center", justify='center', borderwidth=2,
                                     font=('TkDefaultFont', 16), background='grey85')
        self.statusLabel.grid(column=6, row=0, sticky=(tk.W + tk.E), padx=5, pady=5)


        # test frame
        self.test_option = tk.StringVar(value='Standard Test')
        self.option_map = {
            'Standard Test': 1,
            'STX @ 25°C': 2,
            'STX @ 85°C': 3
        }
        testfrm = ttk.LabelFrame(self, text=" Test ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        testfrm.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky="nwe")

        for i, label in enumerate(self.option_map.keys()):
            ttk.Radiobutton(testfrm, text=label, value=label, variable=self.test_option, command=self.on_test_selection
            ).grid(row=i, column=0, sticky="w", padx=10, pady=2)

        ttk.Label(testfrm, text="Confirm voltage and").grid(column=0, row=i+2, sticky="w")
        ttk.Label(testfrm, text="current parameters for").grid(column=0, row=i+3, sticky="w")
        ttk.Label(testfrm, text="each type of test in").grid(column=0, row=i+4, sticky="w")
        ttk.Label(testfrm, text="Edit>Settings").grid(column=0, row=i+5, sticky="w")


        # threshold frame
        thresholdfrm = ttk.LabelFrame(self, text=" Thresholds ",width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        thresholdfrm.grid(column=2, row=1, columnspan=2, padx=10, pady=10, sticky="nwe")
        #thresholdfrm.columnconfigure(0, weight=1)

        self.mintemp = tk.StringVar()
        self.mintemp.set(gb.testInfo.minTemp)
        self.mintemp.trace_add("write", self.on_mintemp_change)
        mintemp_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.mintemp, font=("TkDefaultFont", 10, "bold"))
        mintemp_entry.grid(column=0, row=0, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Min Temp (°C)").grid(column=1, row=0, sticky="w")

        self.maxtemp = tk.StringVar()
        self.maxtemp.set(gb.testInfo.maxTemp)
        self.maxtemp.trace_add("write", self.on_maxtemp_change)
        maxtemp_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.maxtemp, font=("TkDefaultFont", 10, "bold"))
        maxtemp_entry.grid(column=0, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Max Temp (°C)").grid(column=1, row=1, sticky="w")

        self.preheatOn = tk.BooleanVar()
        checkbox = tk.Checkbutton(thresholdfrm, text="Preheat On", variable=self.preheatOn, command=self.on_preheat_change)
        checkbox.grid(row=3, column=0, sticky='w', padx=5, pady=5)

        self.setTemp = tk.StringVar()
        self.setTemp.set(gb.testInfo.setTemp)
        self.setTemp.trace_add("write", self.on_setTemp_change)
        self.setTemp_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.setTemp, font=("TkDefaultFont", 10, "bold"))
        self.setTemp_entry.grid(column=0, row=4, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Set Temp (°C)").grid(column=1, row=4, sticky="w")
        self.setTemp_entry.config(state='disabled')

        self.setTempRange = tk.StringVar()
        self.setTempRange.set(gb.testInfo.setTempRange)
        self.setTempRange.trace_add("write", self.on_setTempRange_change)
        self.setTempRange_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.setTempRange, font=("TkDefaultFont", 10, "bold"))
        self.setTempRange_entry.grid(column=0, row=5, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Set Range (°C)").grid(column=1, row=5, sticky="w")
        self.setTempRange_entry.config(state='disabled')


        # reading frame
        readingfrm = ttk.LabelFrame(self, text=" Readings ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        readingfrm.grid(column=4, row=1, columnspan=4, padx=10, pady=10, sticky="nwe")
        #readingfrm.columnconfigure(0, weight=1)

        self.voltagein = tk.StringVar()
        self.voltagein.set(gb.testData.vin)
        self.voltagein_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.voltagein, font=("TkDefaultFont", 10, "bold"), justify='center')
        self.voltagein_entry.grid(column=0, row=1, padx=(0, 5), pady=5)
        ttk.Label(readingfrm, text="Vin (V)").grid(column=0, row=0)

        self.peakcurrent = tk.StringVar()
        self.peakcurrent.set(gb.testData.ipk)
        self.peakcurrent_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.peakcurrent, font=("TkDefaultFont", 10, "bold"), justify='center')
        self.peakcurrent_entry.grid(column=1, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Ipeak (A)").grid(column=1, row=0)

        self.pulsewidth = tk.StringVar()
        self.pulsewidth.set(gb.testData.pulseWidth)
        self.pulsewidth_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.pulsewidth, font=("TkDefaultFont", 10, "bold"), justify='center')
        self.pulsewidth_entry.grid(column=2, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(readingfrm, text="PulseWidth (μs)").grid(column=2, row=0)

        #self.voltageoutlp = tk.StringVar()
        #self.voltageoutlp.set(gb.testData.voutlp)
        #self.voltageoutlp_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.voltageoutlp)
        #self.voltageoutlp_entry.grid(column=0, row=3, padx=(0, 10), pady=5, sticky="we")
        #ttk.Label(readingfrm, text="Vout@Lp (V))").grid(column=0, row=2)

        self.testtime = tk.StringVar()
        self.testtime.set(gb.testData.testTime)
        self.testtime_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.testtime, font=("TkDefaultFont", 10, "bold"), justify='center')
        self.testtime_entry.grid(column=1, row=3, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Test Time (s)").grid(column=1, row=2)

        gb.testData.finalTemp = gb.thermo.get_measurement(1)
        print(f'temp: {gb.testData.finalTemp}')

        self.finaltemp = tk.StringVar()
        self.finaltemp.set(gb.testData.finalTemp)
        self.finaltemp_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.finaltemp, font=("TkDefaultFont", 10, "bold"), justify='center')
        self.finaltemp_entry.grid(column=2, row=3, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Final Temp (°C)").grid(column=2, row=2)

        self.lpulse = tk.StringVar()
        self.lpulse.set(gb.testData.lpulse)
        self.lpulse_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.lpulse, font=("TkDefaultFont", 10, "bold"), justify='center')
        self.lpulse_entry.grid(column=0, row=5, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Lpulse (μH)").grid(column=0, row=4)

        self.voltageout = tk.StringVar()
        self.voltageout.set(gb.testData.vout)
        self.voltageout_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.voltageout, font=("TkDefaultFont", 10, "bold"), justify='center')
        self.voltageout_entry.grid(column=1, row=5, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Vout (V)").grid(column=1, row=4)

        # initialize button
        self.initButton = (ttk.Button(self, text="Initialize", command=self.initialize))
        self.initButton.grid(column=1, row=7, padx=10, pady=5, sticky=tk.W)

        # start button
        self.startButton = ttk.Button(self, text="Start", command=self.start)
        self.startButton.grid(column=2, row=7, padx=10, pady=5, sticky=tk.E)
        self.startButton.config(state='disabled')

        # test button
        self.testButton = ttk.Button(self, text="Test Part", command=self.test_part)
        self.testButton.grid(column=3, row=7, padx=10, pady=5, sticky=tk.E)
        self.testButton.config(state='disabled')

        # print chart button
        self.ChkTempButton = ttk.Button(self, text="Check Temp", command=self.check_temp)
        self.ChkTempButton.grid(column=4, row=7, padx=10, pady=5, sticky=tk.E)
        #self.chartButton.config(state='disabled')

        # close button
        self.closeButton = ttk.Button(self, text="Close", command=self.close_window)
        self.closeButton.grid(column=5, row=7, padx=10, pady=5, sticky=tk.E)


        self.barno_entry.focus()
        #self.after(100, self.monitor_thread)

    '''
    def check_queue(self):
        try:
            while True:
                data = self.queue.get_nowait()
                self.process_update(data)
        except queue.Empty:
            pass
        self.after(100, self.check_queue)  # Continue checking the queue
    '''

    def handle_escape(self, event=None):
        self.stop_loop = True
        self.statusLabel.config(text='Stopping', background='orange')
        print("Escape key pressed!")

    def monitor_thread(self):
        if not self.queue.empty():
            data = self.queue.get_nowait()
            self.process_update(data)

        if self.done_event.is_set():
            #messagebox.showinfo("Done", "The thread has finished.")
            self.after_test()
        else:
            self.after(50, self.monitor_thread)  # Continue checking the queue

    def check_temp(self):
        gb.testData.finalTemp = gb.thermo.get_measurement(1)
        self.update_label('finaltemp', f"{gb.testData.finalTemp:.1f}", "grey85")
        # check how fast the readings are
        #self.measure_average_time()

    def process_update(self, update):
        if update['type'] == 'label':
            self.update_label(update['label_name'],update['value'], update['color'])

    def update_label(self, label, value, color):
        if label == 'voltagein':
            self.voltagein.set(value)
        elif label == 'pulsewidth':
            self.pulsewidth.set(value)
        elif label == "ipk":
            self.peakcurrent.set(value)
        elif label == "vout":
            self.voltageout.set(value)
        elif label == "testtime":
            self.testtime.set(value)
        elif label == "finaltemp":
            self.finaltemp.set(value)
        elif label == "lpulse":
            self.lpulse.set(value)
        elif label == "voutlp":
            self.voltageoutlp.set(value)
        elif label == 'status':
            #self.teststatus.set(value)
            #gb.testData.status = value
            self.statusLabel.config(text=value, background=color)

    def update_dynamic_line(self, x, y):
        self.line1.set_data(x,y)
        self.canvas.draw()

    def on_mintemp_change(self, *args):
        try:
            gb.testInfo.minTemp = float(self.mintemp.get().strip())
        except ValueError:
            gb.testInfo.minTemp = 0.0

    def on_maxtemp_change(self, *args):
        try:
            gb.testInfo.maxTemp = float(self.maxtemp.get().strip())
        except ValueError:
            gb.testInfo.maxTemp = 0.0

    def on_setTemp_change(self, *args):
        #print(f"setTemp value: '{self.setTemp.get()}'")
        try:
            gb.testInfo.setTemp = float(self.setTemp.get().strip())
        except ValueError:
            gb.testInfo.setTemp = 0.0

    def on_setTempRange_change(self, *args):
        #print(f"setTempRange value: '{self.setTempRange.get()}'")
        try:
            gb.testInfo.setTempRange = float(self.setTempRange.get().strip())
        except ValueError:
            #print("set range to zero.")
            gb.testInfo.setTempRange = 0.0

    def on_preheat_change(self):
        if self.preheatOn.get():
            self.setTemp_entry.config(state='enabled')
            self.setTempRange_entry.config(state='enabled')
            gb.testInfo.preheat = True
        else:
            self.setTemp_entry.config(state='disabled')
            self.setTempRange_entry.config(state='disabled')
            gb.testInfo.preheat = False

    def on_test_selection(self, *args):
        pass


        # subroutines here first
    def do_something(self):
        print("Menu item clicked!")
        # time the thermometer
        start_time = ""

    def measure_average_time(self):
        readings = []
        times = []

        for i in range(10):
            start_time = time.perf_counter()
            reading = gb.thermo.get_measurement(1)
            elapsed = time.perf_counter() - start_time

            readings.append(reading)
            times.append(elapsed)

            print(f"Reading {i + 1}: {reading}, Time: {elapsed:.4f} seconds")

        avg_time = sum(times) / len(times)
        print(f"\nAverage time per measurement: {avg_time:.4f} seconds")

    def settings_window(self):
        newView = SetupView(self)

    def gpib_addressing(self):
        GpibView(self)

    def debug_mode(self):
        if gb.system.debug_mode:
            gb.system.debug_mode = False
            self.master.title("AutoParameters")
            self.status_box.grid_remove()
            print("debugMode OFF")
        else:
            gb.system.debug_mode = True
            self.master.title("AutoParameters - Debug Mode")
            self.status_box.grid()
            print("debugMode ON")

    def show_instructions(self):
        print("showInstructions")
        # open window
        #window = instructionView(self)
        # want to grab so mainview is not changed during testing
        #window.grab_set()

    def close_window(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
            print("Closing window...")
            self.stop_loop = True
            self.parent.quit()
            self.parent.destroy()


    def initialize(self):
        """
        initialize instruments then activate buttons
        :return:
        """
        self.status_box.log("Initialize instruments...")
        # call init_test
        testRoutines.init_test()
        # if error, message and exit
        self.clear_display()
        # activate buttons
        # turn on start, test and set focus
        self.startButton.config(state='enabled')
        # turn off initialize
        self.initButton.config(state='disabled')
        # delay to let instruments catch up
        time.sleep(2)
        print("Done setup")


    def start(self):
        """
        setups up for testing by getting goof parts list, parameters, etc
        :return:
        """
        self.status_box.log("Getting limits...")
        # clears screen
        self.clear_display()
        # gets test limits/parameters
        gb.testLimits = dbase.load_test_limits(self.partno.get())
        self.status_box.log("Getting good parts list...")
        # gets good part list
        self.partList = dbase.get_good_part_list(gb.testInfo.barNum)
        # print(self.partList)
        # display the first part number
        self.serialNum.set(self.partList[0])
        gb.testInfo.position = self.partList[0]
        #gb.testInfo.serialNumber = self.make_serial_number()
        #gb.testInfo.fileName = f"{gb.testInfo.barNum}{gb.testInfo.designNum}x{gb.testInfo.position}.csv"
        self.next_part_idx = 0
        self.endFlag = False
        self.statusLabel.config(text="Ready", background="gray85")
        # turn off start
        self.startButton.config(state='disabled')
        # turn on test
        self.testButton.config(state='enabled')
        print('ready to test')

    def test_part(self):
        """
        tests a part
        :return:
        """

        # reset
        self.stop_loop = False

        # test for endFlag
        if self.endFlag:
            messagebox.showwarning(title='Pulse Inductance Testing', message='All the parts in the bar have been tested. Start a new bar.')
            return

        # check if part number entered is different from indexed
        #print(f"serialNum: {self.serialNum.get()}, partlist s/n: {self.partList[self.next_part_idx]}, testInfoPos: { gb.testInfo.position}")
        if  self.serialNum.get() != self.partList[self.next_part_idx]:
            gb.testInfo.position = self.serialNum.get()
            # find index of next testable part in partlist after serial number given
            # minus 1 because it will be incremented later
            self.next_part_idx = bisect.bisect_right(self.partList, self.serialNum.get()) - 1

        # make serial number
        gb.testInfo.serialNumber = self.make_serial_number()

        self.testButton.config(state='disabled')
        self.serialLabel.config(text="Testing Serial No.")

        # clear test result fields
        self.clear_display()

        # status
        self.statusLabel.config(text="Testing", background="yellow")
        self.statusLabel.update_idletasks()

        # run test with reference to this instance
        self.status_box.log("Starting test...")
        self.done_event.clear()
        self.test_thread = threading.Thread(target=test_pulse, args=(self.queue, self.done_event, self.check_stop_flag, self.preheatOn), daemon=True)
        self.test_thread.start()
        self.after(100, self.monitor_thread)
        # self.check_thread()

        # Check if the thread is alive
        #while self.test_thread.is_alive():
        #    print("Thread is still running...")
        #    time.sleep(1)


        #self.status_flag = test_output(self)

        #if not self.status_flag:

        #self.status_flag = self.check_output_limits(fail_flag)

        #print(f"statusFlag after Output Limits {self.status_flag}")
        #if failFlag in {30, 31, 32, 33, 34, 35}:
        #    messagebox.showwarning(title='Output Testing', message='Not able to complete the test. Check part.')


    def check_stop_flag(self):
        return self.stop_loop

    def after_test(self):

        #print("after_test")
        self.status_box.log("After test...")
        # todo this is ready to use - not sure  - copied from hipot
        # before saving check test history
        """
        self.status_box.log("Checking historyt...")
        history = db.check_test_history(self.make_serial_number())
        print (history)
        if history[0] is None or history[0] == 0 or history[0] < 3:
            # this is first time through
            # update tested code to 3 which is hipot's number
            db.record_tested(3, self.make_serial_number())
        else:
            if history[1] is None or history[1] == 0:
                # this is first time - set history code
                db.record_history(1, self.make_serial_number())
            # there is previous history or first time
            # copy data to testHistory
            db.copy_data_row(self.make_serial_number())
        """

        #4 regardless pass or fail save data and status
        # standard or STx25
        if self.option_map[self.test_option.get()] == 1 or  self.option_map[self.test_option.get()] == 2:
            dbase.record_pulse_25_data(gb.testInfo.serialNumber)
        # STX85
        elif  self.option_map[self.test_option.get()] == 3:
            dbase.record_pulse_85_data(gb.testInfo.serialNumber)

        #5 issue pass/fail signal - not needed here
        #if self.status_flag:
        #    self.statusLabel.config(text=("MV-Fail"), background="red")
        #else:
        #    self.statusLabel.config(text=("MV-Pass"), background="green")

        #6 advance serial number and check for end
        # check for skip - that is parts that failed parameters
        # increment partlist index
        self.next_part_idx += 1
        # test for the end because end of bar may not be the last part
        #print(f"nextPartIndex: {self.next_part_idx}, listLength: {len(self.partList)}")

        # check for end of array partList because it may not be last part
        # and the next part may not be the next serial number
        # check for end of bar
        if self.next_part_idx >= len(self.partList):
            # if end go back to bar
            print('End of bar')
            # ser = int(gb.testInfo.numPositions)
            messagebox.showwarning(title='Output Testing', message='All the parts in the bar have been tested')
            # do something to reset
            self.barno_entry.focus()
            self.barno_entry.bind("<FocusOut>", self.check_bar_no)
            self.testButton.config(state='disabled')
            self.startButton.config(state='enabled')
            self.endFlag = True
        else:
            # show next serial num
            self.serialLabel.config(text="Next Serial No.")
            self.serialNum.set(self.partList[self.next_part_idx])
            gb.testInfo.position = self.partList[self.next_part_idx]
            self.testButton.config(state='enabled')
        #else:
            self.statusLabel.config(text="Ready", background="gray85")



    # todo - remove - not used
    def check_thread(self):
        if self.test_thread.is_alive():
            self.after(500, self.check_thread)
            print("thread alive")
        else:
            print("thread finished")

    def update_status(self, new_text, background_color):
        self.statusLabel.config(text = new_text, background = background_color)

    def update_data(self):
        # from TestRoutines import update_display_values
        pass

    def check_part_no(self):
        """
        gets part number based on bar number
        :return:
        """
        designNum = dbase.check_design_num(self.partno.get())
        self.design.set(designNum)
        print('Design Num: ', designNum)
        return False

    def check_bar_no(self, event=None):
        """
        cannot be empty, needs an upper case 'Y'
        :return:
        """
        if len(self.barno.get()) < 4:
            messagebox.showerror(title="Input", message="Bar number is incomplete. Not enough characters.")
            # focus needs to return to entry
            self.barno_entry.focus_set()
            return

        # check for 'Y' and add if missing
        self.bar = self.barno.get()
        self.bar = self.bar.upper()
        if not self.bar.endswith('Y'):
            # add capital 'Y'
            self.bar += 'Y'

        self.barno.set(self.bar)
        gb.testInfo.barNum =self.barno.get()

        # check bar number in database
        #if not dbase.check_record_exists(self.bar):
        #    messagebox.showerror(title="Bar No", message="Bar number do does not exist in database. ")
        #    return

        # get part number from database
        if not dbase.get_part_number_for_bar(self.bar):
            messagebox.showerror(title="Bar No", message="Bar number do does not exist in database. ")
            return
        else:
            # display part number
            self.partno.set(gb.testInfo.partNum)

        self.initButton.focus_set()
        return

    def check_interval(self):
        # want to limit to 60 sec
        if int(self.testinterval.get()) > 60:
            messagebox.showerror(title="Test Interval", message="Test interval limited to maximum 60 seconds")
            return

    def check_output_limits(self, flag):


        pass

    def make_serial_number(self):
        """
        creates serial number from bar no and position number including leading zero padding
        :return:
        """
        # get the current serial number and pad with leading zeros
        if len(self.serialNum.get()) < 2:
            paddedSerialNo = f"{gb.testInfo.barNum}00{self.serialNum.get()}"
        elif len(self.serialNum.get()) < 3:
            paddedSerialNo = f"{gb.testInfo.barNum}0{self.serialNum.get()}"
        else:
            paddedSerialNo = f"{gb.testInfo.barNum}{self.serialNum.get()}"

        #print(f"padded serial no: {paddedSerialNo}")
        return paddedSerialNo


    def clear_display(self):
        # clear output valves
        self.voltagein.set('')
        self.peakcurrent.set('')
        self.pulsewidth.set('')
        self.testtime.set('')
        self.finaltemp.set('')
        self.lpulse.set('')
        self.voltageout.set('')

    def print_test_info(self):
        # dumps testinno for checking
        print("Instance Attributes and Their Values:")
        for attr in dir(gb.testInfo):
            if not attr.startswith("__"):  # Filter out special methods
                value = getattr(gb.testInfo, attr)
                print(f"{attr}: {value}")



class SetupView(tk.Toplevel):
    """
    Defines window for for instrument settings and board settings
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create a new top-level window
        self.title('Setup Settings')
        self.geometry("700x625+250+300")
        self.style = ttk.Style()
        self.style.configure("Normal", bg="white")
        self.style.configure("Error", bg="red")


        # base path
        self.basepath = tk.StringVar()
        # todo - basepath should be an init variable
        self.basepath.set('N:\\PD0013\\Design\\LTCC')
        ttk.Label(self, text="Base Path:").grid(column=0, row=0, sticky="e", padx=(5,5), pady=(10, 0))
        self.basepath_entry = ttk.Entry(self, width=50, textvariable=self.basepath, validate='focusout')
        self.basepath_entry.grid(column=1, columnspan=3, row=0, sticky="w", pady=(10, 0))
        gb.testInfo.filePath = self.basepath.get()
        # todo - the path should be checked when focusout


        # pulse generator frame
        pulsefrm = ttk.LabelFrame(self, text=" Pulse Generator ", width=175, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        pulsefrm.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky="nwe")
        #pulsefrm.columnconfigure(0, weight=1)

        self.pulse_gen_period = tk.StringVar()
        self.pulse_gen_period.set(gb.testInfo.pulsePeriod)
        self.pulse_gen_period.trace_add("write", self.on_pulse_gen_period_change)
        pulse_gen_period = ttk.Entry(pulsefrm, width=7, textvariable=self.pulse_gen_period)
        pulse_gen_period.grid(column=0, row=0, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(pulsefrm, text="Period").grid(column=1, row=0, sticky="w")

        self.pulse_gen_stop_width = tk.StringVar()
        self.pulse_gen_stop_width.set(gb.testInfo.pulseStop)
        self.pulse_gen_stop_width.trace_add("write", self.on_pulse_gen_stop_width_change)
        pulse_gen_stop_width_entry = ttk.Entry(pulsefrm, width=7, textvariable=self.pulse_gen_stop_width)
        pulse_gen_stop_width_entry.grid(column=0, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(pulsefrm, text="Stop Width").grid(column=1, row=1, sticky="w")


        self.pulse_gen_units = tk.StringVar()
        self.pulse_gen_units.set(gb.testInfo.pulseUnits)
        self.pulse_gen_units.trace_add("write", self.on_pulse_gen_units_change)
        pulse_gen_units_entry = ttk.Entry(pulsefrm, width=7, textvariable=self.pulse_gen_units)
        pulse_gen_units_entry.grid(column=0, row=2, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(pulsefrm, text="Units").grid(column=1, row=2, sticky="w")



        # scanner frame
        scannerfrm = ttk.LabelFrame(self, text=" Scanner/Meter ", width=175, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        scannerfrm.grid(column=3, row=1, columnspan=2, padx=10, pady=10, sticky="nwe")
        #scannerfrm.columnconfigure(0, weight=1)

        self.scanner_temp_type = tk.StringVar()
        self.scanner_temp_type.set(gb.testInfo.tempType)
        self.scanner_temp_type.trace_add("write", self.on_scanner_temp_type_change)
        scanner_temp_type_entry = ttk.Entry(scannerfrm, width=7, textvariable=self.scanner_temp_type)
        scanner_temp_type_entry.grid(column=0, row=0, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scannerfrm, text="Thermo Type").grid(column=1, row=0, sticky="w")


        self.scanner_temp_chan = tk.StringVar()
        self.scanner_temp_chan.set(gb.testInfo.tempChan)
        self.scanner_temp_chan.trace_add("write", self.on_scanner_temp_chan_change)
        scanner_temp_chan_entry = ttk.Entry(scannerfrm, width=7, textvariable=self.scanner_temp_chan)
        scanner_temp_chan_entry.grid(column=0, row=1, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scannerfrm, text="Temp Chan").grid(column=1, row=1, sticky="w")


        # scope frame
        scopefrm = ttk.LabelFrame(self, text=" Oscilloscope ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        scopefrm.grid(column=5, row=1, columnspan=2, padx=10, pady=10, sticky="nwe")
        #scopefrm.columnconfigure(0, weight=3)


        self.scope_current_chan = tk.StringVar()
        self.scope_current_chan.set(gb.testInfo.currentChan)
        self.scope_current_chan.trace_add("write", self.on_scope_current_chan_change)
        scope_current_chan_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_current_chan)
        scope_current_chan_entry.grid(column=0, row=0, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Current Chan").grid(column=1, row=0, sticky="w")

        self.scope_current_scale = tk.StringVar()
        self.scope_current_scale.set(gb.testInfo.currentScale)
        self.scope_current_scale.trace_add("write", self.on_scope_current_scale_change)
        scope_current_scale_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_current_scale)
        scope_current_scale_entry.grid(column=0, row=1, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Current V/div").grid(column=1, row=1, sticky="w")


        # power supply frame
        powerfrm = ttk.LabelFrame(self, text=" Power Supply ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        powerfrm.grid(column=5, row=2, columnspan=2, padx=10, pady=10, sticky="nwe")
        #scopefrm.columnconfigure(0, weight=3)

        self.power_voltage = tk.StringVar()
        self.power_voltage.set(gb.testInfo.vin)
        self.power_voltage.trace_add("write", self.on_power_voltage_change)
        power_voltage_entry = ttk.Entry(powerfrm, width=7, textvariable=self.power_voltage)
        power_voltage_entry.grid(column=0, row=0, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(powerfrm, text="CH1 Voltage").grid(column=1, row=0, sticky="w")

        self.power_current = tk.StringVar()
        self.power_current.set(gb.testInfo.currentLimit)
        self.power_current.trace_add("write", self.on_power_current_change)
        power_current_entry = ttk.Entry(powerfrm, width=7, textvariable=self.power_current)
        power_current_entry.grid(column=0, row=1, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(powerfrm, text="CH1 Current").grid(column=1, row=1, sticky="w")

        self.power_voltage_2 = tk.StringVar()
        self.power_voltage_2.set(gb.testInfo.vaux)
        self.power_voltage_2.trace_add("write", self.on_power_voltage_2_change)
        power_voltage_entry_2 = ttk.Entry(powerfrm, width=7, textvariable=self.power_voltage_2)
        power_voltage_entry_2.grid(column=0, row=2, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(powerfrm, text="CH2 Voltage").grid(column=1, row=2, sticky="w")

        self.power_current_2 = tk.StringVar()
        self.power_current_2.set(gb.testInfo.iaux)
        self.power_current_2.trace_add("write", self.on_power_current_2_change)
        power_current_entry_2 = ttk.Entry(powerfrm, width=7, textvariable=self.power_current_2)
        power_current_entry_2.grid(column=0, row=3, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(powerfrm, text="CH2 Current").grid(column=1, row=3, sticky="w")


        # voltage divider ratio frame
        self.voltage_option = tk.StringVar()
        self.voltage_option.set('1200V')
        self.voltage_ratio = tk.StringVar()
        self.voltage_ratio.set(gb.testInfo.voltageRatio)

        voltagefrm = ttk.LabelFrame(self, text=" Voltage Divider Ratio ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        voltagefrm.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky="nwe")
        #voltagefrm.columnconfigure(0, weight=1)

        ttk.Radiobutton(voltagefrm, text='1200 V (178 k)', variable=self.voltage_option, value='1200V',
                        command=self.voltage_ratio).grid(column=0, row=0, padx=20, sticky=tk.W)

        ttk.Radiobutton(voltagefrm, text='1400 V (150 k)', variable=self.voltage_option, value='1400V',
                        command=self.voltage_ratio).grid(column=0, row=1, padx=20, sticky=tk.W)

        ttk.Radiobutton(voltagefrm, text='2000 V (249 k)', variable=self.voltage_option, value='2000V',
                        command=self.voltage_ratio).grid(column=0, row=2, padx=20, sticky=tk.W)

        ttk.Radiobutton(voltagefrm, text='Other', variable=self.voltage_option, value='Other',
                        command=self.voltage_other).grid(column=0, row=3, padx=20, sticky=tk.W)

        self.voltage_option_map = {
            '1200 V (178 k)': '1200V',
            '1400 V (150 k)': '1400V',
            '2000 V (249 k)': '2000V',
            'Other': 'Other'
        }

        self.voltage_ratio = tk.StringVar()
        self.voltage_ratio.set(gb.testInfo.voltageRatio)
        self.voltage_ratio_entry = ttk.Entry(voltagefrm, width=7, textvariable=self.voltage_ratio)
        self.voltage_ratio_entry.grid(column=0, row=4, padx=(0, 10), pady=5, sticky="we")
        self.voltage_ratio_entry.config(state="disabled")
        ttk.Label(voltagefrm, text="V/1V").grid(column=1, row=4, sticky="w")

        # current probe frame
        self.current_option = tk.StringVar(value='1.5 A (0.604R)')
        self.current_scale = tk.StringVar()
        self.current_scale.set(gb.testInfo.currentRatio)
        self.option_map = {
            '1.5 A (0.604R)': 597,
            '2.4 A (0.374R)': 371,
            '2.7 A (0.332R)': 330,   # was 328 but calc'd value is 330
            'Other': None
        }
        currentfrm = ttk.LabelFrame(self, text=" Current Measurement ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        currentfrm.grid(column=3, row=2, columnspan=2, padx=10, pady=10, sticky="nwe")
        #currentfrm.columnconfigure(0, weight=1)

        for i, label in enumerate(self.option_map.keys()):
            ttk.Radiobutton(currentfrm, text=label, value=label, variable=self.current_option, command=self.on_current_selection
            ).grid(row=i, column=0, sticky="w", padx=10, pady=2)

        self.current_scale_entry = ttk.Entry(currentfrm, width=7)
        self.current_scale_entry.grid(column=0, row=5, padx=(0, 10), pady=5, sticky="we")
        self.current_scale_entry.insert(0, str(self.option_map['2.7 A (0.332R)']))
        self.current_scale_entry.config(state="disabled")
        ttk.Label(currentfrm, text="mV/A").grid(column=1, row=5, sticky="w")


        # Add a button to save settings and close the window
        ttk.Button(self, text="Close", command=self.destroy).grid(column=5, row=3, padx=10, pady=10, sticky="we")

        # Make the setup window modal (it stays on top and blocks interaction with the main window)
        #self.transient(root)
        self.grab_set()
        #root.wait_window(self)
        # how big is the window?
        # can it lay overtop of the main window?

    def check_path(self):
        pass

    def on_pulse_gen_period_change(self, *args):
        gb.testInfo.pulsePeriod = self.pulse_gen_period.get()

    def on_pulse_gen_start_width_change(self, *args):
        gb.testInfo.pulseStart = self.pulse_gen_start_width.get()

    def on_pulse_gen_stop_width_change(self, *args):
        gb.testInfo.pulseStop = self.pulse_gen_stop_width.get()

    def on_pulse_gen_step_change(self, *args):
        gb.testInfo.pulseStep = self.pulse_gen_step.get()

    def on_pulse_gen_units_change(self, *args):
        gb.testInfo.pulseUnits = self.pulse_gen_units.get()

    def on_scanner_temp_type_change(self, *args):
        gb.testInfo.tempType = self.scanner_temp_type.get()

    def on_scanner_temp_chan_change(self, *args):
        gb.testInfo.tempChan = self.scanner_temp_chan.get()

    def on_scanner_vin_chan_change(self, *args):
        gb.testInfo.vinChan = self.scanner_vin_chan.get()

    def on_scanner_vout_chan_change(self, *args):
        gb.testInfo.voutChan = self.scanner_vout_chan.get()

    def on_scope_vdss_chan_change(self, *args):
        gb.testInfo.vdssChan = self.scope_vdss_chan.get()

    def on_scope_vdss_scale_change(self, *args):
        gb.testInfo.vdssScale = self.scope_vdss_scale.get()

    def on_scope_current_chan_change(self, *args):
        gb.testInfo.currentChan = self.scope_current_chan.get()

    def on_scope_current_scale_change(self, *args):
        gb.testInfo.currentScale = self.scope_current_scale.get()

    def on_scope_vout_chan_change(self, *args):
        gb.testInfo.voutChan = self.scope_vout_chan.get()

    def on_scope_vout_scale_change(self, *args):
        gb.testInfo.voutScale = self.scope_vout_scale.get()

    def on_power_voltage_change(self, *args):
        gb.testInfo.vin = self.power_voltage.get()

    def on_power_current_change(self, *args):
        gb.testInfo.currentLimit = self.power_current.get()

    def on_power_voltage_2_change(self, *args):
        gb.testInfo.vaux = self.power_voltage.get()

    def on_power_current_2_change(self, *args):
        gb.testInfo.iaux = self.power_current.get()

    def on_current_selection(self):
        selected_label = self.current_option.get()

        if selected_label == "Other":
            self.current_scale_entry.config(state="normal")
        else:
            # Get corresponding value from the map
            value = self.option_map[selected_label]
            self.current_scale_entry.config(state="normal")  # enable to insert
            self.current_scale_entry.delete(0, tk.END)
            self.current_scale_entry.insert(0, str(value))
            self.current_scale_entry.config(state="readonly")  # prevent edits for fixed values
        gb.testInfo.currentRatio = self.current_scale_entry.get()
        gb.testInfo.currentProbe = self.current_option.get()
        print(f'currentRatio: {gb.testInfo.currentRatio}')

    def current_option(self):
        # here update current ratio test box but leave gray
        #self.current_scale_entry.config(state="disabled")
        if self.current_option == '27A':
            self.current_scale.set(1)
        elif self.current_option == 'TCP202':
            self.current_scale.set(2)
        elif self.current_option == 'P6021':
            self.current_scale.set(3)
        gb.testInfo.currentRatio = self.current_scale.get()
        gb.testInfo.currentProbe = self.current_option.get()
        print(f'currentRatio1: {gb.testInfo.currentRatio}')

    def current_other(self):
        # here activate other text box
        self.current_scale_entry.config(state="enabled")
        gb.testInfo.currentRatio = self.current_scale.get()
        print(f'currentRatio2: {gb.testInfo.currentRatio}')

    def voltage_ratio(self):
        # here update current ratio test box but leave gray
        self.voltage_ratio_entry.config(state="disabled")
        gb.testInfo.voltageRatio = self.voltage_ratio.get()

    def voltage_other(self):
        # here activate other text box
        self.voltage_ratio_entry.config(state="enabled")
        gb.testInfo.voltageRatio = self.voltage_ratio.get()

class GpibView(tk.Toplevel):
    """
    Defines window for for instrument settings and board settings
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create a new top-level window
        self.title('GPIB Addressing')
        self.geometry("400x250+250+300")
        self.style = ttk.Style()
        self.style.configure("Normal", bg="white")
        self.style.configure("Error", bg="red")

        ttk.Label(self, text="Oscilloscope").grid(column=0, row=0, padx=(10,0), sticky="w")
        ttk.Label(self, text=gb.initValues.scopeMeter).grid(column=1, row=1, padx=(10, 0), sticky="e")
        ttk.Label(self, text=gb.initValues.scopeAdr).grid(column=2, row=1, padx=(10, 0), sticky="w")

        ttk.Label(self, text="Signal Generator").grid(column=0, row=2, padx=(10,0), sticky="w")
        ttk.Label(self, text=gb.initValues.sigGen).grid(column=1, row=3, padx=(10, 0), sticky="e")
        ttk.Label(self, text=gb.initValues.sigGenAdr).grid(column=2, row=3, padx=(10, 0), sticky="w")

        ttk.Label(self, text="Power Supply").grid(column=0, row=4, padx=(10,0), sticky="w")
        ttk.Label(self, text=gb.initValues.powerUnit).grid(column=1, row=5, padx=(10, 0), sticky="e")
        ttk.Label(self, text=gb.initValues.powerAdr).grid(column=2, row=5, padx=(10, 0), sticky="w")

        ttk.Label(self, text="Thermo Unit").grid(column=0, row=6, padx=(10,0), sticky="w")
        ttk.Label(self, text=gb.initValues.thermoUnit).grid(column=1, row=7, padx=(10, 0), sticky="e")
        ttk.Label(self, text=gb.initValues.thermoAdr).grid(column=2, row=7, padx=(10, 0), sticky="w")

        # Add a button to save settings and close the window
        ttk.Button(self, text="Close", command=self.destroy).grid(column=2, row=8, padx=10, pady=10, sticky="we")



class StatusBox(ttk.Frame):
    def __init__(self, parent, height=3, max_lines=100, **kwargs):
        super().__init__(parent, **kwargs)

        self.max_lines = max_lines

        # Listbox to show one message per line
        self.listbox = tk.Listbox(
            self,
            height=height,          # visible lines
            activestyle='none'
        )
        self.listbox.grid(row=0, column=0, sticky="nsew")

        # Vertical scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Make listbox expand inside this frame
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def log(self, msg: str):
        """Add a new status message at the TOP (index 0)."""
        # Insert at top
        self.listbox.insert(tk.END, msg)

        # Enforce rolling buffer size
        if self.listbox.size() > self.max_lines:
            # Delete last (oldest) line
            self.listbox.delete(0)

        # Scroll to the newest message
        self.listbox.see(tk.END)

    def clear(self):
        """Clear all messages."""
        self.listbox.delete(0, tk.END)



