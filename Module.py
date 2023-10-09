import colorama
import logging
import os

from LoadModuleToDB import *
from QueriesModule import *

colorama.init(autoreset=True)

# Create and configure the logger
LOG_FORMAT = "%(levelname)s %(asctime)s -%(message)s"
logging.basicConfig(filename="LOG_FILES\\MODULE.log",
                    level=logging.DEBUG,
                    format=LOG_FORMAT)
logger = logging.getLogger()


# Checking and verifying the connection to the database
def db_connection():
    try:
        # creating connection to the database and name of the Database
        amydb = sqlite3.connect('DATABASES\\ASM_MODULE.db', timeout=2)

        # setting the connection isolation level on exclusive
        amydb.isolation_level = 'EXCLUSIVE'

        # creating cursor to database
        myCursor = amydb.cursor()

        query = "insert into module(MODULE_ID, MODULE_NAME, MAT_NUMBER, FS, MANUFACTURER, MANUFACTURER_YEAR, " \
                "MANUFACTURER_MONTH,SERIAL_NUMBER, ADDED_ON, ADDED_BY, MODULE_STATUS) values('Test','0','0', '0','0'," \
                "'0','0','0','0','0','0')"

        # execute the test query
        myCursor.execute(query)

        # rollback every change made in the last execute
        amydb.rollback()

        # setting the connection isolation level on deferred
        amydb.isolation_level = 'DEFERRED'

        # database connection failed
        print(Fore.GREEN + f" Database Access is Connected")

        return amydb

    except sqlite3.OperationalError as e:
        print(Fore.RED + f"{e}: Database Access is Denied, Please close ASM_MODULE.db")
        return None


# creating a function for Reading and Saving the QrCode data
def READ_QR_CODE():
    # Scan the Assembly Qr code to Insert the data
    AQRCode = input(Fore.LIGHTMAGENTA_EX + 'Module QRCode :')

    # Replacing '+' and '-' with '_'
    AQRCode = AQRCode.replace("+", "_")
    AQRCode = AQRCode.replace("-", "_")
    ASSEMBLY_ID = AQRCode[2:]

    # checking the QR Code existed in the database or not and format of the QR Code
    if GetQRCodeFromDB(ASSEMBLY_ID, amydb) == 1:
        if change_status(AQRCode):
            return None
        print(Fore.RED + " Scanned Module Data Already Exist in Database . \n")

    elif Check_Code(AQRCode, logger):

        folder_Name = create_folder(AQRCode)
        LOAD_ASSEMBLY_TO_DB(AQRCode, amydb, logger, folder_Name)


def Check_Code(AQRCode, logger):
    # Name of the user
    SIGNATURE = gt.getuser()
    # Checking the length and format of the QRCode
    if not (AQRCode[0:2] == "1P" and len(AQRCode) >= 25 and AQRCode.count('_') == 4):
        logger.error(" in " + AQRCode[2:] + " Invalid Module QRCode entered wrong format " + " - performed by " + SIGNATURE)
        print(Fore.RED + "Invalid Module QRCode because entered in wrong format. \n")
        return False
    # Splitting the QRCode
    ASSEMBLY_ID = AQRCode[2:]
    split_ASSEMBLY_ID = ASSEMBLY_ID.split("_")

    # In material number removing Data Identifiers (1P)
    MAT_NUMBER = split_ASSEMBLY_ID[0]
    if not (MAT_NUMBER.isnumeric() and len(MAT_NUMBER) == 8):
        logger.error(" in " + ASSEMBLY_ID + " Invalid Material Number " + MAT_NUMBER + " - performed by " + SIGNATURE)
        print(Fore.RED + "Invalid Material Number. \n ")
        return False

    FS = split_ASSEMBLY_ID[1]
    if not (len(FS) == 2 and FS.isnumeric() and not FS == "00"):
        logger.error(" in " + ASSEMBLY_ID + " Invalid Function Stand " + FS + " - performed by " + SIGNATURE)
        print(Fore.RED + "Invalid Function Stand. \n")
        return False

    # Checking the condition for Identifier "S" for Manufacturer
    MANUFACTURER = split_ASSEMBLY_ID[2]
    if not MANUFACTURER.startswith('S'):
        logger.error(
            " in " + ASSEMBLY_ID + " Invalid Manufacturer Name does not start with S " + MANUFACTURER + "- performed "
                                                                                                        "by " + SIGNATURE)
        print(Fore.RED + "Invalid Manufacturer Name. \n")
        return False

    MANUFACTURER = split_ASSEMBLY_ID[2][1:]

    # Adding if condition to remove S from Manufacturer
    if not MANUFACTURER.isalpha():
        logger.error(
            " in " + ASSEMBLY_ID + " Invalid Manufacturer Name " + MANUFACTURER + " - performed by " + SIGNATURE)
        print(Fore.RED + "Invalid Manufacturer Name. \n")
        return False

    MANUFACTURER_DATE = split_ASSEMBLY_ID[3]

    if not len(MANUFACTURER_DATE) == 2:
        logger.error(
            " in " + ASSEMBLY_ID + " Invalid Manufacturer Date " + MANUFACTURER_DATE + " - performed by " + SIGNATURE)
        print(Fore.RED + "Invalid Manufacturer Date. \n")
        return False

    # Condition for Manufacturer Year
    MANUFACTURER_YEAR = MANU_YEAR(str(MANUFACTURER_DATE[:1]))
    if not MANUFACTURER_YEAR.isnumeric():
        logger.error(
            " in " + ASSEMBLY_ID + " Invalid Manufacturer Year " + MANUFACTURER_YEAR + " - performed by " + SIGNATURE)
        print(Fore.RED + "Invalid Manufacturer Year. \n")
        return False
    # Condition for Manufacturer Month
    MANUFACTURER_MONTH = MANU_MONTH(str(MANUFACTURER_DATE[1:2]))
    if not MANUFACTURER_MONTH.isnumeric():
        logger.error(
            "in " + ASSEMBLY_ID + " Invalid Manufacturer Month " + MANUFACTURER_MONTH + " - performed by " + SIGNATURE)
        print(Fore.RED + "Invalid Manufacturer Month. \n")
        return False

    # Condition for Serial Number acceptance
    SERIAL_NUMBER = split_ASSEMBLY_ID[4]
    if not (SERIAL_NUMBER.isnumeric() and len(SERIAL_NUMBER) == 4 and not SERIAL_NUMBER == "0000"):
        logger.error(" in " + ASSEMBLY_ID + " Invalid Serial Number " + SERIAL_NUMBER + " - performed by " + SIGNATURE)
        print(Fore.RED + " Invalid Serial Number. \n")
        return False

    return True


