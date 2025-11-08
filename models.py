"""
models.py
    All the functions dealing with data

"""

from tkinter import messagebox
import pyodbc
print(f'pydoc: " {pyodbc.__file__}')
import csv
import os
from datetime import datetime

import globals as gb


class DataBase:

    #def __init__(self, *args, **kwargs):
        # setup

    # testData = testData()
    #testInfo = testInfo()

    def check_design_num(self, partNum):
        """
        checks part number is database and retrieves design number
        :param partNum:
        :return:
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()

        # find partno in database
        cursor.execute(f"SELECT Design_Num FROM {gb.initValues.barLimitTable} WHERE Part_Num = ?",
                       (partNum,))
        row = cursor.fetchone()

        # if empty
        if row is None:
            messageText = str(partNum) + ' not found'
            messagebox.showerror(title="info box", message=messageText,
                                 detail="Double check part number and try again.\nOtherwise add a new part to the Limits database.")
            designNum = ""
        else:
            designNum = row[0]

        conn.close()
        return designNum


    def check_record_exists(self, barNum):
        """
        check if record exists
        :return: true if exists
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()

        # find partno in database
        cursor.execute(f"SELECT * FROM {gb.initValues.barDataTable} WHERE Bar_Num = ?",
                       (barNum,))
        row = cursor.fetchone()

        # if empty
        if row is None:
            print("barNum not found")
            status: bool = False
        else:
            print("barnum found")
            status: bool = True

        conn.close()
        return status


    def get_part_number(self, barNum):
        """
        check if record exists and gets catalog_num
        :return: true if exists
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()

        # find partno in database
        cursor.execute(f"SELECT * FROM {gb.initValues.barDataTable} WHERE Bar_Num = ?;",
                       (barNum,))
        row = cursor.fetchone()

        # if empty
        if row is None:
            print("barNum not found")
            status: bool = False
        else:
            print("part no: " + row[2])
            gb.testInfo.partNum = row[2]
            gb.testInfo.designNum = row[3]
            status: bool = True

        conn.close()
        return status


    def record_defect(self, defectCode, serialNum):
        """
        record defects and advance serial
        :param defectCode:
        :param serialNum:
        :return:
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # update database
        cursor.execute(f"UPDATE {gb.initValues.barDataTable} SET Defect = ? WHERE PrimeKey = ?",
                       (defectCode, serialNum))
        conn.close()
        return


    def record_status(self, statusCode, serialNum):
        """
        record status code
        :param statusCode:
        :param serialNum:
        :return:
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # update database
        cursor.execute(f"UPDATE {gb.initValues.barDataTable} SET Status = ? WHERE PrimeKey = ?",
                       (statusCode, serialNum))
        conn.close()
        return


    def get_record_stats(self, serialNum):
        '''
        retirns part status
        :param serialNum:
        :return:
        '''

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()

        # update database
        cursor.execute(f"SELECT Status FROM {gb.initValues.barDataTable} WHERE PrimeKey = ?",
                       (serialNum,))
        row = cursor.fetchone()

        conn.close()
        return row[0]


    def record_test_data_25(self, serialNum):
        """
        record measured test data
        :param data:
        :param parameters:
        :return:
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # update database
        cursor.execute(
            f"UPDATE {gb.initValues.barDataTable} SET Vout25 = ?, LPulse25 = ? WHERE PrimeKey = ?",
            (gb.testData.vout, gb.testData.lpulse, serialNum))

        conn.close()
        return


    def record_test_data_85(self, serialNum):
        """
        record measured test data
        :param data:
        :param parameters:
        :return:
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # update database
        cursor.execute(
            f"UPDATE {gb.initValues.barDataTable} SET Vout85 = ?, LPulse85 = ? WHERE PrimeKey = ?",
            (gb.testData.vout, gb.testData.lpulse, serialNum))

        conn.close()
        return


    def get_good_part_list(self, barNum):
        """
        used for ir/hipot testing to only show parts that pass the parameter tests
        part status = 0 (undefined) or 1 (good)
        :param barNum:
        :return: partNum list
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()

        # find partnums in database with good status and return in order
        cursor.execute(f"SELECT convert(varchar,Part_Num) FROM {gb.initValues.barDataTable} WHERE Bar_Num = ? and (Status = 0 or Status = 1) order by Part_Num ASC",
                       (barNum,))
        rows = cursor.fetchall()

        list = []
        for row in rows:
            value = str(row[0])
            list.append(value)

        conn.close()
        return list


    def record_hipot_data(statusCode,serialNum):
        """
        record IR-Hipot test results
        :return:
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # update database
        cursor.execute(
            f"UPDATE {gb.initValues.barDataTable} SET Status = ?, IRVoltage = ?, IRResistance = ?, IRTime = ?, VHypot = ?, IHypot = ?, THypot = ? WHERE PrimeKey = ?",
            statusCode, gb.testData.irVoltage, gb.testData.irResistance, gb.testData.irTime, gb.testData.hipotVoltage, gb.testData.hipotCurrent,
            gb.testData.hipotTime, serialNum)

        conn.close()
        return


    def load_test_limits(self, query):
        """
        get test limits
        assumes the part number is in the limits database
        :param query: is the part number
        :return:
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()

        # find partno in database
        cursor.execute(f"SELECT * FROM {gb.initValues.barLimitTable} WHERE Part_Num = ?",
                       (query,))
        row = cursor.fetchone()

        #unpacked = [{k: item[k] for k in item.keys()} for item in row]

        #columns = [column[0] for column in cursor.description]
        #print(columns)

        #print('Part: ', row[0], ' Design: ', row[1])
        #print (row)

        # the order of the limitFields is important
        # do not change because it must match the column order in the database
        limitFields = (
            'partNum',
            'designNum',
            'numPositions',
            'numTerms',
            'numVariants',
            'prefireFixture',
            'fixtureNum',
            'testType',
            'priLmin',
            'priLmax',
            'priQmin',
            'priRmin',
            'priRmax',
            'leakageMin',
            'leakageMax',
            'coupling',
            'secLmin',
            'secLmax',
            'secRmin',
            'secRmax',
            'pulseLmin',
            'pulseLmax',
            'outputVoltmin',
            'pulseLcur',
            'hipotVoltage',
            'hipotRamp',
            'hipotCur',
            'hipotTime',
            'irVoltage',
            'irResistance',
            'irTime',
            'stx%Change',
            'outputVoltmin85',
            'pulseLmin85',
            'outputGraphline',
            'startingPulseWidth',
            'turnsRatio',
            'lcrlevel',
            'indL100min',
            'indL100max',
            'satCur',
            'satLmin%',
            'hipotType',
        )

        packed = dict(zip(limitFields, row))
        #print(packed)

        conn.close()

        # Break up testType - assign to testInfo
        # type of part to test - transformer or inductor
        # print(f"Test Type: {packed['testType']}")
        if "T" in packed['testType']:
            gb.testInfo.testType = "T"
        elif "I" in packed['testType']:
            gb.testInfo.testType = "I"
        else:
            gb.testInfo.testType = "X"

        # check results? - production or development
        if "P" in packed['testType']:
            gb.testInfo.testCheck = "P"
        elif "D" in packed['testType']:
            gb.testInfo.testCheck = "D"
        else:
            gb.testInfo.testCheck = "X"
        return packed


    def record_output_data(self):
        '''
        add output test results to database
        values at 25 C are also written
        :return:
        '''

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={gb.initValues.sqlServer};"
            f"DATABASE={gb.initValues.barDataBase};"
            f"UID={gb.initValues.serverUserName};"
            f"PWD={gb.initValues.serverPassword};"
            f"ENCRYPT=no;"
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # update database
        cursor.execute(
            f"UPDATE {gb.initValues.barDataTable} SET Status = ?, LPulse = ?, VOut = ?, IPulse = ?, LPulse25 = ?, Vout25 = ? WHERE PrimeKey = ?",
            gb.testData.status, gb.testData.lpulse, gb.testData.vout, gb.testData.ipk, gb.testData.lpulse, gb.testData.vout, gb.testInfo.serialNumber )

        conn.close()

    ## end of database class ==========================================================


