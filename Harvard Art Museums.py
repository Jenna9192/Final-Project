#Harvard Art Museums (museum_id = 2)
#collecting data on: object id, period, culture, medium, century


#import necessary tools and libraries 
import sqlite3
import json
import os
import requests
import numpy as np
import matplotlib.pyplot as plt
import random

#PART 1: RETRIEVE DATA FROM API
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
    

    #make cache: each dictionary k,v is a seperate object
    for i in artwork_ids:
        obj_url = f"{url}/{i}"
        obj_params = {"apikey": "68411e70-914a-4159-822a-02b918deadc9"}
        info = requests.get(obj_url, params = obj_params).json()
        data[str(count)] = info
        count+=1
        write_json(filename, data)

   
    

#PART 2: ADD DATA TO DB 
def create_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def create_museum_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Museums(id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
    table_dict = {1:"The Metropolitan Museum of Art", 2: "Harvard Art Museums"}
    for i in range(1,3):
        cur.execute("INSERT OR IGNORE INTO Museums(id,name) Values(?,?)", (i, table_dict[i]))
    conn.commit()

def create_medium_data(data,cur,conn):
    #table length 8
    mediums = []
    for artwork in data:
        if data[artwork]["classification"] not in mediums:
            mediums.append(data[artwork]["classification"])

    cur.execute("CREATE TABLE IF NOT EXISTS Harvard_mediums (id INTEGER PRIMARY KEY, medium TEXT UNIQUE)")
    for i in range(len(mediums)):
        cur.execute("INSERT OR IGNORE INTO Harvard_mediums(id, medium) VALUES (?,?)", (i+1,mediums[i]))
    conn.commit()


def create_culture_data(data,cur,conn):
    #table length 14
    cultures = []
    for artwork in data:
        if data[artwork]["culture"] not in cultures:
            cultures.append(data[artwork]["culture"])
    cur.execute("CREATE TABLE IF NOT EXISTS Harvard_cultures (id INTEGER PRIMARY KEY, culture TEXT UNIQUE)")
    for i in range(len(cultures)):
        cur.execute("INSERT OR IGNORE INTO Harvard_cultures(id, culture) VALUES (?,?)", (i+1,cultures[i]))
    conn.commit()

def create_period_data(data,cur,conn):
    #table length 8 
    periods = []
    for artwork in data:
        period = data[artwork]["period"]
        if period == None:
            period = "N/A"

        if period not in periods:
            periods.append(period)
    cur.execute("CREATE TABLE IF NOT EXISTS Harvard_periods (id INTEGER PRIMARY KEY, period TEXT UNIQUE)")
    for i in range(len(periods)):
        cur.execute("INSERT OR IGNORE INTO Harvard_periods(id, period) VALUES (?,?)", (i+1,periods[i]))
    conn.commit()



def create_century_data(data,cur,conn):
    centuries = []
    for artwork in data:
        cent = data[artwork]["century"]
        if cent == None:
            cent = "N/A"
        if cent not in centuries:
            centuries.append(cent)
    cur.execute("CREATE TABLE IF NOT EXISTS Harvard_centuries(id INTEGER PRIMARY KEY, century TEXT UNIQUE)")
    for i in range(len(centuries)):
        cur.execute("INSERT OR IGNORE INTO Harvard_centuries(id, century) VALUES (?,?)", (i+1, centuries[i]))
    conn.commit()




#make a table featuring id, museum id, object id, medium, culture, period, century, artist? - add later once debugged?
def create_harvard_full_data(data,cur,conn,index):
    cur.execute('CREATE TABLE IF NOT EXISTS Harvard_data(id INTEGER PRIMARY KEY, Museum_id INTEGER, Object_id INTEGER,\
                 Medium_id INTEGER, Culture_id INTEGER, Period_id INTEGER, Century_id INTEGER)')
    
    
    #find values to be entered in each field
    for i in range(25):
        #find object_id based on given index:
        index += 1 # NEW ADDED THIS HERE
        keys = list(data.keys())
        pos = index -1
        artwork = keys[pos]
        Object_id = int(data[artwork]["id"])
        
        
        #assign id 
        id = int(artwork)
        Museum_id = 2

        #find medium
        medium = data[artwork]["classification"]
        cur.execute('SELECT id FROM  Harvard_mediums WHERE medium = ?', (medium,))
        Medium_id = cur.fetchone()[0]

        #find culture
        culture = data[artwork]["culture"]
        cur.execute('SELECT id FROM  Harvard_cultures WHERE culture = ?', (culture,))
        Culture_id = cur.fetchone()[0]

        #find period 
        period = data[artwork]["period"]
        if period == None:
            period = "N/A"
        cur.execute('SELECT id FROM  Harvard_periods WHERE period = ?', (period,))
        Period_id = cur.fetchone()[0]

        #find century
        century = data[artwork]["century"]
        if century == None:
            century == "N/A"
        cur.execute('SELECT id FROM  Harvard_centuries WHERE century = ?', (century,))
        Century_id = cur.fetchone()[0]
    

        cur.execute('INSERT OR IGNORE INTO Harvard_data VALUES (?,?,?,?,?,?,?)', (id, Museum_id, Object_id, Medium_id, Culture_id, Period_id, Century_id))
        
    conn.commit()

    



def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = dir_path + '/' + "harvard.json"
    cache = load_json(filename)
    url = "https://api.harvardartmuseums.org/object"
    cache_pages(url,"harvard.json")
    data = load_json("harvard.json")
    cur,conn = create_database("all_database.db")
    
    #set up id tables 
    create_museum_table(cur, conn)
    create_medium_data(data,cur,conn)
    create_culture_data(data,cur,conn)
    create_period_data(data,cur,conn)
    create_century_data(data,cur,conn)

   
    #create full table:
    index = 0 
    #check for full data table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Harvard_data'")

    # if table doesn't exist create it; otherwise, add info to db
    if cur.fetchone() is None:
        create_harvard_full_data(data, cur, conn, index) 
    else:
        cur.execute("SELECT id FROM Harvard_data")
        ids = cur.fetchall()
        if len(ids) != 0:
            index = ids[-1][0]
        if (index == 100):
            cur.execute("DELETE FROM Harvard_data")
            index = 0
        create_harvard_full_data(data, cur, conn, index)






    
if __name__ == "__main__":
    main()  
