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
        if str(count) not in data.keys():
            response = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}")

            # Check if the request was successful
            if response.status_code == 200:
            # Save the response data to a JSON file
                data[str(count)] = response.json()
                write_json(filename, data)
        count += 1

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def make_period_data(data, cur, conn):
    periods = []
    for art in data:
        period = data[art]["period"]
        if (len(period)== 0):
            period = 'N/A'
        if period not in periods:
            periods.append(period)
    cur.execute("CREATE TABLE IF NOT EXISTS met_periods (id INTEGER PRIMARY KEY, period TEXT UNIQUE)")
    for i in range(0,len(periods)):
        cur.execute("INSERT OR IGNORE INTO met_periods (id, period) VALUES (?,?)",(i, periods[i]))
    conn.commit()

def make_medium_data(data, cur, conn):
    count = 0
    mediums = []
    for art in data:
        medium = data[art]["classification"]
        if (len(medium)== 0):
            medium = data[art]["medium"]
            if (len(medium) == 0) or medium == "[no medium available]":
                medium = 'N/A'
        if medium not in mediums:
            mediums.append(medium)
    cur.execute("CREATE TABLE IF NOT EXISTS met_mediums (id INTEGER PRIMARY KEY, medium TEXT UNIQUE)")
    for i in range(0,len(mediums)):
        cur.execute("INSERT OR IGNORE INTO met_mediums (id, medium) VALUES (?,?)",(i, mediums[i]))
    conn.commit()

def make_culture_data(data, cur, conn):
    cultures = []
    for art in data:
        culture= data[art]["culture"]
        if (len(culture)== 0) :
            culture = 'N/A'
        if culture not in cultures:
            cultures.append(culture)
    cur.execute("CREATE TABLE IF NOT EXISTS met_cultures (id INTEGER PRIMARY KEY, culture TEXT UNIQUE)")
    for i in range(0,len(cultures)):
        cur.execute("INSERT OR IGNORE INTO met_cultures (id, culture) VALUES (?,?)",(i, cultures[i]))
    conn.commit()


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = dir_path + '/' + "met.json"
    cache = load_json(filename)
    url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    cache_all_pages(url, "met_data.json")
    data = load_json("met_data.json")
    cur1, conn1 = setUpDatabase("met_database.db")
    make_period_data(data, cur1, conn1)
    make_medium_data(data, cur1, conn1)
    make_culture_data(data, cur1, conn1)


if __name__ == "__main__":
    main()  
