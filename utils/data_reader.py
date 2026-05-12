import json
import os

def load_test_data(filename="test_data.json"):
    """Loads JSON data from the data directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "..", "data", filename)
    
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)
