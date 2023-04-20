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
    cur.execute("DROP TABLE IF EXISTS met_periods")
    periods = ["N/A"]
    for art in data:
        period = data[art]["period"]
        if (len(period)== 0):
            continue
        if "," in period:
            period = period.split(",")
            for word in period:
                word.lstrip()
        if "/" in period:
            period = period.split("/")
            for word in period:
                word.lstrip()
        if type(period) == list:
            for word in period:
                if word not in periods:
                    periods.append(word)
        elif period not in periods:
            periods.append(period)
    cur.execute("CREATE TABLE IF NOT EXISTS met_periods (id INTEGER PRIMARY KEY, period TEXT UNIQUE)")
    for i in range(0,len(periods)):
        cur.execute("INSERT OR IGNORE INTO met_periods (id, period) VALUES (?,?)",(i, periods[i]))
    conn.commit()

def make_medium_data(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS met_mediums")
    mediums = []
    for art in data:
        medium = data[art]["classification"]
        if (len(medium)== 0):
            medium = data[art]["medium"]
            if (len(medium) == 0) or medium == "[no medium available]":
                medium = 'N/A'
        book = ["Books", "Codices"]
        for spelling in book:
            if spelling in medium:
                medium = "Books"
        photography = ["Negatives", "Photographs"]
        for spelling in photography:
            if spelling in medium:
                medium = "Photographs"
        ceramic = ["Ceramics", "Ceramic", "ceramic", "ceramics", "Faience", "terracottas"]
        for spelling in ceramic:
            if spelling in medium:
                medium = "Ceramics"
        paper = ["Paper", "paper"]
        for spelling in paper:
            if spelling in medium:
                medium = "Paper"
        glass = ["glass", "Glass"]
        metalwork = ["Metalwork", "copper", "gold", "Krisses"]
        for spelling in metalwork:
            if spelling in medium:
                medium = "Metalwork"
        for spelling in glass:
            if spelling in medium:
                medium = "Glass"
        vase = ["Vase", "Vases", "vase", "vases"]
        for spelling in vase:
            if spelling in medium:
                medium = "Vases"
        if medium.startswith("Textiles"):
            medium = "Textiles"
        Textiles = ["Linen", "linen", "leather", "Wool", "Cotton"]
        for spelling in Textiles:
            if spelling in medium:
                medium = "Textiles"
        if medium.startswith("Wood"):
            medium = "Wood"
        if medium.endswith("Ornaments"):
            medium = "Ornaments"
        ivory = ["Ivory", "Ivories", "ivory", "ivories"]
        for spelling in ivory:
            if spelling in medium:
                medium = "Ivory"
        if medium not in mediums:
            mediums.append(medium)
    cur.execute("CREATE TABLE IF NOT EXISTS met_mediums (id INTEGER PRIMARY KEY, medium TEXT UNIQUE)")
    for i in range(0,len(mediums)):
        cur.execute("INSERT OR IGNORE INTO met_mediums (id, medium) VALUES (?,?)",(i, mediums[i]))
    conn.commit()

def make_culture_data(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS met_cultures")
    cultures = []
    for art in data:
        culture= data[art]["culture"]
        if (len(culture)== 0 or culture.startswith('Unknown')):
            culture = 'N/A'
        if culture not in cultures:
            cultures.append(culture)
    cur.execute("CREATE TABLE IF NOT EXISTS met_cultures (id INTEGER PRIMARY KEY, culture TEXT UNIQUE)")
    for i in range(0,len(cultures)):
        cur.execute("INSERT OR IGNORE INTO met_cultures (id, culture) VALUES (?,?)",(i, cultures[i]))
    conn.commit()

def make_location_data(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS met_location")
    locations = []
    for art in data:
        location = data[art]["region"]
        if (len(location)== 0):
            location = data[art]["subregion"]
            if (len(location)== 0):
                location = data[art]["country"]
                if (len(location)== 0):
                    location = data[art]["county"]
                    if (len(location)== 0):
                        location = data[art]["state"]
                        if (len(location)== 0):
                            location = data[art]["city"]
                            if (len(location)== 0):
                                location = 'N/A'
        word = "Iran"
        if word in str(location):
            location = word
        if location not in locations:
            locations.append(location)
    cur.execute("CREATE TABLE IF NOT EXISTS met_locations (id INTEGER PRIMARY KEY, location TEXT UNIQUE)")
    for i in range(0,len(locations)):
        cur.execute("INSERT OR IGNORE INTO met_locations (id, location) VALUES (?,?)",(i, locations[i]))
    conn.commit()


def make_met_data(data, cur, conn, index):
    cur.execute("CREATE TABLE IF NOT EXISTS met_database (id INTEGER PRIMARY KEY, Museum_id INTEGER, object_id INTEGER, title TEXT, artist TEXT, year INTEGER, medium_id INTEGER, culture_id INTEGER, location_id INTEGER, Period_id INTEGER)")
    for i in range(25):
        index += 1
        art = list(data.keys())
        place = index - 1
        art = art[place]
        museum_id = 1
        object_id = data[art]["objectID"]
        title = data[art]["title"]
        artist = data[art]["artistDisplayName"]
        if len(artist) == 0:
            artist = "N/A"
        year = data[art]["objectEndDate"]

        #identify medium
        cur.execute("SELECT medium, id FROM met_mediums")
        medium_dict = dict(cur.fetchall())

        medium = data[art]["classification"]
        if (len(medium)== 0):
            medium = data[art]["medium"]
            if (len(medium) == 0) or medium == "[no medium available]":
                medium = 'N/A'
        book = ["Books", "Codices"]
        for spelling in book:
            if spelling in medium:
                medium = "Books"
        photography = ["Negatives", "Photographs"]
        for spelling in photography:
            if spelling in medium:
                medium = "Photographs"
        ceramic = ["Ceramics", "Ceramic", "ceramic", "ceramics", "Faience", "terracottas"]
        for spelling in ceramic:
            if spelling in medium:
                medium = "Ceramics"
        paper = ["Paper", "paper"]
        for spelling in paper:
            if spelling in medium:
                medium = "Paper"
        glass = ["glass", "Glass"]
        metalwork = ["Metalwork", "copper", "gold", "Krisses"]
        for spelling in metalwork:
            if spelling in medium:
                medium = "Metalwork"
        for spelling in glass:
            if spelling in medium:
                medium = "Glass"
        vase = ["Vase", "Vases", "vase", "vases"]
        for spelling in vase:
            if spelling in medium:
                medium = "Vases"
        if medium.startswith("Textiles"):
            medium = "Textiles"
        Textiles = ["Linen", "linen", "leather", "Wool", "Cotton"]
        for spelling in Textiles:
            if spelling in medium:
                medium = "Textiles"
        if medium.startswith("Wood"):
            medium = "Wood"
        if medium.endswith("Ornaments"):
            medium = "Ornaments"
        ivory = ["Ivory", "Ivories", "ivory", "ivories"]
        for spelling in ivory:
            if spelling in medium:
                medium = "Ivory"
        medium_id = medium_dict[medium]
        
        #identifying culture
        cur.execute("SELECT culture, id FROM met_cultures")
        culture_dict = dict(cur.fetchall())
        culture= data[art]["culture"]
        if (len(culture)== 0 or culture.startswith('Unknown')):
            culture = 'N/A'
        culture_id = culture_dict[culture]
        
        #identify location
        cur.execute("SELECT location, id FROM met_locations")
        location_dict = dict(cur.fetchall())
        location = data[art]["region"]
        if (len(location)== 0):
            location = data[art]["subregion"]
            if (len(location)== 0):
                location = data[art]["country"]
                if (len(location)== 0):
                    location = data[art]["county"]
                    if (len(location)== 0):
                        location = data[art]["state"]
                        if (len(location)== 0):
                            location = data[art]["city"]
                            if (len(location)== 0):
                                location = 'N/A'
        word = "Iran"
        if word in str(location):
            location = word
        location_id = location_dict[location]
        
        #identify period
        cur.execute("SELECT period, id FROM met_periods")
        period_dict = dict(cur.fetchall())
        period = data[art]["period"]
        if (len(period)== 0):
            period = "N/A"
        elif "," in period:
            period = period.split(",")
            for word in period:
                word.lstrip()
        elif "/" in period:
            period = period.split("/")
            for word in period:
                word.lstrip()

        if type(period) == list:
            period_id = []
            for per in period:
                period_id = period_dict[per]
        else:
            period_id = period_dict[period]

        art = int(art)
        museum_id = int(museum_id)
        object_id = int(object_id)
        title = str(title)
        artist = str(artist)
        year = int(year)
        medium_id = int(medium_id)
        culture_id = int(culture_id)
        location_id = int(location_id)
        period_id = int(period_id)
        
        cur.execute("INSERT OR IGNORE INTO met_database (id, Museum_id, object_id, title, artist, year, medium_id, culture_id, location_id, period_id) VALUES (?,?,?,?,?,?,?,?,?,?)",(art, museum_id, object_id, title, artist, year, medium_id, culture_id, location_id, period_id))
        


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
    make_location_data(data, cur1, conn1)
    index = 0
    #check if the database exist
    cur1.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='met_database'")
    #if does not exist
    if cur1.fetchone() is None:
        make_met_data(data, cur1, conn1, index) 
    else:
        cur1.execute("SELECT id FROM met_database")
        id = cur1.fetchall()
        if len(id) != 0:
            index = id[-1][0]
        if (index == 100):
            cur1.execute("DROP TABLE IF EXISTS met_database")
            index = 0
        make_met_data(data, cur1, conn1, index)
    #make_met_data(data,cur1, conn1, index)

if __name__ == "__main__":
    main()  
