import getpass as gt
import sqlite3
import sys
import time

from MonthYearFormat import *
from colorama import Fore
from QueriesModule import *


def LOAD_ASSEMBLY_TO_DB(ASSEMBLY_ID, amydb, logger, folder_Name):
    # Name of the user
    SIGNATURE = gt.getuser()
    # Splitting the QRCode
    split_ASSEMBLY_ID = ASSEMBLY_ID.split("_")
    # Removing Data Identifiers (1P) and storing Material number
    MAT_NUMBER = split_ASSEMBLY_ID[0][2:]
    # Condition for storing Function Stand
    FS = split_ASSEMBLY_ID[1]
    # Removing Data Identifiers (S) and storing Manufacturer Name
    MANUFACTURER = split_ASSEMBLY_ID[2][1:]
    # Condition for storing Manufacturer Year and Month
    MANUFACTURER_DATE = split_ASSEMBLY_ID[3]
    MANUFACTURER_YEAR = MANU_YEAR(str(MANUFACTURER_DATE[:1]))
    MANUFACTURER_MONTH = MANU_MONTH(str(MANUFACTURER_DATE[1:2]))
    # Condition for storing Serial Number
    SERIAL_NUMBER = split_ASSEMBLY_ID[4]
    # Condition for Status after is Raw(1), Update(2) and Broken(3)
    STATUS = "Raw"
    # Condition for storing Assembly Name
    ASSEMBLY_NAME = folder_Name

    try:
        # To create, modify and insert data into the tables inside Database we need cursor
        myCursor = amydb.cursor()
        # Inserting parameters into a table inside the Database
        query = InsertAssemblyDetailsInto_DB()
        # Calling the function and Passing the values
        val = (ASSEMBLY_ID[2:], ASSEMBLY_NAME, MAT_NUMBER, FS, MANUFACTURER, MANUFACTURER_YEAR, MANUFACTURER_MONTH,
               SERIAL_NUMBER, SIGNATURE, STATUS)
        # Inserting data into Table
        myCursor.execute(query, val)

        # save data into the database
        amydb.commit()
        logger.info(ASSEMBLY_ID + " - performed by " + SIGNATURE)
        print(Fore.GREEN + "Data Saved. \n")
        amydb.close()
        return True

    except sqlite3.OperationalError as e:
        print(Fore.RED + f"{e}: Database Access is Denied, Please close Database ASM_MODULE.db")
        time.sleep(5)
        sys.exit(0)

    except sqlite3.IntegrityError as e:
        print(Fore.RED + f"MODULE already exist in Database.")
        return None
