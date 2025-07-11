"""
Home for global variables

"powerUnit": "GPP4323",
"powerAdr": "TCPIP0::192.168.88.48::1026::SOCKET",
"""
import array as arr
from enum import Enum
from dataclasses import dataclass

# declare variables for instrumemts
lcr = None
hipot = None
scope = None
sig_gen = None
power = None
meter = None
thermo = None


class CLsystem(object):
    '''
    system information
    '''
    # internal system variables, mostly status
    def __init__(self):
        self.version = "1.0.0"
        self.debugMode = True
        self.calibrated = False
        self.fixture = ""

@dataclass
class CLinitValues(object):
    '''
    These come from a file loaded at the start of the program
    "testerInit.txt"
    '''

    def __init__(self):
        self.sqlServer = ""
        self.serverUserName = ""
        self.serverPassword = ""
        self.partLimitsDataBase = ""
        self.barDatabase = ""
        self.barDataTable = ""
        self.barLimitTable = ""
        self.basePath = ""
        self.testDataPath = ""
        self.inductorDataPath = ""
        self.chartDataPath = ""
        self.excelChartFileName = ""
        self.lcrMeter = ""
        self.lcrAdr = ""
        self.hipotMeter = ""
        self.hipotAdr = ""
        self.scopeMeter = "SDS824X"
        self.scopeAdr = ""
        self.meterUnit = "SDM3055SC"
        self.meterAdr = ""
        self.sigGen = "SDG2042X"
        self.sigGenAdr = ""
        self.powerUnit = "GPP4323"
        self.powerAdr = ""
        self.scannerUnit = "HP34970A"
        self.scannerAdr = ""
        self.thermoUnit = "USB2001TC"
        self.thermoAdr = "1"
        self.boardNum = "0"
        self.commPort = "4"
        self.lcrXfmrLevel = "0.5"
        self.lcrIndLevel = "0.1"
        self.lcrFrequency = "100000"
        self.lcrCalLevel = "0.5"
        self.lcrBias = "0"
        self.debugLcr = 1
        self.ipeakLo = 0.9
        self.ipeakHi = 1.1

@dataclass
class CLtestInfo(object):
    '''
    information about test setup and parameters
    default values included
    '''
    def __init__(self):
        self.partNum = None
        self.barNum = None
        self.designNum = None
        self.buildNum = None
        self.furnaceNum = None
        self.fireDate = None
        self.fileName = ""
        self.filePath = ""
        self.filePathBase = ""
        self.filePathOutput = ""
        self.numPositions = None
        self.position = None
        self.serialNumber = None
        self.testType = None
        self.testCheck = None
        self.testOption = None
        self.fixture = None
        self.tempType = "T"
        self.tempChan = "105"
        self.vinChan = "110"
        self.voutChan = "107"
        self.vdssChan = "2"
        self.vdssScale = "100"
        self.currentChan = "3"
        self.currentScale = "0.50"
        self.voutChan = "4"
        self.voutScale = "0.5"
        self.currentRatio = 597
        self.currentProbe = "1.5 A (0.604R)"
        self.voltageRatio = 562.8
        self.pulsePeriod = 20
        self.pulseWidth = None
        self.pulseStart = 1
        self.pulseStop = 7
        self.pulseStep = 0.5
        self.pulseUnits = "us"
        self.thresholdCurrent = 2.5
        self.thresholdVoltage = 2000
        self.minTemp = 18
        self.maxTemp = 30
        self.testInterval = 3
        self.testCurrent = 1.5
        self.lpulseCurrent = 1.5
        self.vin = 15
        self.currentLimit = 2
        self.vaux = 5.3
        self.iaux = 1
        self.setTemp = 85
        self.setTempRange = 1
        self.preheat = False


def update_from_dict(self, data):
    for key, value in data.items():
        if hasattr(self, key):
            setattr(self, key, value)

