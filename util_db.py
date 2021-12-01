import sqlite3
from sqlite3.dbapi2 import Error


DB_PATH = "./sandbox.db"
BLOCKING_EVENTS = "('PANNES MICRO ARRETS', 'ATTENTE OPERATEUR', 'ARRETS FONCTIONNELS', 'PERTE EXPLOITATION')"


def connect_to_db(db_path = None):
    if db_path :
        return sqlite3.connect(db_path)
    else : 
        return sqlite3.connect(DB_PATH)

def deconnect_from_db(connection):
    connection.close()

def get_mean_time_to_repair(module_key, connection):
    if connection and module_key: 
        cursor = connection.cursor()
        query = "SELECT AVG(duration) FROM DF109BFD_Events WHERE module ='" + module_key + "' AND type IN " + BLOCKING_EVENTS
        return cursor.execute(query).fetchone()[0]
    else:
        Error("No SQLit connection or module id")     

def get_all_module_ids_db(connection):
    if connection:
        cursor = connection.cursor()
        query = "SELECT DISTINCT module FROM DF109BFD_Events ORDER BY module"
        return cursor.execute(query).fetchall()
    else :
        Error("No SQLit connection") 
        

def get_exit_timestamps_by_module_id(module_key, connection):
    if connection and module_key:
        cursor = connection.cursor()
        query = "SELECT timestamp FROM DF109BFD_Exits WHERE module ='" + module_key + "'ORDER by timestamp"
        return cursor.execute(query).fetchall()
        
    else:
        Error("No SQLit connection or module id") 

# get timestamp_ini and timestamp_end for all events for a module_id
def get_events_timestamps_by_module_id(module_key, connection):
    if connection and module_key:
        cursor = connection.cursor()
        query = "SELECT timestamp_ini, timestamp_end, type FROM DF109BFD_Events WHERE module ='" + module_key + "' ORDER BY timestamp_ini"
        return cursor.execute(query).fetchall()  
    else:
        Error("No SQLit connection or module id")

def get_nb_parts_by_module_id(module_key, connection):
    if connection and module_key:
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM DF109BFD_Exits WHERE module='" + module_key + "'"
        return cursor.execute(query).fetchone()[0] 
    else:
        Error("No SQLit connection or module id")


def get_nb_blocking_events_by_module_id(module_key, connection):
    if connection and module_key:
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM DF109BFD_Events WHERE module='" + module_key + "' AND type IN " + BLOCKING_EVENTS 
        return cursor.execute(query).fetchone()[0]
    else:
       Error("No SQLit connection or module id") 

def get_events_overlapping_timestamps_by_module_id(module_key, t_begin, t_end, connection):
    if module_key and t_begin and t_end:
        cursor = connection.cursor()
        query = ("SELECT type, timestamp_ini, timestamp_end, duration FROM DF109BFD_Events" + 
                 " WHERE module='" + module_key + "' " +
                       "AND ( (timestamp_ini BETWEEN " + str(t_begin) + " AND " + str(t_end) + ")" +
                          "OR (timestamp_end BETWEEN " + str(t_begin) + " AND " + str(t_end) + ")" + 
                        ")") 
        return cursor.execute(query).fetchall()
    
 