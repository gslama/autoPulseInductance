"""
MainView.py
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



#import TestRoutines
import models
import TestRoutines
import globals as gb
import os

from TestRoutines import test_output

# declare instance of dbase class
dbase=models.DataBase()

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

        # add menus
        # create widgets
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Exit", command=self.close_window)
        menubar.add_cascade(label="File", menu=filemenu)

        optionsmenu = tk.Menu(menubar, tearoff=False)
        optionsmenu.add_command(label="Settings", command=self.settings_window)
        optionsmenu.add_command(label="GPIB Addressing", command=self.gpib_addressing)
        optionsmenu.add_command(label="Debug", command=self.debug_mode)
        menubar.add_cascade(label="Options", menu=optionsmenu)

        helpmenu = tk.Menu(menubar, tearoff=False)
        helpmenu.add_command(label="About", command=self.show_about)
        helpmenu.add_command(label="Instructions", command=self.show_instructions)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # bar number
        self.barno = tk.StringVar()
        self.barno.set('8850Y')
        ttk.Label(self, text="Bar Number").grid(column=0, row=0, sticky="e", padx=5, pady=(10, 0))
        self.barno_entry = ttk.Entry(self, width=10, textvariable=self.barno, validate='focusout',
                                     validatecommand=self.check_bar_no)
        self.barno_entry.grid(column=1, row=0, sticky="we", pady=(10, 0))
        #self.barno_entry.bind("<FocusOut>", self.checkBarNo)
        self.barno_entry.focus()

        # part number
        self.partno = tk.StringVar()
        self.partno.set('950xx')
        ttk.Label(self, text="Part Number").grid(column=2, row=0, padx=5, pady=(5,0),sticky="e")
        self.partno_entry = ttk.Entry(self, width=10, takefocus=0, textvariable=self.partno)
        self.partno_entry.grid(column=3, row=0, sticky="we",pady=(5, 0))
        self.partno_entry.config(state="disabled")

        # serial number
        self.serialLabel = ttk.Label(self, text='Serial No.')
        self.serialLabel.grid(column=4, row=0, padx=5, pady=(5, 0), sticky="w")
        self.serialNum = tk.StringVar()
        self.serialNum.set('0')
        ttk.Entry(self, width=6, takefocus=0, textvariable=self.serialNum).grid(column=5, row=0, sticky="w", padx=5, pady=5)

        # test status
        self.teststatus = tk.StringVar()
        self.teststatus.set('Idle')
        #test_output().set_label_test_status(self.teststatus)
        self.statusLabel = ttk.Label(self, text=self.teststatus.get(), anchor="center", justify='center', borderwidth=2,
                                     font=('TkDefaultFont', 16), background='grey85')
        self.statusLabel.grid(column=6, row=0, sticky=(tk.W + tk.E), padx=5, pady=5)


        # timer frame
        timerfrm = ttk.LabelFrame(self, text=" Timer ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        timerfrm.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky="nwe")
        #timerfrm.columnconfigure(0, weight=1)

        self.testinterval = tk.StringVar()
        self.testinterval.set(gb.testInfo.testInterval)
        self.testinterval.trace_add("write", self.on_testinterval_change)
        testinterval_entry = ttk.Entry(timerfrm, width=7, textvariable=self.testinterval, validate='focusout',
                                     validatecommand=self.check_interval)
        testinterval_entry.grid(column=0, row=0, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(timerfrm, text="Test Interval (s)").grid(column=1, row=0, sticky="w")

        self.setcurrent = tk.StringVar()
        self.setcurrent.set(gb.testInfo.testCurrent)
        self.setcurrent.trace_add("write", self.on_setcurrent_change)
        setcurrent_entry = ttk.Entry(timerfrm, width=7, textvariable=self.setcurrent)
        setcurrent_entry.grid(column=0, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(timerfrm, text="Set Current (A)").grid(column=1, row=1, sticky="w")

        self.lpulsecurrent = tk.StringVar()
        self.lpulsecurrent.set(gb.testInfo.lpulseCurrent)
        self.lpulsecurrent.trace_add("write", self.on_lpulsecurrent_change)
        lpulsecurrent_entry = ttk.Entry(timerfrm, width=7, textvariable=self.lpulsecurrent)
        lpulsecurrent_entry.grid(column=0, row=4, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(timerfrm, text="Lpulse Current (A)").grid(column=1, row=4, sticky="w")


        # threshold frame
        thresholdfrm = ttk.LabelFrame(self, text=" Thresholds ",width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        thresholdfrm.grid(column=2, row=1, columnspan=2, padx=10, pady=10, sticky="nwe")
        #thresholdfrm.columnconfigure(0, weight=1)

        self.mintemp = tk.StringVar()
        self.mintemp.set(gb.testInfo.minTemp)
        self.mintemp.trace_add("write", self.on_mintemp_change)
        mintemp_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.mintemp)
        mintemp_entry.grid(column=0, row=0, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Min Temp (C)").grid(column=1, row=0, sticky="w")

        self.maxtemp = tk.StringVar()
        self.maxtemp.set(gb.testInfo.maxTemp)
        self.maxtemp.trace_add("write", self.on_maxtemp_change)
        maxtemp_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.maxtemp)
        maxtemp_entry.grid(column=0, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Max Temp (C)").grid(column=1, row=1, sticky="w")

        self.currentlimit = tk.StringVar()
        self.currentlimit.set(gb.testInfo.thresholdCurrent)
        self.currentlimit.trace_add("write", self.on_currentlimit_change)
        currentlimit_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.currentlimit)
        currentlimit_entry.grid(column=0, row=3, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Current Limit (A)").grid(column=1, row=3, sticky="w")

        self.voltagelimit = tk.StringVar()
        self.voltagelimit.set(gb.testInfo.thresholdVoltage)
        self.voltagelimit.trace_add("write", self.on_voltagelimit_change)
        voltagelimit_entry = ttk.Entry(thresholdfrm, width=7, textvariable=self.voltagelimit)
        voltagelimit_entry.grid(column=0, row=4, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(thresholdfrm, text="Voltage Limit (V)").grid(column=1, row=4, sticky="w")


        # reading frame
        readingfrm = ttk.LabelFrame(self, text=" Readings ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        readingfrm.grid(column=4, row=1, columnspan=4, padx=10, pady=10, sticky="nwe")
        #readingfrm.columnconfigure(0, weight=1)

        self.voltagein = tk.StringVar()
        self.voltagein.set(gb.testData.vin)
        self.voltagein_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.voltagein)
        self.voltagein_entry.grid(column=0, row=1, padx=(0, 5), pady=5)
        ttk.Label(readingfrm, text="Vin (V)").grid(column=0, row=0)

        self.peakcurrent = tk.StringVar()
        self.peakcurrent.set(gb.testData.ipk)
        self.peakcurrent_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.peakcurrent)
        self.peakcurrent_entry.grid(column=1, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Ipeak (A)").grid(column=1, row=0)

        self.pulsewidth = tk.StringVar()
        self.pulsewidth.set(gb.testData.pulseWidth)
        self.pulsewidth_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.pulsewidth)
        self.pulsewidth_entry.grid(column=2, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(readingfrm, text="PulseWidth (us)").grid(column=2, row=0)

        self.voltageoutlp = tk.StringVar()
        self.voltageoutlp.set(gb.testData.voutlp)
        self.voltageoutlp_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.voltageoutlp)
        self.voltageoutlp_entry.grid(column=0, row=3, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Vout@Lp (V))").grid(column=0, row=2)

        self.testtime = tk.StringVar()
        self.testtime.set(gb.testData.testTime)
        self.testtime_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.testtime)
        self.testtime_entry.grid(column=1, row=3, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Test Time (s))").grid(column=1, row=2)

        self.finaltemp = tk.StringVar()
        self.finaltemp.set(gb.testData.finalTemp)
        self.finaltemp_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.finaltemp)
        self.finaltemp_entry.grid(column=2, row=3, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Final Temp (C))").grid(column=2, row=2)

        self.lpulse = tk.StringVar()
        self.lpulse.set(gb.testData.lpulseSpecific)
        self.lpulse_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.lpulse)
        self.lpulse_entry.grid(column=0, row=5, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Lpulse (uH)").grid(column=0, row=4)

        self.voltageout = tk.StringVar()
        self.voltageout.set(gb.testData.vout)
        self.voltageout_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.voltageout)
        self.voltageout_entry.grid(column=1, row=5, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Vout (V)").grid(column=1, row=4)

        self.vdss = tk.StringVar()
        self.vdss.set(gb.testData.vdss)
        self.vdss_entry = ttk.Entry(readingfrm, takefocus=0, width=10, textvariable=self.vdss)
        self.vdss_entry.grid(column=2, row=5, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(readingfrm, text="Vdss (V)").grid(column=2, row=4)


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
        self.chartButton = ttk.Button(self, text="Print Chart", command=self.print_chart)
        self.chartButton.grid(column=4, row=7, padx=10, pady=5, sticky=tk.E)
        #self.chartButton.config(state='disabled')

        # close button
        self.closeButton = ttk.Button(self, text="Close", command=self.close_window)
        self.closeButton.grid(column=5, row=7, padx=10, pady=5, sticky=tk.E)


        # Create a frame for the chart
        #frame = ttk.LabelFrame(self, text=" Output Chart ", width=450, height=200, relief='raised', borderwidth=20)
        #frame.grid(column=0, row=8, columnspan=6, padx=10, pady=10)
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.grid(column=0, row=8, columnspan=6, padx=10, pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0)

        # Create a Matplotlib Figure object
        #self.fig = Figure(figsize=(5, 4), dpi=100)
        #self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Output Voltage Plot")
        self.ax.set_xlabel("Current (A)")
        self.ax.set_ylabel("Voltage (kV)")
        #self.ax.legend()
        self.ax.set_xlim(0, 4)  # Fix the x-axis from 0 to 4
        self.ax.set_ylim(0, 2)  # Fix the y-axis from 0 to 2

        # Embed the figure in the Tkinter Frame
        #self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        #self.canvas.draw()
        #self.canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0)

        # Plot data (example: simple line plot)
        self.x_data1 = []
        self.y_data1 = []

        # Initial data for the second plot reference line
        # means at 0.6 A s/b 400 V and at 2.8 A s/b 1600 V
        self.x_data2 = [0.6, 2.8]
        self.y_data2 = [0.4, 1.6]

        # Create a matplotlib figure
        #plt.ion()
        #fig, ax = plt.subplots()
        self.line1, = self.ax.plot(self.x_data1, self.y_data1, marker='o', label="Actual", color="blue")  # First plot line
        self.line2, = self.ax.plot(self.x_data2, self.y_data2, label="Min Line", color="green")  # Second plot line
        self.ax.legend()


        self.update_plot_1(0,0)
        #self.update_plot(1, 0.5)
        #self.update_plot(2, 1)
        #self.update_plot(2.5, 1.5)


        #fig = Figure(figsize=(6, 4), dpi=100)
        #ax = fig.add_subplot(111)

        #ax.plot(x, y)
        #set plot limits
        #ax.set_xlim(0, 4)  # Fix the x-axis from 0 to 4
        #ax.set_ylim(0, 2)  # Fix the y-axis from 0 to 2

        # Set title and labels
        #ax.set_title("Sample Line Plot")
        #ax.set_xlabel("Current (A)")
        #ax.set_ylabel("Voltage (kV)")
        #ax.legend()

        # Create a canvas for the figure in tkinter
        #canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        # Display the canvas in the tkinter window
        #canvas_widget = canvas.get_tk_widget()
        #canvas_widget.grid()

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

    def print_chart(self):
        # test values
        #C:\Users\gslam\Dropbox\SlamaTech\Consulting\AUTO Programs Python\Test Data\Output_Test\Auto Output Chart r3.xlsm
        #C:\Users\gslam\Dropbox\SlamaTech\Consulting\AUTO Programs Python\AutoOutput\Test Data\Output_Test\3509y
        base_path = r"C:\Users\gslam\Dropbox\SlamaTech\Consulting\AUTO Programs Python\AutoOutput"
        bar_num = "7998Y"
        part_num = "95073"
        self.print_excel_charts(base_path, bar_num, part_num)
        # todo real call below - check file path will match
        #self.print_excel_charts(self, gb.testInfo.filePath, gb.testInfo.barNum, gb.testInfo.partNum)

        pass


    def process_update(self, update):
        if update['type'] == 'label':
            self.update_label(update['label_name'],update['value'], update['color'])
        elif update['type'] == 'plot':
            self.update_plot_1(update['x_data'], update['y_data'])

    def update_label(self, label, value, color):
        if label == 'voltagein':
            self.voltagein.set(value)
        elif label == 'pulsewidth':
            self.pulsewidth.set(value)
        elif label == "ipk":
            self.peakcurrent.set(value)
        elif label == "vdss":
            self.vdss.set(value)
        elif label == "vout":
            self.voltageout.set(value)
        elif label == "testtime":
            self.testtime.set(value)
        elif label == "finaltemp":
            self.finaltemp.set(value)
        elif label == "lpulsespec":
            self.lpulse.set(value)
        elif label == "voutlp":
            self.voltageoutlp.set(value)
        elif label == 'status':
            #self.teststatus.set(value)
            #gb.testData.status = value
            self.statusLabel.config(text=value, background=color)

    def update_plot_1(self, new_x, new_y):
        self.x_data1.append(new_x)
        self.y_data1.append(new_y)
        #self.ax.plot(self.x_data1, self.y_data1, marker='o')
        self.line1.set_data(self.x_data1, self.y_data1)
        self.canvas.draw()

    def clear_plot_1(self):
        self.line1.remove()
        # recreate line 1
        self.x_data1 = []
        self.y_data1 = []
        self.line1, = self.ax.plot(self.x_data1, self.y_data1, marker='o', label="Actual",
                                   color="blue")  # First plot line
        self.update_plot_1(0, 0)
        self.canvas.draw()

    def plot_reference_line(self):
        self.line2.remove()
        # get data and split
        point_set = [num for num in gb.testLimits['outputGraphline'].split(',') if num]
        points = [float(num) for num in point_set]
        print(points)
        self.x_data2 = [points[0], points[2]]
        self.y_data2 = [points[1], points[3]]
        self.line2, = self.ax.plot(self.x_data2, self.y_data2, label="Min Line", color="green")
        self.canvas.draw()

    def update_dynamic_line(self, x, y):
        self.line1.set_data(x,y)
        self.canvas.draw()

    def on_mintemp_change(self, *args):
        gb.testInfo.minTemp = float(self.mintemp.get())

    def on_maxtemp_change(self, *args):
        gb.testInfo.maxTemp = float(self.maxtemp.get())

    def on_currentlimit_change(self, *args):
        gb.testInfo.thresholdCurrent = float(self.currentlimit.get())

    def on_voltagelimit_change(self, *args):
        gb.testInfo.thresholdVoltage = float(self.voltagelimit.get())

    def on_testinterval_change(self, *args):
        text = self.testinterval.get()
        # Strip whitespace and check if empty
        gb.testInfo.testInterval = float(text.strip()) if text.strip() else 0.0

    def on_setcurrent_change(self, *args):
        gb.testInfo.testCurrent = float(self.setcurrent.get())

    def on_lpulsecurrent_change(self, *args):
        gb.testInfo.lpulseCurrent = float(self.lpulsecurrent.get())

        # subroutines here first
    def do_something(self):
        print("Menu item clicked!")

    def settings_window(self):
        newView = SetupView(self)

    def gpib_addressing(self):
        gpib_view = GpibView(self)

    def debug_mode(self):
        if gb.system.debugMode:
            gb.system.debugMode = False
            self.master.title("AutoParameters")
            print("debugMode OFF")
        else:
            gb.system.debugMode = True
            self.master.title("AutoParameters - Debug Mode")
            print("debugMode ON")

    def show_about(self):
        print("showAbout")
        # open window
        window = aboutView(self)
        # want to grab so mainview is not changed during testing
        window.grab_set()


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
        # call init_test
        TestRoutines.init_test()
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
        # clears screen
        self.clear_display()
        # gets test limits/parameters
        gb.testLimits = dbase.load_test_limits(self.partno.get())
        # print(gb.testLimits)
        # plot reference line
        self.plot_reference_line()
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
            messagebox.showwarning(title='Output Testing', message='All the parts in the bar have been tested. Start a new bar.')
            return

        # check if part number entered is different from indexed
        #print(f"serialNum: {self.serialNum.get()}, partlist s/n: {self.partList[self.next_part_idx]}, testInfoPos: { gb.testInfo.position}")
        if  self.serialNum.get() != self.partList[self.next_part_idx]:
            gb.testInfo.position = self.serialNum.get()
            # find index of next testable part in partlist after serial number given
            # minus 1 because it will be incremented later
            self.next_part_idx = bisect.bisect_right(self.partList, self.serialNum.get()) - 1

        # create new csv file
        gb.testInfo.serialNumber = self.make_serial_number()
        gb.testInfo.fileName = f"{gb.testInfo.barNum}{gb.testInfo.designNum}x{gb.testInfo.position}.csv"

        self.testButton.config(state='disabled')
        self.serialLabel.config(text="Testing Serial No.")

        # clear test result fields
        self.clear_display()
        self.clear_plot_1()

        # status
        self.statusLabel.config(text="Testing", background="yellow")
        self.statusLabel.update_idletasks()

        # run test with reference to this instance
        self.done_event.clear()
        self.test_thread = threading.Thread(target=test_output, args=(self.queue, self.done_event, self.check_stop_flag), daemon=True)
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

        print("after_test")

        # todo this is ready to use - not sure  - copied from hipot
        # before saving check test history
        """
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
        dbase.record_output_data()
        # dbase.recordStatus(dbase, self.statusFlag, self.makeSerialNumber())

        #5 issue pass/fail signal
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
        #    self.statusLabel.config(text="Ready", background="gray85")



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
        if not dbase.get_part_number(self.bar):
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
        self.voltageoutlp.set('')
        self.testtime.set('')
        self.finaltemp.set('')
        self.lpulse.set('')
        self.voltageout.set('')
        self.vdss.set('')

    def print_test_info(self):
        # dumps testinfo for checking
        print("Instance Attributes and Their Values:")
        for attr in dir(gb.testInfo):
            if not attr.startswith("__"):  # Filter out special methods
                value = getattr(gb.testInfo, attr)
                print(f"{attr}: {value}")

    def print_excel_charts(self, base_path, bar_num, part_num):
        try:
            # Define file paths
            # todo excel file should be a global init value
            # base_path = gb.initValues.
            # test_data_folder = gb.initValues.
            # chart_folder = gb.initValues.
            # excel_chart_filename = gb.initValues.
            template_file = os.path.join(base_path, "Test Data", "Auto Output Chart r3.xlsm")
            data_dir = os.path.join(base_path, "Test Data", "Output_Test", bar_num, "*.csv")
            data_path = os.path.join(base_path, "Test Data", "Output_Test", bar_num)
            chart_file = os.path.join(base_path, "95_series", part_num, "Test Data", f"{bar_num} Output Chart.xlsm")
            #"C:\Users\gslam\Dropbox\SlamaTech\Consulting\AUTO Programs Python\AutoOutput\95_series\95073\Test Data\7998Y Output Chart.xls"

            # Get the list of CSV files
            data_files = []
            for file in os.listdir(data_path):
                if file.endswith(".csv"):
                    data_files.append(os.path.join(data_path, file))

            # Ensure we have data files to process
            if not data_files:
                print("No data files found.")
                return

            # Start Excel
            xlapp = win32.Dispatch("Excel.Application")
            xlapp.Visible = True  # Make Excel visible for debugging

            # Open the template file
            xlbook = xlapp.Workbooks.Open(template_file)

            # Call the macro to load data
            #data_files = [r'C:\Users\gslam\Dropbox\SlamaTech\Consulting\AUTO Programs Python\AutoOutput\Test Data\Output_Test\3509Y\20100518_102633_3509YD50x01.csv', 'C:\\Users\\gslam\\Dropbox\\SlamaTech\\Consulting\\AUTO Programs Python\\AutoOutput\\Test Data\\Output_Test\\3509Y\\20100518_102821_3509YD50x02.csv']
            #print (part_num)
            #print (data_files)
            xlapp.Run("Module2.LoadFiles", data_files, part_num)

            # Call the macro to save the chart file
            xlapp.Run("Module2.SaveChartFile", chart_file)

            # Call the macro to print charts
            xlapp.Run("Module2.PrintCharts")

            # Close Excel
            xlapp.Quit()
            print("Process completed successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")