@dataclass
class CLtestData:
    '''
    measured test results
    status codes ennum below
    '''
    def __init__(self):
        self.status = 0
        self.priInd = None
        self.secInd = None
        self.priLkg = None
        self.priQ = None
        self.priRes = None
        self.secRes = None
        self.coupling = None
        self.irVoltage = None
        self.irResistance = None
        self.irTime = None
        self.hipotVoltage = None
        self.hipotCurrent = None
        self.hipotTime = None
        self.indInd = []
        self.indQ = []
        self.indBias = []
        self.indRes = None
        self.indSetBias = None
        self.vin = None
        self.ipk = None
        self.vout = None
        self.voutlp = None
        self.pulseWidth = None
        self.lpulse = None
        self.lpulseSpecific = None
        self.finalTemp = None
        self.tempDiff = None
        self.vdss = None
        self.testTime = None
        self.logTime = None

    def appendInd(self, value):
        self.indInd.append(value)

    def appendQ(self, value):
        self.indQ.append(value)

    def appendBias(self, value):
        self.indBias.append(value)

@dataclass
class CLtestLimits(object):
    '''
    test limits retrieved from database
    '''
    def __init__(self):
            self.partNum = None       # was Part_Num
            self.designNum = None     # was Design_Num
            self.numPositions = None  # was Num_Positions
            self.numTerms = None
            self.numVariants = None
            self.prefireFixture = None
            self.fixtureNum = None    # was Fixture
            self.testType = None
            self.priLmin = None
            self.priLmax = None
            self.priQmin = None
            self.priRmin = None
            self.priRmax = None
            self.leakageMin = None
            self.leakageMax = None
            self.coupling = None
            self.secLmin = None
            self.secLmax = None
            self.secRmin = None
            self.secRmax = None
            self.pulseLmin = None     # was LPulsemin
            self.pulseLmax = None     # was LPulsemax
            self.outputVoltmin = None    # was Voutmin
            self.pulseLcur = None     # was IPulse
            self.hipotVoltage = None  # was VHipot
            self.hipotRamp = None
            self.hipotCur = None      # was IHipot
            self.hipotTime = None     # was THipot
            self.irVoltage = None
            self.irResistance = None
            self.irTime = None
            self.stxPercentChange = None  # was STX%change
            self.outputVoltmin85 = None   # was Voutmin85
            self.pulseLmin85 = None       # was LPulsemin85
            self.outputGraphline = None
            self.startPulseWidth = None   # was StartingPulseWidth
            self.turnsRatio = None
            self.lcrlevel = None
            self.indL100min = None
            self.indL100max = None
            self.satCur = None
            self.satLminPercent = None    # Lsatmin%
            self.hipotType = None

    def __getitem__(self, key):
        raise TypeError(f"{self.__class__.__name__} object is not subscriptable")

    def __setitem__(self, key, value):
        raise TypeError(f"{self.__class__.__name__} object is not subscriptable")

    def update_from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class StatusCodeText():
    def __init__(self):
        self.codes('Undetermined', 'Good part', 'Parameter test failure', 'IR failure',
                   'Hipot failure', 'Output failure', 'Physical defect', 'Other',
                   'Primary Inductance', 'Primary resistance', 'Green open',
                   'Green split', 'Fired open', 'Fired crack', 'Fired split',
                   'Primary Q', 'Leakage inductance', 'Secondary inductance',
                   'Secondary resistance', 'Failed preLAT', 'Rework')

class TestBoardBits(Enum):
    ledGrn = 0  # pass
    ledRed = 1  # fail
    ledYel = 2  # test
    priShort = 3  # k3, short pri
    instr = 4  # k1,k8 inductance/resistance
    secSide = 5  # k5,k7 sec
    secShort = 6  # k6, short sec
    priSide = 7  # k2, k4 pri

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


# declare variables
system = CLsystem()
initValues = CLinitValues()
testInfo = CLtestInfo()
testData = CLtestData()
testLimits = CLtestLimits()

#boardNum = 0

