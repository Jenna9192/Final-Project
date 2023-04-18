import unittest
import sqlite3
import json
import os
import json
import requests
import numpy as np
import matplotlib.pyplot as plt

def load_json(filename):
    '''
    Loads a JSON cache from filename if it exists

    Parameters
    ----------
    filename: string
        the name of the cache file to read in

    Returns
    -------
    dict
        if the cache exists, a dict with loaded data
        if the cache does not exist, an empty dict
    '''
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

def make_positions_table(data, cur, conn):
    positions = []
    for player in data['squad']:
        position = player['position']
        if position not in positions:
            positions.append(position)
    cur.execute("CREATE TABLE IF NOT EXISTS Positions (id INTEGER PRIMARY KEY, position TEXT UNIQUE)")
    for i in range(len(positions)):
        cur.execute("INSERT OR IGNORE INTO Positions (id, position) VALUES (?,?)",(i, positions[i]))
    conn.commit()


def write_json(filename, dict):
    '''
    Encodes dict into JSON format and writes
    the JSON to filename to save the search results

    Parameters
    ----------
    filename: string
        the name of the file to write a cache to
    
    dict: cache dictionary

    Returns
    -------
    None
        does not return anything
    '''  

    with open(filename, 'w') as f:
        json.dump(dict, f, indent=4)

def get_swapi_info(url, params=None):
    '''
    Check whether the 'params' dictionary has been specified. Makes a request to access data with 
    the 'url' and 'params' given, if any. If the request is successful, return a dictionary representation 
    of the decoded JSON. If the search is unsuccessful, print out "Exception!" and return None.

    Parameters
    ----------
    url (str): a url that provides information about entities in the Star Wars universe.
    params (dict): optional dictionary of querystring arguments (default value is 'None').
        

    Returns
    -------
    dict: dictionary representation of the decoded JSON.
    '''
    if params is not None:
        r = requests.get(url, params=params)
    else:
        r = requests.get(url)
    
    if r.status_code == 200:
        return r.json()
    else:
        print("Exception")
        return None


def get_info(url)：
    https://collectionapi.metmuseum.org/public/collection/v1/objects/[objectID] 


class TestHomework6(unittest.TestCase):
    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.filename = dir_path + '/' + "swapi_people.json"
        self.cache = load_json(self.filename)
        self.url = "https://swapi.dev/api/people"

if __name__ == "__main__":
    unittest.main(verbosity=2)    
