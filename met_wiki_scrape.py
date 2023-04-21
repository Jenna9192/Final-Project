from bs4 import BeautifulSoup
import sqlite3
import requests
import os
import re
import csv

def make_request(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    
    except:
        print(f"ERROR: {res.status_code}")
        return None
    
def get_selected_objects(soup):
    master = []
    
    tags = soup.find_all("div", class_="mod-gallery mod-gallery-default mod-gallery-center")

    # Parses through selected objects:
    for tag in tags[:2]:
        captions = tag.find_all("div", class_="thumb")

        for caption in captions:

            info = caption.find("a")
            info_t = info.get("title").strip()

            # Find pattern for title
            pattern_ttl = "^[^\d,.()]+"
            match_ttl = re.search(pattern_ttl, info_t)

            if match_ttl:
                title = match_ttl[0]
            else:
                title = "NaN"

            # Find pattern for year
            pattern_yr = ["\d+s*[^.,)]{0,4}\d*[^,.)]* (century|cen\.|c\.|BCE|)", 
                          "\d{3,4}s*"]
            match_yr1 = re.search(pattern_yr[0], info_t)
            match_yr2 = re.search(pattern_yr[1], info_t)
            
            if match_yr1:
                year = match_yr1[0]
            
            elif match_yr2:
                year = match_yr2[0]

            else:
                year = "NaN"
            
            artist = "NaN"
            obj_type = "object"
            museum_Id = 1
            image = info.get("href")

            # Format tuple to (title, museum_Id, artist, year, type, image)
            tup = [title, museum_Id, artist, year, obj_type, image]
            master.append(tup)
            
    return master

def get_selected_paintings(soup):
    master = []
    
    tags = soup.find_all("div", class_="mod-gallery mod-gallery-default mod-gallery-center")

    # Parses through selected paintings:
    for tag in tags[2:]:
        captions = tag.find_all("div", class_="thumb")
        
        for caption in captions:

            info = caption.find("a")
            info_t = info.get("title")

            # Find pattern for artist, title, and year
            pattern = "([^,]+),\s(.+),\s\D*(\d+.\d+)(,.+)*"
            match = re.search(pattern, info_t)

            if match:
                artist = match.group(1)
                obj_name = match.group(2)
                year = match.group(3)

            else:   
                obj_name = "NaN"
                artist = "NaN"
                year = "NaN"

            obj_type = "paintings"
            museum_Id = 1
            image = info.get("href")

            # Format tuple to (title, museum id, artist, year, type, image)
            tup = [obj_name, museum_Id, artist, year, obj_type, image]
            master.append(tup)
    
    return master

def get_citations(soup):
    master = []
    
    tag = soup.find_all("div", class_="reflist")
    references = tag[1].find_all("span", class_="reference-text")

    for reference in references:
        
        # Find pattern for title and source
        pattern = '("[^"]+")(?:\.\s)*(www\.\w+\.\w+|([^\.,\d]+))'
        match = re.search(pattern, reference.text)

        if match:
            title = match.group(1)
            source = match.group(2)
        
        else:
            title = "NaN"
            source = "NaN"
        
        # Find pattern for date
        pattern_dt = ["([A-Z][a-z]+ \d+, \d{4})", "(?:\s|\()(\d{4})(?:\)|)"]
        match_dt1 = re.search(pattern_dt[0], reference.text)
        match_dt2 = re.search(pattern_dt[1], reference.text)

        if match_dt1:
            date = match_dt1[0]

        elif match_dt2:
            date = match_dt2.group(1)
        
        else:
            "NaN"
        
        ref_link = reference.find("a")
        try:
            link = ref_link.get("href")
        except:
            link = "NaN"
        
        # Format tuple to (title, source, date, link)
        tup = [title, source, date, link]
        master.append(tup)

    return master

    # (website title, source, date, link)

def create_csv(data, heading, filename):
    
    # Create output file
    with open(filename, "w") as out_file:
        csv_out = csv.writer(out_file)
    
        # write in header
        heading.insert(0, "Index")
        csv_out.writerow(heading)

        # write in data
        data.sort(key = lambda x: x[2])
        for i in range(len(data)):
            data[i].insert(0, i+1)
            csv_out.writerow(data[i])

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

def create_data(file, cur, conn):
    table_query = "CREATE TABLE IF NOT EXISTS selected_works (id INTEGER PRIMARY KEY, title TEXT, museum_Id INTEGER, artist TEXT, year TEXT, obj_Type TEXT, image TEXT)"
    cur.execute(table_query)
    
    with open(file, "r") as f:
        reader = csv.reader(f)
        next(reader)
        
        for row in reader:
            insert_query = "INSERT INTO selected_works (id, title, museum_Id, artist, year, obj_Type, image) VALUES (?, ?, ?, ?, ? ,?, ?)"
            cur.execute(insert_query, row)
        
    conn.commit()
    conn.close()

def main():
    # Request content from MET wikipedia page
    url = "https://en.wikipedia.org/wiki/Metropolitan_Museum_of_Art"
    soup = make_request(url)

    # Create master list of all objects
    master_lst = []
    select_works_header = ["Object Title",
                           "Museum_Id",
                           "Artist",
                           "Year",
                           "Object Type",
                           "Image"]

    # Extract selected objects to add to master list
    select_objs = get_selected_objects(soup)
    master_lst.extend(select_objs)

    # Extract selected paintings to add to master list
    select_ptngs = get_selected_paintings(soup)
    master_lst.extend(select_ptngs)

    # Create csv from selected works
    create_csv(master_lst, select_works_header, "wiki_selected_works.csv")

    # Extract citations and create csv from data
    citations = get_citations(soup)
    citations_header = ["Title",
                        "Website",
                        "Date",
                        "Link"]
    create_csv(citations, citations_header, "wiki_citations.csv")

    # Add wiki_selected_works.csv data to database
    index = 0
    cur, conn = setUpDatabase("all_database.db")
    #check if the database exist
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='selected_works'")
    #if does not exist
    if cur.fetchone() is None:
        create_data("wiki_selected_works.csv", cur, conn) 
    else:
        cur.execute("SELECT id FROM selected_works")
        id = cur.fetchall()
        if len(id) != 0:
            index = id[-1][0]
        if (index == 65):
            cur.execute("DELETE FROM selected_works")
            index = 0
        create_data("wiki_selected_works.csv", cur, conn) 


if __name__ == "__main__":
    main()
