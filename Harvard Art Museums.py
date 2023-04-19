#Harvard Art Museums (museum_id = 1)
#collecting data on: period, culture, artist, artist gender, medium 

#import necessary tools and libraries 
import sqlite3
import json
import os
import json
import requests
import numpy as np
import matplotlib.pyplot as plt

def load_json(filename):
    try:
        source_dir = os.path.dirname(__file__)
        full_path = os.path.join(source_dir, filename)
        fn= open(full_path, 'r')
        content = fn.read()
        fn.close()
        data = json.loads(content)
        return data
    except:
        data = []
        return data


def get_api_info(url, params = None):
    response = requests.get(url)
    
