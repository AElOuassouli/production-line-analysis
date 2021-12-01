import matplotlib.pyplot as plt
import pandas as pd
import os

from statistics import mean
from statistics import harmonic_mean

import util_db as udb
import util_calculation as ucalc
import util_viz as uviz


from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS


FIG_SIZE = 300


def get_outliers(df, anomaly_attribute):
    return df.loc[df[anomaly_attribute] == -1, ['first_endpoint', 'cycle_duration']]


def isolation_forsest_based_ad(df, contamination, plot = False, object_id = None, tests_folder = None):
    data_shaped = df["cycle_duration"].values.reshape(-1, 1)
    isolation_forest = IsolationForest(contamination=contamination).fit(data_shaped)
    df['anomaly_if'] = pd.Series(isolation_forest.predict(data_shaped))
    df['anomaly_if_scores'] = pd.Series(isolation_forest.decision_function(data_shaped))

    if object_id and tests_folder and plot:
        uviz.plotAnomalies(df, 'anomaly_if', object_id, tests_folder, "isolation_forest" + str(contamination) )
        uviz.plotAnomaliesLog(df, 'anomaly_if', object_id, tests_folder, "isolation_forest" + str(contamination) + "log" )
    return df

# ref : https://www.analyticsvidhya.com/blog/2021/06/univariate-anomaly-detection-a-walkthrough-in-python/
def find_anomalies_iqr(value, lower_bound, upper_bound):
    if value < lower_bound or value > upper_bound:
        return -1
    else:
        return 1

def iqr_based_ad(df, plot = None, object_id = None, tests_folder = None):
    quantile_25 = df["cycle_duration"].quantile(0.25)
    quantile_75 = df["cycle_duration"].quantile(0.75)
    IQR = quantile_75 - quantile_25
    lower_bound = quantile_25 - IQR*1.5
    upper_bound = quantile_75 + IQR*1.5
    df["anomaly_iqr"] = df["cycle_duration"].apply(find_anomalies_iqr, args=(lower_bound, upper_bound))
    if object_id and tests_folder and plot:
        uviz.plotAnomaliesLog(df, "anomaly_iqr", object_id, tests_folder, "iqr")
    return df


def one_class_SVM_based_ad(df, plot = None, object_id = None, tests_folder = None):
    ocSVM = OneClassSVM(gamma='auto', )
    data_shaped = df["cycle_duration"].values.reshape(-1,1)
    ocSVM.fit(data_shaped)
    df['anomaly_ocsvm'] = pd.Series(ocSVM.predict(data_shaped))
    df['anomaly_ocsvm_scores'] = pd.Series(ocSVM.decision_function(data_shaped))
    print(df)
    if object_id and tests_folder and plot :
        uviz.plotAnomaliesLog(df, 'anomaly_ocsvm', object_id, tests_folder, "ocsvmLog")
    return df
   

def local_outlier_foctor_based_ad(df, plot = None, object_id = None, tests_folder= None):
    lof = LocalOutlierFactor()
    data_shaped = df["cycle_duration"].values.reshape(-1,1)
    df['anomaly_lof'] = pd.Series(lof.fit_predict(data_shaped))
    df['anomaly_lof_score'] = pd.Series(lof.negative_outlier_factor_)
    print(lof.negative_outlier_factor_)
    
    if object_id and tests_folder and plot :
        uviz.plotAnomaliesLog(df, 'anomaly_lof', object_id, tests_folder, "lofLog")
    return df

def dbscan_based_ad(df,min_samples, epsilon, plot = None, object_id = None, tests_folder = None):
    dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)
    data_shaped = df["cycle_duration"].values.reshape(-1,1)
    dbscan.fit(data_shaped)
    df['anomaly_dbscan'] = pd.Series(dbscan.labels_)
    if object_id and tests_folder and plot :
        uviz.plotAnomalies(df, 'anomaly_dbscan', object_id, tests_folder, "dbscan_minsamples" + str(min_samples) + "_epsilon_" + str(epsilon))
        uviz.plotAnomaliesLog(df, 'anomaly_dbscan', object_id, tests_folder, "dbscan_minsamples" + str(min_samples) + "_epsilon_" + str(epsilon) + "log")
        uviz.plotClusters(df, "anomaly_dbscan", object_id, tests_folder, "dbscan_minsamples" + str(min_samples) + "_epsilon_" + str(epsilon)) 
    return df

def optics_based_ad(df, plot = None, object_id = None, tests_folder = None):
    optics = OPTICS(max_eps=3, min_samples=20)
    data_shaped = df["cycle_duration"].values.reshape(-1,1)
    optics.fit(data_shaped)
    df['anomaly_optics'] = pd.Series(optics.labels_)
    if object_id and tests_folder and plot :
        uviz.plotClusters(df, 'anomaly_optics', object_id, tests_folder, "optics" )
    
    return df


def anomaly_events_analysis(df, anomaly_labels_attribute, object_id, object_key, connection, results):
    df_events_anomalies = get_outliers(df, anomaly_labels_attribute)

    results[object_id]["cycles_anomalies_nb"] = len(df_events_anomalies)
    results[object_id]["cycles_anomalies_mean"] = df_events_anomalies["cycle_duration"].mean()        
    results[object_id]["anomalies_events"] = {}
            
    events_dict = dict()
    anomalies_without_events = 0
    for index, anomaly in df_events_anomalies.iterrows():
        dist_events = udb.get_events_overlapping_timestamps_by_module_id(object_key, anomaly["first_endpoint"], anomaly["first_endpoint"] + anomaly["cycle_duration"], connection)
        if len(dist_events) == 0:
            anomalies_without_events += 1
        for  dist_event in dist_events:
            cost = ucalc.get_event_cost_on_cycle_from_overlapping_event(
                anomaly["first_endpoint"],
                anomaly["first_endpoint"] + anomaly["cycle_duration"],
                dist_event[1],
                dist_event[2]
            )
            if cost != 0 :        
                if dist_event[0] not in events_dict :
                    events_dict[dist_event[0]] = {"cost" : [], "cycles" : set() }
                events_dict[dist_event[0]]["cost"].append(cost)
                events_dict[dist_event[0]]["cycles"].add(index)
                
    results[object_id]["cycles_anomalies_without_event"] = anomalies_without_events
    for event in events_dict :
        results[object_id]["anomalies_events"][event] = {
             "events_nb" : len(events_dict[event]["cost"]),
             "cycles_nb" : len(events_dict[event]["cycles"]),
             "cost_mean" : mean(events_dict[event]["cost"]),
             "cost_sum"  : sum(events_dict[event]["cost"]),
             "cost_ratio" : sum(events_dict[event]["cost"])/df["cycle_duration"].sum() ,
             "cycles_nb_ratio" : len(events_dict[event]["cycles"])/results[object_id]["cycles_Nb"]
         }
        results[object_id]["anomalies_events"][event]["harmonic_mean_ratios"] = harmonic_mean(
             [results[object_id]["anomalies_events"][event]["cost_ratio"],
             results[object_id]["anomalies_events"][event]["cycles_nb_ratio"]]
         )
    return results
        