def create_folder(code):
    folder = get_folder(code, "DATABASES\\MODULE")
    if not folder:

        folder_name = ""

        while True:
            folder_name = input(Fore.LIGHTWHITE_EX + f"Please enter Module Name: ")
            folder_name = folder_name.replace(" ", "_")
            if folder_name:
                break

        # create path to the storage of the .db file
        path = f"DATABASES\\MODULE\\{code[2:10]}_{folder_name}\\Files"

        os.makedirs(path)
        return folder_name

    else:
        a = folder.split("\\")[-1]
        return a.split('_', 1)[1]


def get_folder(code, path):
    """
    Searches for a folder with the specified code in a given path.
1P03332222_01_SRD_R7_1122
    Args:
        code (str): The code to search for.
        path (str): The path to search in.

    Returns:
        str: The full path to the found folder.
             If no matching folder is found, returns None.
    """
    code = code[2:10]

    # Extract the desired portion of the code
    for item in os.listdir(path):

        item_path = os.path.join(path, item)

        if os.path.isdir(item_path) and code in item:
            # Return the full path to the found folder
            return f"{path}\\{item}"

        # Return None if no matching folder is found
    return False


# Storing and getting the records from the Database
def GetQRCodeFromDB(ASSEMBLY_ID, amydb):
    myCursor = amydb.cursor()
    query = GetAssemblyRecordsFrom_DB()
    values = myCursor.execute(query, [ASSEMBLY_ID]).fetchall()
    return len(values)


def yesno():
    """
    this function ask for user input. if "Y" or "y" is entered the function returns true.if "N", "n" or "" is entered
    the function returns False. else the function starts from the beginning.

    arg:
    None

    return:
    False: if "Y" or "y" was entered
    True: if "N", "n" or "" was entered
    """

    # while loop if input is not what is excepted
    while True:

        # user input
        user_input = input(Fore.YELLOW + f"Please enter Y or N: (N) ")

        # check user input
        # if "Y" or "y"
        if user_input == "Y" or user_input == "y":

            return True

        # if "N", "n" or ""
        elif user_input == "N" or user_input == "n" or user_input == "":
            return False

        # incorrect input loop starts again
        else:
            print(Fore.RED + f"Invalid input, please try again.")


def new_status():
    # while loop if input is not what is excepted
    while True:
        # user input
        user_input = input(Fore.YELLOW + f"Please choose Status (1) Raw, (2) Updated, (3) Broken: ")
        print("")
        # check user input

        if user_input == "1":
            return "Raw"

        elif user_input == "2":
            return "Updated"

        elif user_input == "3":
            return "Broken"

        # incorrect input loop starts again
        else:
            print(Fore.RED + f"Invalid input, please try again.")


def change_status(code):
    print(Fore.LIGHTBLUE_EX + f"Do you want to change the Status of the scanned Module?")
    if not yesno():
        return False

    mycursor = amydb.cursor()
    query = get_status_query()
    status = mycursor.execute(query, [code[2:]]).fetchone()
    print(Fore.LIGHTBLUE_EX + f"actual status: {status[0]}")

    status = new_status()
    query = change_status_query()
    mycursor.execute(query, [status, code[2:]])
    amydb.commit()
    amydb.close()
    return True


# creating Main Loop
if __name__ == '__main__':

    while True:
        amydb = db_connection()

        if amydb:

            print(Fore.LIGHTCYAN_EX + 'Please Scan Correct Module QRCode.')
            READ_QR_CODE()

        else:
            time.sleep(5)
            break
