"""
Home for global variables
"""


import array as arr
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from tkinter import messagebox
import os

# declare variables for instruments
lcr = None
hipot = None
scope = None
sig_gen = None
power = None
meter = None
thermo = None

@dataclass
class CLsystem(object):
    '''
    system information
    '''
    # internal system variables, mostly status
    version: str = "1.1.0"
    debug_mode: bool = Flase
    calibrated: bool = False
    fixture: str = ""

# declare instance
system = CLsystem()

@dataclass
class CLinitValues(object):
    '''
    These come from a file loaded at the start of the program
    "testerInit.txt" expected in the local folder
    However 'commonInitFile' points to another location where
    additional common values can be stored for all programs
    '''

    commonInitFile: str = ""
    sqlServer: str = ""
    serverUserName: str = ""
    serverPassword: str = ""
    partLimitsDataBase: str = ""
    barDataBase: str = ""
    barDataTable: str = ""
    barHistoryTable: str = ""
    barLimitTable: str = ""
    basePath: str = ""
    testDataPath: str = ""
    inductorDataPath: str = ""
    chartDataPath: str = ""
    excelChartFileName: str = ""
    lcrMeter: str = ""
    lcrAdr: str = ""
    hipotMeter: str = ""
    hipotAdr: str = ""
    scopeMeter: str = "SDS824X"
    scopeAdr: str = ""
    sigGen: str = "SDG2042X"
    sigGenAdr: str = ""
    powerUnit: str = "GPP4323"
    powerAdr: str = ""
    scannerUnit: str = "HP34970A"
    scannerAdr: str = ""
    meterUnit: str = "USB2001TC"
    meterAdr: str = "1"
    dioUnit: str = ""
    dioAdr: str = ""
    commPort: int = 4
    lcrXfmrLevel: float = 0.5
    lcrIndLevel: float = 0.1
    lcrFrequency: int = 100000
    lcrCalLevel: float = 0.5
    lcrBias: float = 0
    ipeakLo: float = 0.95
    ipeakHi: float = 1.1
    debugLcr: int = 1
    test: str = ""

# function to load from files
def load_init_values(filename):
    """Load init values, with optional commonInit.txt defaults."""

    def load_file(path):
        data = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        data[key.strip()] = value.strip().strip('"').strip("'")
        except FileNotFoundError:
            print("File not found.")
            messagebox.showerror(title="File Open", message="The testerInit.txt file was not found")
        except IOError:
            print("Error reading the file.")
            messagebox.showerror(title="File Open", message="testerInit.txt - Error reading file.")
        except Exception as e:
            print("An error occurred:", str(e))
            messagebox.showerror(title="File Open", message="testerInit.txt - File error on open", detail=str(e))
        return data

    # Step 1: load the main/local file
    local_data = load_file(filename)

    # Step 2: if it defines a commonInitFile, load that first
    common_file = local_data.get('commonInitFile', '')
    merged_data = {}

    if common_file:
        # If relative, make it relative to the main file’s directory
        if not os.path.isabs(common_file):
            common_file = os.path.join(os.path.dirname(filename), common_file)
        if os.path.exists(common_file):
            merged_data = load_file(common_file)

    # Step 3: update with local data, overwriting common values
    merged_data.update(local_data)

    return merged_data

# --- auto-load the values when the module is imported ---
init_dict = load_init_values('testerinit.txt')
initValues = CLinitValues(**init_dict)


@dataclass
class CLtestInfo(object):
    '''
    information about test setup and parameters
    default values included
    '''
    partNum: str = None
    barNum: str = None
    designNum: str = None
    buildNum: str = None
    furnaceNum: str = None
    fireDate: str = None
    fileName: str = ""
    filePath: str = ""
    filePathBase: str = ""
    filePathOutput: str = ""
    numPositions = None
    position = None
    serialNumber: str = None
    testType: str = None
    testCheck: str = None
    testOption: str = None
    fixture: str = None
    tempType: str = "T"
    tempChan: str = "105"
    #vinChan: str = "110"
    #voutChan: str = "107"
    vdssChan: str = "2"
    vdssScale: str = "100"
    currentChan: str = "3"
    currentScale: str = "0.50"
    voutChan: str = "4"
    voutScale = "0.5"
    currentRatio = 330
    currentProbe: str = "2.7 A (0.332R)"
    voltageDivider = "1200V (178k)"
    voltageRatio: float = 562.8
    pulsePeriod: float = 20
    pulseWidth: float = 0
    pulseStart:float = 1
    pulseStop: float = 7
    pulseStep: float = 0.5
    pulseUnits: str = "us"
    thresholdCurrent: float = 2.5
    thresholdVoltage: float = 2000
    minTemp: float = 18
    maxTemp: float = 30
    testInterval: float = 3
    testCurrent: float = 1.5
    lpulseCurrent: float = 1.5
    ch1Voltage: float = 15
    ch1CurrentLimit: float = 2
    ch2Voltage: float = 5.3
    ch2CurrentLimit: float = 1
    vin: float = 15
    currentLimit: float = 2
    vaux: float = 5.3
    iaux: float = 1
    setTemp: float = 85
    setTempRange: float = 1
    preheat: bool = False

# declare instance
testInfo = CLtestInfo()


