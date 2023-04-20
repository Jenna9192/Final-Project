#Harvard Art Museums (museum_id = 2)
#collecting data on: period, culture, medium 
#visualize: most common period, and medium

#import necessary tools and libraries 
import sqlite3
import json
import os
import requests
import numpy as np
import matplotlib.pyplot as plt
import random

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
        data = {}
        return data

def write_json(filename, dict):
    with open(filename, 'w') as f:
        json.dump(dict, f, indent=4)

#function retrieves json from initial url
def get_api_info(url):
    
    params =  {"apikey": "68411e70-914a-4159-822a-02b918deadc9","size" : 100}
    resp = requests.get(url,params)

    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"Exception: cannot get api. Response code: {resp.status_code}, {resp.text}")
        return None
    

#retrieves individual pages from url
def cache_pages(url, filename):
    data = load_json(filename)
    count = 1
    #retrieve json that contains all objects 
    artworks = get_api_info(url)
    write_json("objects.json",artworks)
    artwork_ids = []
    for record in artworks["records"]:
       artwork_ids.append(record.get("id",None))
    print(artwork_ids)

    #make cache: each dictionary k,v is a seperate object
    for i in artwork_ids:
        obj_url = f"{url}/{i}"
        #print(obj_url)   
        obj_params = {"apikey": "68411e70-914a-4159-822a-02b918deadc9"}
        info = requests.get(obj_url, params = obj_params).json()
        data[str(count)] = info
        count+=1
        write_json(filename, data)
        


                 



    

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = dir_path + '/' + "test.json"
    cache = load_json(filename)
    url = "https://api.harvardartmuseums.org/object"
    #"https://api.harvardartmuseums.org/object?apikey=68411e70-914a-4159-822a-02b918deadc9"
  
    cache_pages(url,"test.json")
    
if __name__ == "__main__":
    main()  