def create_output_file_header():
    '''
    header for ascii files of output steps
    :return:
    '''

    # todo change to include path before releasing
    #file_name = f"{gb.testInfo.filePath}\{gb.testInfo.fileName}"
    file_name = f"{gb.testInfo.fileName}"
    with open(file_name, 'w') as file:
        now = datetime.now()
        # Format the date and time
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        # todo - check against actual files - oscMeas = vdss ?
        file.write(f"autoOutput, {formatted_date}\n")
        file.write(f"{file_name}\n")
        file.write(f"{gb.testInfo.serialNumber}\n")
        file.write(f"Time, PulseWidth({gb.testInfo.pulseUnits}), Vo(Vdc), Ipk(A), FinalTemp(C), Vdss(V), TempDiff(C), Vin(Vdc), PulseInd(uH)\n")


def append_data_output_file():
    '''

    :return:
    '''

    # todo change to include path before releasing
    #file_name = f"{gb.testInfo.filePath}{gb.testInfo.fileName}"
    file_name = f"{gb.testInfo.fileName}"
    with open(file_name, 'a') as file:
        now = datetime.now()
        # Format the date and time
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f'record data time: {formatted_date}')
        # todo varify variables against actual files
        file.write(
            f"{gb.testData.logTime}, {gb.testData.pulseWidth:.1f}, {gb.testData.vout:.3f}, "
            f"{gb.testData.ipk:.3f}, {gb.testData.finalTemp:.1f}, {gb.testData.vdss:.1f}, "
            f"{gb.testData.tempDiff:.1f}, {gb.testData.vin:.1f}, {gb.testData.lpulse:.2f}\n"
        )

