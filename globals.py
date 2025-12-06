"""
Home for global variables
"""


import array as arr
from enum import Enum
from dataclasses import dataclass, fields
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
    version: str = "1.0.0"
    debug_mode = True
    calibrated = False
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
    dioAdr: int = 0
    commPort: int = 4
    lcrXfmrLevel: float = 0.5
    lcrIndLevel: float = 0.1
    lcrFrequency: int = 100000
    lcrCalLevel: float = 0.5
    lcrBias: float = 0
    ipeakLo: float = 0.95
    ipeakHi: float = 1.1
    debugLcr: int = 1
    debugMode: int = 0
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
    vinChan: str = "110"
    voutChan: str = "107"
    vdssChan: str = "2"
    vdssScale: str = "100"
    currentChan: str = "3"
    currentScale: str = "0.50"
    voutChan: str = "4"
    voutScale = "0.5"
    currentRatio = 330
    currentProbe: str = "2.7 A (0.332R)"
    voltageRatio = 562.8
    pulsePeriod = 20
    pulseWidth = None
    pulseStart = 1
    pulseStop = 7
    pulseStep = 0.5
    pulseUnits: str = "us"
    thresholdCurrent = 2.5
    thresholdVoltage = 2000
    minTemp = 18
    maxTemp = 30
    testInterval = 3
    testCurrent = 1.5
    lpulseCurrent = 1.5
    vin = 15
    currentLimit = 2
    vaux = 5.3
    iaux = 1
    setTemp = 85
    setTempRange = 1
    preheat = False

# declare instance
testInfo = CLtestInfo()


@dataclass
class CLtestData:
    '''
    measured test results
    status codes ennum below
    '''
    status = 0
    priInd = None
    secInd = None
    priLkg = None
    priQ = None
    priRes = None
    secRes = None
    coupling = None
    irVoltage = None
    irResistance = None
    irTime = None
    hipotVoltage = None
    hipotCurrent = None
    hipotTime = None
    indInd = []
    indQ = []
    indBias = []
    indRes = None
    indSetBias = None
    vin = None
    ipk = None
    vout = None
    voutlp = None
    pulseWidth = None
    lpulse = None
    lpulseSpecific = None
    finalTemp = None
    tempDiff = None
    vdss = None
    testTime = None
    logTime = None

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
    partNum = None       # was Part_Num
    designNum = None     # was Design_Num
    numPositions = None  # was Num_Positions
    numTerms = None
    numVariants = None
    prefireFixture = None
    fixtureNum = None    # was Fixture
    testType = None
    priLmin = None
    priLmax = None
    priQmin = None
    priRmin = None
    priRmax = None
    leakageMin = None
    leakageMax = None
    coupling = None
    secLmin = None
    secLmax = None
    secRmin = None
    secRmax = None
    pulseLmin = None     # was LPulsemin
    pulseLmax = None     # was LPulsemax
    outputVoltmin = None    # was Voutmin
    pulseLcur = None     # was IPulse
    hipotVoltage = None  # was VHipot
    hipotRamp = None
    hipotCur = None      # was IHipot
    hipotTime = None     # was THipot
    irVoltage = None
    irResistance = None
    irTime = None
    stxPercentChange = None  # was STX%change
    outputVoltmin85 = None   # was Voutmin85
    pulseLmin85 = None       # was LPulsemin85
    outputGraphline = None
    startPulseWidth = None   # was StartingPulseWidth
    turnsRatio = None
    lcrlevel = None
    indL100min = None
    indL100max = None
    satCur = None
    satLminPercent = None    # Lsatmin%
    hipotType = None

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





