"""
models.py
    Database access and data helpers for bar/part testing.

"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, List, Optional, Sequence, Tuple

import pyodbc
from tkinter import messagebox

import globals as gb


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------


def _get_connection() -> pyodbc.Connection:
    """Create a new connection using settings from gb.initValues."""
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={gb.initValues.sqlServer};"
        f"DATABASE={gb.initValues.barDataBase};"
        f"UID={gb.initValues.serverUserName};"
        f"PWD={gb.initValues.serverPassword};"
        "ENCRYPT=no;"
    )


# ---------------------------------------------------------------------------
# Small data helpers
# ---------------------------------------------------------------------------


@dataclass
class BarMetadata:
    """Basic metadata for a bar, returned by get_bar_metadata."""
    bar_num: str
    build_num: Any
    furnace_num: Any
    fire_date: Any
    tape_lot: Any
    con_lot: Any
    die_lot: Any


# ---------------------------------------------------------------------------
# Main database class
# ---------------------------------------------------------------------------


class Database:
    """
    High-level API for all database operations used by the tester.
    Each method opens and closes its own connection.
    """

    # ---- Lookup / existence ------------------------------------------------

    def check_design_num(self, part_num: str) -> str:
        """
        Check that a part number exists in the limits table and return its design number.
        Shows a messagebox and returns "" if not found.
        """
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT Design_Num "
                f"FROM {gb.initValues.barLimitTable} "
                f"WHERE Part_Num = ?",
                (part_num,),
            )
            row = cursor.fetchone()

        if row is None:
            message_text = f"{part_num} not found"
            messagebox.showerror(
                title="Info",
                message=message_text,
                detail=(
                    "Double check the part number and try again.\n"
                    "Otherwise add a new part to the Limits database."
                ),
            )
            return ""

        return row[0]

    def check_record_exists(self, bar_num: str) -> bool:
        """
        Return True if a record exists in the bar data table for this bar number.
        """
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {gb.initValues.barDataTable} WHERE Bar_Num = ?",
                (bar_num,),
            )
            row = cursor.fetchone()

        if row is None:
            print("barNum not found")
            return False

        print("barNum found")
        return True

    def get_bar_metadata(self, bar_num: str) -> Optional[BarMetadata]:
        """
        Return metadata for the bar or None if not found.
        Uses column names from the Electrical / barDataTable schema.
        """
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT Bar_Num, Build_Num, Furnace_Num, Fire_Date, "
                f"TapeLot, ConLot, DieLot "
                f"FROM {gb.initValues.barDataTable} "
                f"WHERE Bar_Num = ?",
                (bar_num,),
            )
            row = cursor.fetchone()

        if not row:
            print("barNum not found")
            return None

        return BarMetadata(
            bar_num=row.Bar_Num,
            build_num=row.Build_Num,
            furnace_num=row.Furnace_Num,
            fire_date=row.Fire_Date,
            tape_lot=row.TapeLot,
            con_lot=row.ConLot,
            die_lot=row.DieLot,
        )

    def get_part_number_for_bar(self, bar_num: str) -> bool:
        """
        Check if a record exists for bar_num and, if so, populate
        gb.testInfo.partNum and gb.testInfo.designNum.
        Returns True if found, False otherwise.
        """
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT Catalog_Num, Design_Num "
                f"FROM {gb.initValues.barDataTable} "
                f"WHERE Bar_Num = ?",
                (bar_num,),
            )
            row = cursor.fetchone()

        if row is None:
            print("barNum not found")
            return False

        gb.testInfo.partNum = row[0]
        gb.testInfo.designNum = row[1]
        print("part no:", gb.testInfo.partNum)
        return True

    def get_good_part_list(self, bar_num: str) -> List[str]:
        """
        For IR/Hipot testing: return a list of Part_Num values for parts with
        Status 0 (undefined) or 1 (good), ordered by Part_Num ascending.
        """
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT CONVERT(varchar, Part_Num) "
                f"FROM {gb.initValues.barDataTable} "
                f"WHERE Bar_Num = ? AND (Status = 0 OR Status = 1) "
                f"ORDER BY Part_Num ASC",
                (bar_num,),
            )
            rows = cursor.fetchall()

        return [str(row[0]) for row in rows]

    # ---- Test history / status / defect -----------------------------------

    def check_test_history(self, serial_num: str) -> Tuple[int, int]:
        """
        Return (tested, history) flags for a serial number.
        If not found, returns (0, 0).
        """
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT Tested, History "
                f"FROM {gb.initValues.barDataTable} "
                f"WHERE PrimeKey = ?",
                (serial_num,),
            )
            row = cursor.fetchone()

        if row is None:
            return 0, 0

        return int(row[0]), int(row[1])

    def record_tested(self, code: int, serial_num: str) -> None:
        """Update Tested field for a serial number."""
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                f"SET Tested = ? "
                f"WHERE PrimeKey = ?",
                (code, serial_num),
            )

    def record_history(self, code: int, serial_num: str) -> None:
        """Update History field for a serial number."""
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                f"SET History = ? "
                f"WHERE PrimeKey = ?",
                (code, serial_num),
            )

    def record_defect(self, defect_code: int, serial_num: str) -> None:
        """Update Defect field for a serial number."""
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                f"SET Defect = ? "
                f"WHERE PrimeKey = ?",
                (defect_code, serial_num),
            )

    def record_status(self, status_code: int, serial_num: str) -> None:
        """Update Status field for a serial number."""
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                f"SET Status = ? "
                f"WHERE PrimeKey = ?",
                (status_code, serial_num),
            )

    def get_record_status(self, serial_num: str) -> int:
        """Return Status field for a serial number."""
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT Status "
                f"FROM {gb.initValues.barDataTable} "
                f"WHERE PrimeKey = ?",
                (serial_num,),
            )
            row = cursor.fetchone()

        return int(row[0]) if row else 0

    # ---- Record creation / copying ----------------------------------------

    def create_records_for_bar(self) -> None:
        """
        Create electrical records for each position on the bar.
        Uses gb.testLimits and gb.testInfo.
        """
        num_positions = gb.testLimits["numPositions"]

        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()

            for index in range(1, num_positions + 1):
                if index < 10:
                    position = f"00{index}"
                elif index < 100:
                    position = f"0{index}"
                else:
                    position = str(index)

                serial_num = f"{gb.testInfo.barNum}{position}"

                cursor.execute(
                    f"INSERT INTO {gb.initValues.barDataTable} "
                    "(PrimeKey, Bar_Num, Catalog_Num, Design_Num, Part_Num, "
                    " Build_Num, Furnace_Num, Fire_Date, Defect, Status, "
                    " TapeLot, ConLot, DieLot) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        serial_num,
                        gb.testInfo.barNum,
                        gb.testInfo.partNum,
                        gb.testInfo.designNum,
                        index,
                        gb.testInfo.buildNum,
                        gb.testInfo.furnaceNum,
                        gb.testInfo.fireDate,
                        "0",
                        "0",
                        gb.testInfo.tapeLot,
                        gb.testInfo.conLot,
                        gb.testInfo.dieLot,
                    ),
                )

    def copy_data_row_to_history(self, serial_num: str) -> None:
        """
        Copy a row of data from the electrical/bar data table to the history table.
        PrimeKey in the electrical table becomes Serial_Num in history.
        """
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {gb.initValues.barHistoryTable} "
                "(Serial_Num, Bar_Num, Catalog_Num, Design_Num, "
                " Variant, Part_Num, Build_Num, Furnace_Num, Date_Tested, Fire_Date, "
                " Defect, Status, Frequency, Level, LPri, LSec, Leakage, QPri, RPri, "
                " RSec, LPulse, VOut, IPulse, VHypot, IHypot, THypot, IRVoltage, "
                " IRResistance, IRTime, stxpreLpri, stxpostLpri, Vout25, Vout85, "
                " LPulse25, LPulse85, Rework, TurnsRatio, stxpostQpri, stxpreQpri, "
                " stxpreRpri, stxpostRpri, Tested, History) "
                "SELECT "
                " PrimeKey, Bar_Num, Catalog_Num, Design_Num, "
                " Variant, Part_Num, Build_Num, Furnace_Num, Date_Tested, Fire_Date, "
                " Defect, Status, Frequency, Level, LPri, LSec, Leakage, QPri, RPri, "
                " RSec, LPulse, VOut, IPulse, VHypot, IHypot, THypot, IRVoltage, "
                " IRResistance, IRTime, stxpreLpri, stxpostLpri, Vout25, Vout85, "
                " LPulse25, LPulse85, Rework, TurnsRatio, stxpostQpri, stxpreQpri, "
                " stxpreRpri, stxpostRpri, Tested, History "
                f"FROM {gb.initValues.barDataTable} "
                "WHERE PrimeKey = ?",
                (serial_num,),
            )

    # ---- Parameter test data (LCR/transformer) ----------------------------

    def record_param_data(self, serial_num: str, tested_flag: int) -> None:
        """
        Record measured LCR test data (transformer/primary/secondary) to the table
        and mark tested/date-tested.
        """
        today = date.today().strftime("%Y/%m/%d")

        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET LPri = ?, LSec = ?, Leakage = ?, QPri = ?, RPri = ?, RSec = ?, "
                "    Frequency = ?, Level = ?, Tested = ?, Date_Tested = ? "
                "WHERE PrimeKey = ?",
                (
                    gb.testData.priInd,
                    gb.testData.secInd,
                    gb.testData.priLkg,
                    gb.testData.priQ,
                    gb.testData.priRes,
                    gb.testData.secRes,
                    gb.initValues.lcrFrequency,
                    gb.initValues.lcrIndLevel,
                    tested_flag,
                    today,
                    serial_num,
                ),
            )

    def record_stx_pre(self, serial_num: str) -> None:
        """
        Record pre-STX inductance, Q, and resistance.
        """
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET stxpreLpri = ?, stxpreQpri = ?, stxpreRpri = ? "
                "WHERE PrimeKey = ?",
                (
                    gb.testData.priInd,
                    gb.testData.priQ,
                    gb.testData.priRes,
                    serial_num,
                ),
            )

    def record_stx_post(self, serial_num: str) -> None:
        """
        Record post-STX inductance, Q, and resistance.
        """
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET stxpostLpri = ?, stxpostQpri = ?, stxpostRpri = ? "
                "WHERE PrimeKey = ?",
                (
                    gb.testData.priInd,
                    gb.testData.priQ,
                    gb.testData.priRes,
                    serial_num,
                ),
            )

    def record_pre_fire_resistance(self, serial_num: str) -> None:
        """
        Record pre-fire resistances (RPri, RSec) which will be overwritten later.
        """
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET RPri = ?, RSec = ? "
                "WHERE PrimeKey = ?",
                (gb.testData.priRes, gb.testData.secRes, serial_num),
            )

    # ---- Inductor tests ----------------------------------------------------

    def record_inductor_data(self, status: int, serial_num: str) -> None:
        """
        Record inductor test results at zero bias into the table.
        """
        today = date.today().strftime("%Y/%m/%d")

        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET LPri = ?, QPri = ?, RPri = ?, "
                "    Frequency = ?, Level = ?, Status = ?, Date_Tested = ? "
                "WHERE PrimeKey = ?",
                (
                    gb.testData.priInd,
                    gb.testData.priQ,
                    gb.testData.priRes,
                    gb.initValues.lcrFrequency,
                    gb.initValues.lcrIndLevel,
                    status,
                    today,
                    serial_num,
                ),
            )

    def record_inductor_bias_data(
        self,
        result_window: Any,
        serial_num: str,
        status_flag: Any,
    ) -> None:
        """
        Record inductor DC bias results to a CSV file.
        One line per serial number: s/n, defect/status, R, L/Q pairs for each bias.
        """
        row_data: List[Any] = [
            serial_num,
            status_flag,
            gb.testData.indRes,
        ]

        num_items = result_window.dcBiasListBox.size()
        for idx in range(num_items):
            row_data.append(gb.testData.indInd[idx])
            row_data.append(gb.testData.indQ[idx])

        file_name = os.path.join(gb.testInfo.filePath, gb.testInfo.fileName)
        with open(file_name, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row_data)

    def create_inductor_file_header(self, result_window: Any) -> None:
        """
        Create a CSV file and header for inductor bias results.
        Should be called after DC bias settings are established.
        """
        today = date.today().strftime("%m/%d/%Y")

        os.makedirs(gb.testInfo.filePath, exist_ok=True)

        file_name = os.path.join(gb.testInfo.filePath, gb.testInfo.fileName)
        with open(file_name, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow([f"Parameter Test v{gb.system.version}"])
            writer.writerow(["Date", today])
            writer.writerow(["Bar", gb.testInfo.barNum])
            writer.writerow(["Design", gb.testInfo.designNum])
            writer.writerow(["Build", gb.testInfo.buildNum])
            writer.writerow(["Furn", gb.testInfo.furnaceNum])
            writer.writerow(["Fire Date", gb.testInfo.fireDate])
            writer.writerow(["Freq", gb.initValues.lcrFrequency])
            writer.writerow(["Level", gb.initValues.lcrIndLevel])

            header: List[str] = ["Serial", "Defect", "R"]
            items = result_window.dcBiasListBox.get(0, "end")
            for item in items:
                header.append(f"L({item})")
                header.append(f"Q({item})")
            writer.writerow(header)

    # ---- Output / pulse tests (25°C / 85°C / combined) --------------------

    def record_output_data(self) -> None:
        """
        Add pulse/output test results to the DB.
        Also stores LPulse25/Vout25 at the same time.
        Uses gb.testData.status and gb.testInfo.serialNumber.
        """
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET Status = ?, LPulse = ?, VOut = ?, IPulse = ?, "
                "    LPulse25 = ?, Vout25 = ? "
                "WHERE PrimeKey = ?",
                (
                    gb.testData.status,
                    gb.testData.lpulse,
                    gb.testData.vout,
                    gb.testData.ipk,
                    gb.testData.lpulse,
                    gb.testData.vout,
                    gb.testInfo.serialNumber,
                ),
            )

    def record_pulse_25_data(self, serial_num: str) -> None:
        """
        Record Vout25 and LPulse25 fields.
        """
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET Vout25 = ?, LPulse25 = ? "
                "WHERE PrimeKey = ?",
                (gb.testData.vout, gb.testData.lpulse, serial_num),
            )

    def record_pulse_85_data(self, serial_num: str) -> None:
        """
        Record Vout85 and LPulse85 fields.
        S"""
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET Vout85 = ?, LPulse85 = ? "
                "WHERE PrimeKey = ?",
                (gb.testData.vout, gb.testData.lpulse, serial_num),
            )

    # ---- IR / Hipot tests --------------------------------------------------

    def record_hipot_data(self, status_code: int, serial_num: str) -> None:
        """
        Record IR/Hipot test results for a serial number.
        """
        with _get_connection() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {gb.initValues.barDataTable} "
                "SET Status = ?, IRVoltage = ?, IRResistance = ?, IRTime = ?, "
                "    VHypot = ?, IHypot = ?, THypot = ? "
                "WHERE PrimeKey = ?",
                (
                    status_code,
                    gb.testData.irVoltage,
                    gb.testData.irResistance,
                    gb.testData.irTime,
                    gb.testData.hipotVoltage,
                    gb.testData.hipotCurrent,
                    gb.testData.hipotTime,
                    serial_num,
                ),
            )


    # ---- Limits ------------------------------------------------------------

    def load_test_limits(self, part_num: str) -> dict:
        """
        Load test limits for the given part number from the limits table.
        Also sets gb.testInfo.testType and gb.testInfo.testCheck based on the
        testType field.
        """
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {gb.initValues.barLimitTable} "
                f"WHERE Part_Num = ?",
                (part_num,),
            )
            row = cursor.fetchone()

        if row is None:
            raise ValueError(f"Part_Num '{part_num}' not found in limits table")

        limit_fields = (
            "partNum",
            "designNum",
            "numPositions",
            "numTerms",
            "numVariants",
            "prefireFixture",
            "fixtureNum",
            "testType",
            "priLmin",
            "priLmax",
            "priQmin",
            "priRmin",
            "priRmax",
            "leakageMin",
            "leakageMax",
            "coupling",
            "secLmin",
            "secLmax",
            "secRmin",
            "secRmax",
            "pulseLmin",
            "pulseLmax",
            "outputVoltmin",
            "pulseLcur",
            "hipotVoltage",
            "hipotRamp",
            "hipotCur",
            "hipotTime",
            "irVoltage",
            "irResistance",
            "irTime",
            "stx%Change",
            "outputVoltmin85",
            "pulseLmin85",
            "outputGraphline",
            "startingPulseWidth",
            "turnsRatio",
            "lcrlevel",
            "indL100min",
            "indL100max",
            "satCur",
            "satLmin%",
            "hipotType",
        )

        packed = dict(zip(limit_fields, row))
        test_type = packed.get("testType", "")

        # Type of part: transformer (T) or inductor (I)
        if "T" in test_type:
            gb.testInfo.testType = "T"
        elif "I" in test_type:
            gb.testInfo.testType = "I"
        else:
            gb.testInfo.testType = "X"

        # Production (P) or development (D)
        if "P" in test_type:
            gb.testInfo.testCheck = "P"
        elif "D" in test_type:
            gb.testInfo.testCheck = "D"
        else:
            gb.testInfo.testCheck = "X"

        return packed

    # ---- ASCII autoOutput helpers ----------------------------------------

    def create_output_file_header(self) -> None:
        """
        Create the header for ASCII files of output steps (autoOutput).
        Uses gb.testInfo for file name and serial / units.
        """
        file_name = gb.testInfo.fileName  # path can be included in fileName if desired

        with open(file_name, "w", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"autoOutput, {now}\n")
            f.write(f"{file_name}\n")
            f.write(f"{gb.testInfo.serialNumber}\n")
            f.write(
                "Time, "
                f"PulseWidth({gb.testInfo.pulseUnits}), "
                "Vo(Vdc), Ipk(A), FinalTemp(C), Vdss(V), "
                "TempDiff(C), Vin(Vdc), PulseInd(uH)\n"
            )

    def append_data_output_file(self) -> None:
        """
        Append one line of output data to the ASCII file created by
        create_output_file_header(). Uses gb.testData fields.
        """
        file_name = gb.testInfo.fileName

        with open(file_name, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"record data time: {now}")
            f.write(
                f"{gb.testData.logTime}, "
                f"{gb.testData.pulseWidth:.1f}, "
                f"{gb.testData.vout:.3f}, "
                f"{gb.testData.ipk:.3f}, "
                f"{gb.testData.finalTemp:.1f}, "
                f"{gb.testData.vdss:.1f}, "
                f"{gb.testData.tempDiff:.1f}, "
                f"{gb.testData.vin:.1f}, "
                f"{gb.testData.lpulse:.2f}\n"
            )

