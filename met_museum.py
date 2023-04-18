import sqlite3
import json
import os
import json
import requests
import random
import numpy as np
import matplotlib.pyplot as plt

def load_json(filename):
    try:
        source_dir = os.path.dirname(__file__)
        full_path = os.path.join(source_dir, filename)
        f = open(full_path, 'r')
        content = f.read()
        f.close()
        data = json.loads(content)
        return data
    except:
        data = {}
        return data

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def write_json(filename, dict):
    with open(filename, 'w') as f:
        json.dump(dict, f, indent=4)

def get_swapi_info(url, params=None):
    if params is not None:
        r = requests.get(url, params=params)
    else:
        r = requests.get(url)
    
    if r.status_code == 200:
        return r.json()
    else:
        print("Exception")
        return None
    
def cache_all_pages(artifact_url, filename):
    data = load_json(filename)

    count = 1
    artifacts = get_swapi_info(artifact_url)
    artifacts_ids = artifacts["objectIDs"]
    for i in range(100):
        index = random.randint(0,len(artifacts_ids) - 1)
        object_id = str(artifacts_ids[index])
        print (object_id)
        if object_id not in data.keys():
            response = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}")

            # Check if the request was successful
            if response.status_code == 200:
            # Save the response data to a JSON file
                data[str(count)] = response.json()
                write_json(filename, data)
        count += 1





def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = dir_path + '/' + "met.json"
    cache = load_json(filename)
    url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    cache_all_pages(url, "met_data.json")




if __name__ == "__main__":
    main()  
