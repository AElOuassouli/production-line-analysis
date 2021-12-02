# production-line-analysis

## Environment 

You can create the environment used for this repository using the requirement.txt file. Please execute at the commande prompt: 

`conda create --name <env> --file requirements.txt --channel default --channel conda-forge`

Then, 

`conda activate <env>`

with `<env>` the name of your environement.

## Execution 

Before execution the code make sure that: 
* YAML data file is in the root folder and named **graph.yaml**
* The database file is in the root folder and name **sandbox.db**
* The plots folder exists in the root, named **plots** 

To run the code, please execute:
`python main.py`

Three files are generated: 
* **results.txt** containing calculation and anomaly analysis results
* **production_graph.html** a 2D visualization of the production graph using pyvis
* **production_graph.png** a 2D visualization of the production graph using Networkx 

## Files Description
* **main.py** contains the main code to be executed.
* **util_db.py** contains all functions related to database querying
* **util_yaml.py** contains all functions related to yaml manipulation
* **util_viz.py** contains all functions related to visualization
* **util_calculations.py** contains all functions used for computing metrics and other calculations
* **util_anomaly_detection.py** contains functions related to anomaly detection. 
