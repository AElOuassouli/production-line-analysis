import yaml

YAML_FILE = "./graph.yaml"

def load_yaml_content_for_file(file = None ):
    if not file:
        file = YAML_FILE
    with open(file, 'r') as raw_yaml:
        return yaml.load(raw_yaml, Loader=yaml.FullLoader)
