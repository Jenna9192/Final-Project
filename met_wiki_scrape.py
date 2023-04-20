from bs4 import BeautifulSoup
import requests
import re
import csv
import unittest

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
            image = info.get("href")

            # Format tuple to (title, artist, year, type, image)
            tup = (title, artist, year, obj_type, image)
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
            image = info.get("href")

            # Format tuple to (title, artist, year, type, image)
            tup = (obj_name, artist, year, obj_type, image)
            master.append(tup)
    
    return master

def create_csv(data, filename):
    
    # Create output file
    with open(filename, "w") as out_file:
        csv_out = csv.writer(out_file)
    
        # write in header
        header = ("Object Title",
                "Artist",
                "Year",
                "Object Type",
                "Image")
        csv_out.writerow(header)

        # write in data
        data.sort(key = lambda x: x[2])
        for listing in data:
            csv_out.writerow(listing)

def main():
    # Request content from MET wikipedia page
    url = "https://en.wikipedia.org/wiki/Metropolitan_Museum_of_Art"
    soup = make_request(url)

    # Create master list of all objects
    master_lst = []

    # Extract selected objects to add to master list
    select_objs = get_selected_objects(soup)
    master_lst.extend(select_objs)

    # Extract selected paintings to add to master list
    select_ptngs = get_selected_paintings(soup)
    master_lst.extend(select_ptngs)

    # Extract selected works from thumb images

    create_csv(master_lst, "wiki_selected_works.csv")

class TestAllMethods(unittest.TestCase):
    pass

if __name__ == "__main__":
    main()
