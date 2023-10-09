# Inserting parameters into a pcb table inside the Database
def InsertAssemblyDetailsInto_DB():
    return "insert into module(MODULE_ID, MODULE_NAME, MAT_NUMBER, FS, MANUFACTURER, MANUFACTURER_YEAR, " \
           "MANUFACTURER_MONTH, " \
           "SERIAL_NUMBER, ADDED_BY, MODULE_STATUS) values(?,?,?,?,?,?,?,?,?,?)"


#  Retrieving the data from a pcb table inside the Database
def GetAssemblyRecordsFrom_DB():
    return "Select * from module WHERE MODULE_ID = ? "


# update the status of a pcb in the database
def change_status_query():
    return f"UPDATE module SET MODULE_STATUS = ? WHERE MODULE_ID = ?"


def get_status_query():
    return f"SELECT MODULE_STATUS FROM module WHERE MODULE_ID = ?"