def run_excel_macro():
        try:
            # todo Path to Excel file
            excel_file = r"C:\Users\gslam\Dropbox\SlamaTech\Consulting\AUTO Programs Python\Test Data\Output_Test\Auto Output Chart r3.xlsm"

            # Macro name (include the module name if needed, e.g., 'Module1.MyMacro')
            macro_name = "CommandButton1_Click1"

            # Open Excel
            excel = win32.Dispatch("Excel.Application")
            excel.Visible = True  # Set to True to see Excel open

            # Open the workbook
            workbook = excel.Workbooks.Open(excel_file)

            # Run the macro
            excel.Application.Run(macro_name)

            # Save and close the workbook
            workbook.Save()
            workbook.Close()

            # Quit Excel
            excel.Quit()

            messagebox.showinfo("Success", "Macro ran successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to run macro: {e}")

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


        self.pulse_gen_start_width = tk.StringVar()
        self.pulse_gen_start_width.set(gb.testInfo.pulseStart)
        self.pulse_gen_start_width.trace_add("write", self.on_pulse_gen_start_width_change)
        pulse_gen_start_width_entry = ttk.Entry(pulsefrm, width=7, textvariable=self.pulse_gen_start_width)
        pulse_gen_start_width_entry.grid(column=0, row=1, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(pulsefrm, text="Start Width").grid(column=1, row=1, sticky="w")


        self.pulse_gen_stop_width = tk.StringVar()
        self.pulse_gen_stop_width.set(gb.testInfo.pulseStop)
        self.pulse_gen_stop_width.trace_add("write", self.on_pulse_gen_stop_width_change)
        pulse_gen_stop_width_entry = ttk.Entry(pulsefrm, width=7, textvariable=self.pulse_gen_stop_width)
        pulse_gen_stop_width_entry.grid(column=0, row=2, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(pulsefrm, text="Stop Width").grid(column=1, row=2, sticky="w")


        self.pulse_gen_step = tk.StringVar()
        self.pulse_gen_step.set(gb.testInfo.pulseStep)
        self.pulse_gen_step.trace_add("write", self.on_pulse_gen_step_change)
        pulse_gen_step_entry = ttk.Entry(pulsefrm, width=7, textvariable=self.pulse_gen_step)
        pulse_gen_step_entry.grid(column=0, row=3, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(pulsefrm, text="Step").grid(column=1, row=3, sticky="w")


        self.pulse_gen_units = tk.StringVar()
        self.pulse_gen_units.set(gb.testInfo.pulseUnits)
        self.pulse_gen_units.trace_add("write", self.on_pulse_gen_units_change)
        pulse_gen_units_entry = ttk.Entry(pulsefrm, width=7, textvariable=self.pulse_gen_units)
        pulse_gen_units_entry.grid(column=0, row=4, padx=(0, 5), pady=5, sticky="we")
        ttk.Label(pulsefrm, text="Units").grid(column=1, row=4, sticky="w")



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

        self.scope_vdss_chan = tk.StringVar()
        self.scope_vdss_chan.set(gb.testInfo.vdssChan)
        self.scope_vdss_chan.trace_add("write", self.on_scope_vdss_chan_change)
        scope_vdss_chan_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_vdss_chan)
        scope_vdss_chan_entry.grid(column=0, row=0, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Vdss Chan").grid(column=1, row=0, sticky="w")

        self.scope_vdss_scale = tk.StringVar()
        self.scope_vdss_scale.set(gb.testInfo.vdssScale)
        self.scope_vdss_scale.trace_add("write", self.on_scope_vdss_scale_change)
        scope_vdss_scale_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_vdss_scale)
        scope_vdss_scale_entry.grid(column=0, row=1, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Vdss V/div").grid(column=1, row=1, sticky="w")


        self.scope_current_chan = tk.StringVar()
        self.scope_current_chan.set(gb.testInfo.currentChan)
        self.scope_current_chan.trace_add("write", self.on_scope_current_chan_change)
        scope_current_chan_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_current_chan)
        scope_current_chan_entry.grid(column=0, row=2, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Current Chan").grid(column=1, row=2, sticky="w")

        self.scope_current_scale = tk.StringVar()
        self.scope_current_scale.set(gb.testInfo.currentScale)
        self.scope_current_scale.trace_add("write", self.on_scope_current_scale_change)
        scope_current_scale_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_current_scale)
        scope_current_scale_entry.grid(column=0, row=3, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Current V/div").grid(column=1, row=3, sticky="w")


        self.scope_vout_chan = tk.StringVar()
        self.scope_vout_chan.set(gb.testInfo.voutChan)
        self.scope_vout_chan.trace_add("write", self.on_scope_vout_chan_change)
        scope_vout_chan_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_vout_chan)
        scope_vout_chan_entry.grid(column=0, row=4, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Vout Chan").grid(column=1, row=4, sticky="w")

        self.scope_vout_scale = tk.StringVar()
        self.scope_vout_scale.set(gb.testInfo.voutScale)
        self.scope_vout_scale.trace_add("write", self.on_scope_vout_scale_change)
        scope_vout_scale_entry = ttk.Entry(scopefrm, width=7, textvariable=self.scope_vout_scale)
        scope_vout_scale_entry.grid(column=0, row=5, padx=(0, 10), pady=5, sticky="we")
        ttk.Label(scopefrm, text="Vout V/div").grid(column=1, row=5, sticky="w")


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
        self.voltage_option.set('2000V')
        self.voltage_ratio = tk.StringVar()
        self.voltage_ratio.set(gb.testInfo.voltageRatio)

        voltagefrm = ttk.LabelFrame(self, text=" Voltage Divider Ratio ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        voltagefrm.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky="nwe")
        #voltagefrm.columnconfigure(0, weight=1)

        ttk.Radiobutton(voltagefrm, text='2000 V (249 k)', variable=self.voltage_option, value='2000V',
                        command=self.voltage_ratio).grid(column=0, row=0, padx=20, sticky=tk.W)

        ttk.Radiobutton(voltagefrm, text='Other', variable=self.voltage_option, value='Other',
                        command=self.voltage_other).grid(column=0, row=1, padx=20, sticky=tk.W)

        self.voltage_ratio = tk.StringVar()
        self.voltage_ratio.set(gb.testInfo.voltageRatio)
        self.voltage_ratio_entry = ttk.Entry(voltagefrm, width=7, textvariable=self.voltage_ratio)
        self.voltage_ratio_entry.grid(column=0, row=2, padx=(0, 10), pady=5, sticky="we")
        self.voltage_ratio_entry.config(state="disabled")
        ttk.Label(voltagefrm, text="V/1V").grid(column=1, row=2, sticky="w")


        # current probe frame
        self.current_option = tk.StringVar(value='P6021')
        self.current_scale = tk.StringVar()
        self.current_scale.set(gb.testInfo.currentRatio)
        self.option_map = {
            '2.7 A (0.332R)': 328,
            '1.5 A (0.604R)': 597,
            'TCP202': 1000,
            'P6021': 100,
            'Other': None
        }
        currentfrm = ttk.LabelFrame(self, text=" Current Measurement ", width=200, height=200, relief='raised', borderwidth=20, padding="10 10 10 10")
        currentfrm.grid(column=3, row=2, columnspan=2, padx=10, pady=10, sticky="nwe")
        #currentfrm.columnconfigure(0, weight=1)

        for i, label in enumerate(self.option_map.keys()):
            ttk.Radiobutton(currentfrm, text=label, value=label, variable=self.current_option, command=self.on_current_selection
            ).grid(row=i, column=0, sticky="w", padx=10, pady=2)

        #ttk.Radiobutton(currentfrm, text='2.7 A (0.33 R)', variable=self.currentOption, value='27A',command=self.current_option).grid(column=0, row=0, padx=20, sticky=tk.W)

        #ttk.Radiobutton(currentfrm, text='TCP202', variable=self.currentOption, value='TCP202',command=self.current_option).grid(column=0, row=1, padx=20, sticky=tk.W)

        #ttk.Radiobutton(currentfrm, text='P6021', variable=self.currentOption, value='P6021',command=self.current_option).grid(column=0, row=3, padx=20, sticky=tk.W)

        #ttk.Radiobutton(currentfrm, text='Other', variable=self.currentOption, value='Other',command=self.current_other).grid(column=0, row=4, padx=20, sticky=tk.W)

        self.current_scale_entry = ttk.Entry(currentfrm, width=7)
        self.current_scale_entry.grid(column=0, row=5, padx=(0, 10), pady=5, sticky="we")
        self.current_scale_entry.insert(0, str(self.option_map['P6021']))
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


        self.pulse_gen_ieee_adr = tk.StringVar()
        self.pulse_gen_ieee_adr.set(gb.initValues.sigGenAdr)
        self.pulse_gen_ieee_adr.trace_add("write", self.pulse_gen_ieee_adr_change)
        pulse_gen_ieee_adr_entry = ttk.Entry(self, width=35, textvariable=self.pulse_gen_ieee_adr)
        pulse_gen_ieee_adr_entry.grid(column=1, row=1, padx=(10, 10), pady=5, sticky="we")
        ttk.Label(self, text="Pulse Generator").grid(column=0, row=1, padx=(10,0), sticky="e")

        self.power_ieee_adr = tk.StringVar()
        self.power_ieee_adr.set(gb.initValues.powerAdr)
        self.power_ieee_adr.trace_add("write", self.power_ieee_adr_change)
        power_ieee_adr_entry = ttk.Entry(self, width=35, textvariable=self.power_ieee_adr)
        power_ieee_adr_entry.grid(column=1, row=2, padx=(10, 10), pady=5, sticky="we")
        ttk.Label(self, text="Power Supply").grid(column=0, row=2, padx=(10,0), sticky="e")

        self.scanner_ieee_adr = tk.StringVar()
        self.scanner_ieee_adr.set(gb.initValues.scannerAdr)
        self.scanner_ieee_adr.trace_add("write", self.scanner_ieee_adr_change)
        scanner_ieee_adr_entry = ttk.Entry(self, width=35, textvariable=self.scanner_ieee_adr)
        scanner_ieee_adr_entry.grid(column=1, row=3, padx=(10, 10), pady=5, sticky="we")
        ttk.Label(self, text="Data Scanner").grid(column=0, row=3, padx=(10,0), sticky="e")

        self.scope_ieee_adr = tk.StringVar()
        self.scope_ieee_adr.set(gb.initValues.scopeAdr)
        self.scope_ieee_adr.trace_add("write", self.scope_ieee_adr_change)
        scope_ieee_adr_entry = ttk.Entry(self, width=35, textvariable=self.scope_ieee_adr)
        scope_ieee_adr_entry.grid(column=1, row=4, padx=(10, 10), pady=5, sticky="we")
        ttk.Label(self, text="Oscilloscope").grid(column=0, row=4, padx=(10,0), sticky="e")

        # Add a button to save settings and close the window
        ttk.Button(self, text="Close", command=self.destroy).grid(column=1, row=5, padx=10, pady=10, sticky="we")

    def pulse_gen_ieee_adr_change(self, *args):
        gb.initValues.sigGenAdr = self.power_ieee_adr.get()

    def power_ieee_adr_change(self, *args):
        gb.initValues.powerAdr = self.power_ieee_adr.get()

    def scanner_ieee_adr_change(self, *args):
        gb.initValues.scannerAdr = self.scanner_ieee_adr.get()

    def scope_ieee_adr_change(self, *args):
        gb.initValues.scopeAdr = self.scope_ieee_adr.get()