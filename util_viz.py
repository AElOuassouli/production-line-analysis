import os
from pyvis.network import Network

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


import networkx as nx

#################### Production line graph #######################

def plot_prodcution_graph_networkx(yaml_dict, results, filename):
    graph = nx.DiGraph()
    
    pos_modules = dict()
    pos_artifact = dict()
    pos_buffer = dict()
    
    modules_node = []
    modules_size = []
    modules_colors = []

    no_data_nodes = []
    
    buffer_nodes = []
    artifct_nodes = []
    operator_nodes = []

    node_labels = dict()

    for obj in yaml_dict:
        if yaml_dict[obj]['type'] == 'module':
            graph.add_node(obj)
            pos_modules[obj] = (yaml_dict[obj]['position'][0], yaml_dict[obj]['position'][1])
            if not results[obj]["cycles_CYCLE_TIME"]:
                no_data_nodes.append(obj) 
            else :
                modules_size.append(results[obj]["cycles_CYCLE_TIME"])
                modules_colors.append(results[obj]["cycles_MTTF"] )
                modules_node.append(obj)
            node_labels[obj] = yaml_dict[obj]['display']
        elif yaml_dict[obj]['type'] == 'buffer':
            graph.add_node(obj)
            pos_buffer[obj] = (yaml_dict[obj]['position'][0], yaml_dict[obj]['position'][1])
            buffer_nodes.append(obj)
            node_labels[obj] = yaml_dict[obj]['display']
        elif yaml_dict[obj]['type'] == 'artifact':
            graph.add_node(obj)
            pos_artifact[obj] = (yaml_dict[obj]['position'][0], yaml_dict[obj]['position'][1])
            artifct_nodes.append(obj)
        #elif yaml_dict[obj]['type'] == 'operator':
        #    graph.add_node(obj)
        #    operator_nodes.append(obj)

    pos_merged = {**pos_modules, **pos_artifact, **pos_buffer}
    pos = nx.spring_layout(graph, pos= pos_merged, fixed= pos_merged.keys(), iterations=1 ) 

    for obj in yaml_dict:
        if yaml_dict[obj]["type"] != "operator": 
            if 'downstream' in yaml_dict[obj] and yaml_dict[obj]['downstream'] and yaml_dict[yaml_dict[obj]['downstream']]["type"] != "operator" :
                graph.add_edge(obj, yaml_dict[obj]['downstream'], color="black")
            if  'upstream' in yaml_dict[obj] and yaml_dict[obj]['upstream'] and yaml_dict[yaml_dict[obj]['upstream']]["type"] != "operator"  :
                graph.add_edge(yaml_dict[obj]['upstream'], obj, color="black")
   
    
    plt.figure(figsize=(20, 10))
    
    cmap = matplotlib.cm.get_cmap('Reds')

    nx.draw_networkx_edges(graph, pos)
    
    nc = nx.draw_networkx_nodes(graph, pos, 
                            nodelist=modules_node,
                            node_size=modules_size, 
                            node_color=modules_colors,
                            cmap= cmap,
                            node_shape="o",
                            label="Module (Node size = Cycle Time)")
    nc.set_norm(mcolors.LogNorm())
    cbar = plt.colorbar(nc, aspect=20, shrink=0.55)
    cbar.set_label("Mean Time To Fail (log scale)")

    nx.draw_networkx_nodes(graph, pos, 
                            nodelist=no_data_nodes,
                            node_size=30, 
                            node_color="black",
                            cmap= cmap,
                            node_shape="H",
                            label = "Module with no data")
    
    nx.draw_networkx_nodes(graph, pos, 
                            nodelist=buffer_nodes, 
                            node_color="blue",
                            node_size=25, 
                            node_shape="s",
                            label="Buffer")
    
    nx.draw_networkx_nodes(graph, pos, 
                            nodelist=artifct_nodes, 
                            node_color="green",
                            node_size=25,
                            alpha=0.4,  
                            node_shape="s",
                            label="Artifact")
    
    #nx.draw_networkx_nodes(graph, pos, 
    #                        nodelist=operator_nodes, 
    #                        node_color="black",
    #                        node_size=50,  
    #                        node_shape="*")
    
    nx.draw_networkx_labels(graph, pos, node_labels, 
                            font_size=8,
                            horizontalalignment= "right",
                            verticalalignment="bottom")
    
    
    legend = plt.legend()
    for item in legend.legendHandles:
        item._sizes = [40]
    
    plt.tight_layout()
    plt.savefig(filename)

    
        


def plot_production_line_pyvis(yaml_dict, results, filename):
    net = Network("800px", "1500px", directed = True)
    for obj in yaml_dict:
        if yaml_dict[obj]['type'] == 'module':
            title = ("Cycle Time: " + str(results[obj]["cycles_CYCLE_TIME"]) + "\r\n" +
                     "MTTF      : " + str(results[obj]["cycles_MTTF"]) + "\r\n" +
                     "MTTR      : " + str(results[obj]["cycles_MTTR"]))
            
            if obj == "LUGE":
                 net.add_node(obj, label=yaml_dict[obj]['display'], 
                 color="red", 
                 size= 3, 
                 title= title, 
                 x=yaml_dict[obj]['position'][0], 
                 y=yaml_dict[obj]['position'][1], 
                 physics=False)
            
            else:
                net.add_node(obj, 
                label=yaml_dict[obj]['display'], color="red", 
                value= results[obj]["cycles_CYCLE_TIME"],
                title= title,
                x=yaml_dict[obj]['position'][0], 
                y=yaml_dict[obj]['position'][1], 
                physics=False)

        elif yaml_dict[obj]['type'] == 'buffer':
            
            net.add_node(obj, 
            label=yaml_dict[obj]['display'], 
            color="green", 
            shape="square",
            size = 10, 
            x=yaml_dict[obj]['position'][0], 
            y=yaml_dict[obj]['position'][1], 
            physics=False)

        elif yaml_dict[obj]['type'] == 'artifact':
            
            net.add_node(obj, 
            title=yaml_dict[obj]['display'], 
            label= " ",
            color="blue", shape="square", 
            size=10,
            x=yaml_dict[obj]['position'][0], y=yaml_dict[obj]['position'][1],
            physics=False)

        elif yaml_dict[obj]['type'] == 'operator':
            net.add_node(obj, 
            label=yaml_dict[obj]['display'], 
            color="yellow", 
            shape="star", 
            physics=True)
    
    
    for obj in yaml_dict:
        if 'downstream' in yaml_dict[obj] and yaml_dict[obj]['downstream'] :
            net.add_edge(obj, yaml_dict[obj]['downstream'], color="black")
        if  'upstream' in yaml_dict[obj] and yaml_dict[obj]['upstream'] :
            net.add_edge(yaml_dict[obj]['upstream'], obj, color="black")

    net.show(filename)
    return


