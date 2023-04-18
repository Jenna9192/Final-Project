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

def get_api_info(url, params=None):
    if params is not None:
        r = requests.get(url, params=params)
    else:
        r = requests.get(url)
    
    if r.status_code == 200:
        return r.json()
    else:
        print("Exception- cannot get json")
        return None
    
def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def write_json(filename, dict):
    with open(filename, 'w') as f:
        json.dump(dict, f, indent=4)


    
def cache_all_pages(people_url, filename):
    data = load_json(filename)
    
    for i in range(1,10):
        page_number = "page " + str(i)
        if page_number not in data.keys():
            data_lst = get_api_info(people_url, params={"page": i})
            data[page_number] = data_lst["results"]
    
    write_json(filename, data)





def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = dir_path + '/' + "met.json"
    cache = load_json(filename)
    #url =

if __name__ == "__main__":
    main()  
