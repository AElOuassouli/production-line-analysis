from pprint import pprint
from pandas import DataFrame

import util_yaml as uyaml
import util_db as udb
import util_calculation as ucalc
import util_anomaly_detection as uad
import util_viz as uviz


PLOT = False
TESTS_FOLDER = "./plots/anomaly_detection"

# Parsing the YAML FILE
yaml_data = uyaml.load_yaml_content_for_file()
# Connection to the database 
connection = udb.connect_to_db()

results = dict()

for object_id in yaml_data:
    if yaml_data[object_id]["type"] == "module": 
        print("Computing for module :" + object_id)
        results[object_id] = {}
        # Object key corresponds to ids in the database
        module_key = yaml_data[object_id]["key"]
        
        #querying necessary data from the database
        exit_timestamps = udb.get_exit_timestamps_by_module_id(module_key, connection)  
        event_timestamps = udb.get_events_timestamps_by_module_id(module_key, connection)
        nb_blocking_events = udb.get_nb_blocking_events_by_module_id(module_key, connection)
        
        # Computing Average Cycle Time (considering overlapping events)
        if exit_timestamps and event_timestamps:
            results[object_id]["cycles_CYCLE_TIME"] = ucalc.compute_avg_instantaneous_cycle_time(exit_timestamps, event_timestamps)
        else : 
            results[object_id]["cycles_CYCLE_TIME"] = None
        print("     Cycle Time:         " + str(results[object_id]["cycles_CYCLE_TIME"]))

        # Computing Mean Time To Repair (MTTR)
        results[object_id]["cycles_MTTR"] = udb.get_mean_time_to_repair(module_key, connection)
        print("     MTTR:               " + str(results[object_id]["cycles_MTTR"]))

        # Computing Mean Time To Fail (MTTF)
        if exit_timestamps:
            nb_cycles = len(exit_timestamps) - 1
            results[object_id]["cycles_MTTF"] = ucalc.compute_mean_time_to_fail(results[object_id]["cycles_CYCLE_TIME"], nb_cycles,  nb_blocking_events)
        else : 
            results[object_id]["cycles_MTTF"] = None
        print("     MTTF:               " + str(results[object_id]["cycles_MTTF"]))

        ##### Anomaly detection 
        if exit_timestamps:
            # Computing all cycles. Returns cycle duration and first endpoint 
            cycles_duration, first_endpoints = ucalc.compute_cycle_times(exit_timestamps)
            if cycles_duration and first_endpoints:
                df = DataFrame({'first_endpoint': first_endpoints, "cycle_duration":cycles_duration})

                results[object_id]["cycles_Nb"] =  int(len(df))
                results[object_id]["cycles_Mean"] =  df["cycle_duration"].mean()
                results[object_id]["cycles_Total_duration"] = df["cycle_duration"].sum()
                
                # Anomaly detection algorithms. 
                # Anomalies labels are -1 for anomaly, != -1 for non-anomaly

                ## Applying Isolation Forest.
                ## Second parameter corresponds to contamination
                ## Anomaly labels in df. Column name : anomaly_if
                #print("Anomaly detection - Isolation Forest - Begin")
                #df = uad.isolation_forsest_based_ad(df, "auto")
                #print("Anomaly detection - Isolation Forest - End")

                ## Applying DBSCAN. 
                ## Second parameter: min_samples. 
                ## Third parameter : epsilon
                ## Anomaly labels in df. Column name: anomaly_dbscan
                print("Anomaly detection - DBSCAN")
                df = uad.dbscan_based_ad(df, int(0.05*len(df)), 5)
                print("Anomaly detection - DBSCAN - Ended")
                # Anomaly events analysis

                results = uad.anomaly_events_analysis(df, "anomaly_dbscan", object_id, module_key, connection, results)

pprint(results)
with open("./results.txt", "w") as fp:
    pprint(results, fp)
print("Results file saved in " + "./results.txt")

# 2D Vizualisation of production line
uviz.plot_prodcution_graph_networkx(yaml_data, results, "production_graph.png")
uviz.plot_production_line_pyvis(yaml_data, results, "production_graph.html")

# Deconnnection for DB
udb.deconnect_from_db(connection)