@dataclass
class CLtestData:
    '''
    measured test results
    status codes ennum below
    '''
    status: Optional[int] = 0
    priInd: Optional[float] = None
    secInd: Optional[float] = None
    priLkg: Optional[float] = None
    priQ: Optional[float] = None
    priRes: Optional[float] = None
    secRes: Optional[float] = None
    coupling: Optional[float] = None
    irVoltage: Optional[float] = None
    irResistance: Optional[float] = None
    irTime: Optional[float] = None
    hipotVoltage: Optional[float] = None
    hipotCurrent: Optional[float] = None
    hipotTime: Optional[float] = None
    indInd: list[float] = field(default_factory=list)
    indQ: list[float] = field(default_factory=list)
    indBias: list[float] = field(default_factory=list)
    indRes: Optional[float] = None
    indSetBias: Optional[float] = None
    vin: Optional[float] = None
    ipk: Optional[float] = None
    vout: Optional[float] = None
    voutlp: Optional[float] = None
    pulseWidth: Optional[float] = None
    lpulse: Optional[float] = None
    lpulseSpecific: Optional[float] = None
    finalTemp: Optional[float] = None
    tempDiff: Optional[float] = None
    vdss: Optional[float] = None
    testTime: Optional[float] = None
    logTime: Optional[str] = None

    def appendInd(self, value):
        self.indInd.append(value)

    def appendQ(self, value):
        self.indQ.append(value)

    def appendBias(self, value):
        self.indBias.append(value)

# declare instance
testData = CLtestData()


@dataclass
class CLtestLimits(object):
    '''
    test limits retrieved from database
    '''
    partNum: Optional[str] = None       # was Part_Num
    designNum: Optional[str] = None     # was Design_Num
    numPositions: Optional[int] = None  # was Num_Positions
    numTerms: Optional[int] = None
    numVariants: Optional[int] = None
    prefireFixture: Optional[str] = None
    fixtureNum: Optional[str] = None    # was Fixture
    testType: Optional[str] = None
    priLmin: Optional[float] = None
    priLmax: Optional[float] = None
    priQmin: Optional[float] = None
    priRmin: Optional[float] = None
    priRmax: Optional[float] = None
    leakageMin: Optional[float] = None
    leakageMax: Optional[float] = None
    coupling: Optional[float] = None
    secLmin: Optional[float] = None
    secLmax: Optional[float] = None
    secRmin: Optional[float] = None
    secRmax: Optional[float] = None
    pulseLmin: Optional[float] = None     # was LPulsemin
    pulseLmax: Optional[float] = None     # was LPulsemax
    outputVoltmin: Optional[float] = None    # was Voutmin
    pulseLcur: Optional[float] = None     # was IPulse
    hipotVoltage: Optional[float] = None  # was VHipot
    hipotRamp: Optional[float] = None
    hipotCur: Optional[float] = None      # was IHipot
    hipotTime: Optional[float] = None     # was THipot
    irVoltage: Optional[float] = None
    irResistance: Optional[float] = None
    irTime: Optional[float] = None
    stxPercentChange: Optional[float] = None  # was STX%change
    outputVoltmin85: Optional[float] = None   # was Voutmin85
    pulseLmin85: Optional[float] = None       # was LPulsemin85
    outputGraphline: Optional[str] = None
    startPulseWidth: Optional[float] = None   # was StartingPulseWidth
    turnsRatio: Optional[float] = None
    lcrlevel: Optional[float] = None
    indL100min: Optional[float] = None
    indL100max: Optional[float] = None
    satCur: Optional[float] = None
    satLminPercent: Optional[float] = None    # Lsatmin%
    hipotType: Optional[str] = None

    def __getitem__(self, key):
        raise TypeError(f"{self.__class__.__name__} object is not subscriptable")

    def __setitem__(self, key, value):
        raise TypeError(f"{self.__class__.__name__} object is not subscriptable")

    def update_from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

# declare instance
testLimits = CLtestLimits()


class StatusCodeText():
    def __init__(self):
        self.codes('Undetermined', 'Good part', 'Parameter test failure', 'IR failure',
                   'Hipot failure', 'Output failure', 'Physical defect', 'Other',
                   'Primary Inductance', 'Primary resistance', 'Green open',
                   'Green split', 'Fired open', 'Fired crack', 'Fired split',
                   'Primary Q', 'Leakage inductance', 'Secondary inductance',
                   'Secondary resistance', 'Failed preLAT', 'Rework')

@dataclass
class TestBoardBits(Enum):
    ledGrn = 0  # pass
    ledRed = 1  # fail
    ledYel = 2  # test
    priShort = 3  # k3, short pri
    instr = 4  # k1,k8 inductance/resistance
    secSide = 5  # k5,k7 sec
    secShort = 6  # k6, short sec
    priSide = 7  # k2, k4 pri


@dataclass
class StatusCode(Enum):
    '''
    a part is undetermined '0' until it has passed all tests when it becomes '1'
    tests are parameters, hipot/ir, output test
    '''
    Undetermined = 0
    GoodPart = 1
    ParameterFail = 2
    IRFail = 3
    HipotFail = 4
    OutputFail = 5
    PhysicalDefect = 6
    Other = 7
    PriInductFail = 8
    PriResFail = 9
    GreenOpen = 10
    GreenSplit = 11
    FiredOpen = 12
    FiredCrack = 13
    FiredSplit = 14
    PriQFail = 15
    LeakageIndFail = 16
    SecInductFail =17
    SecResFail = 18
    PreLATFail = 19
    Rework = 20
    HiLimit = 30
    LoLimit = 31
    Breakdown = 32
    ArcDetect = 33
    Abort = 34
    Short = 35

class testType:
    # this is here as a definition
    test_dict = {
        'P_I': 'Production - Inductor',
        'P_T': 'Production - Transformer',
        'D_I': 'Design - Inductor',
        'D_T': 'Design - Transformer',
        'D_C': 'Design - Common Mode Inductor'
    }

class testLimitsDict(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)