########### Misc plotting for testing and exploratory analysis #####

FIG_SIZE = 300

#https://jwalton.info/Embed-Publication-Matplotlib-Latex/
def set_size(width, fraction=1):
    """Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float
            Document textwidth or columnwidth in pts
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy

    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    # Width of figure (in pts)
    fig_width_pt = width * fraction

    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio

    fig_dim = (fig_width_in, fig_height_in)

    return fig_dim


def plotAnomalies(df, anomaly_attribute, object_id, tests_folder, ad_algorithm_name_and_hyper_parameters ):
    out = df.loc[df[anomaly_attribute] == -1, ['first_endpoint', 'cycle_duration']]
    inlier = df.loc[df[anomaly_attribute] != -1, ['first_endpoint', 'cycle_duration']]

    if object_id and tests_folder:
        plt.clf()
        plt.figure(figsize=set_size(FIG_SIZE))
        plt.scatter(inlier['first_endpoint'], inlier['cycle_duration'], color="blue", s=2 )
        plt.scatter(out['first_endpoint'], out['cycle_duration'], color="red", label="Anomaly", s=2)
        plt.xlabel('Timestamp')
        plt.ylabel('Cycle Duration')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(tests_folder, object_id, ad_algorithm_name_and_hyper_parameters + ".png"))

def plotAnomaliesLog(df, anomaly_attribute, object_id, tests_folder, ad_algorithm_name_and_hyper_parameters ):
    out = df.loc[df[anomaly_attribute] == -1, ['first_endpoint', 'cycle_duration']]
    inlinier = df.loc[df[anomaly_attribute] != -1, ['first_endpoint', 'cycle_duration']]

    if object_id and tests_folder:
        plt.clf()
        plt.figure(figsize=set_size(FIG_SIZE))
        plt.scatter(inlinier['first_endpoint'], inlinier['cycle_duration'], color="blue", s=2 )
        plt.scatter(out['first_endpoint'], out['cycle_duration'], color="red", label="Anomaly", s=2)
        plt.xlabel('Timestamp')
        plt.ylabel('Cycle Time')
        plt.yscale("log")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(tests_folder, object_id, ad_algorithm_name_and_hyper_parameters + "Log.png"))

def plotClusters(df, clusters_attribute, object_id, tests_folder, ad_algorithm_name_and_hyper_parameters ):
    groups = df.groupby(clusters_attribute)
    if object_id and tests_folder:
        plt.clf()
        for name, group in groups:
            if name == -1: 
                plt.scatter(group['first_endpoint'], group['cycle_duration'], s=2, label = "Anomaly")
            else:
                plt.scatter(group['first_endpoint'], group['cycle_duration'], s=2, label = name)
        plt.xlabel('Timestamp')
        plt.ylabel('Cycle Time')
        plt.yscale("log")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(tests_folder, object_id, ad_algorithm_name_and_hyper_parameters + "clusters.png"))

def plotHistogramCycleDuration(cycle_durations, object_id, tests_folder):
    plt.clf()
    plt.figure(figsize=set_size(FIG_SIZE))
    plt.hist(cycle_durations, len(cycle_durations.unique()))
    plt.xlabel('Cycle duration')
    plt.tight_layout()
    plt.savefig(os.path.join(tests_folder, object_id,  "histogram.png"))


def plotHistogramCycleDurationLog(cycle_durations, object_id, tests_folder):
    plt.clf()
    plt.figure(figsize=set_size(FIG_SIZE))
    plt.hist(cycle_durations, len(cycle_durations.unique()))
    plt.xlabel('Cycle duration')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(tests_folder, object_id,  "histogramLog.png"))



def plotCycleTimesOverTime(cycle_times, timestamps, object_id, tests_folder):
    plt.clf()
    plt.figure(figsize=set_size(FIG_SIZE))
    plt.scatter(timestamps, cycle_times, color="blue", s=2)
    plt.xlabel("Timestamp")
    plt.ylabel("Cycle duration")
    plt.tight_layout()
    plt.savefig(os.path.join(tests_folder, object_id,  "timeseries.png"))

def plotCycleTimesOverTimeLog(cycle_times, timestamps, object_id, tests_folder):
    plt.clf()
    plt.figure(figsize=set_size(FIG_SIZE))
    plt.scatter(timestamps, cycle_times, color="blue", s=2)
    plt.xlabel("Timestamp")
    plt.ylabel("Cycle duration")
    plt.yscale('log')
    plt.savefig(os.path.join(tests_folder, object_id,  "timeseriesLog.png"))



