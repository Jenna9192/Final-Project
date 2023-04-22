#import necessary tools and libraries 

import sqlite3
import json
import os
import json
import requests
import random
import numpy as np
import matplotlib.pyplot as plt

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def write_json(filename, dict):
    with open(filename, 'w') as f:
        json.dump(dict, f, indent=4)


def calc_mediums(db_name, cur, conn):
    cur.execute("SELECT met_mediums.medium, Harvard_mediums.medium\
                FROM met_mediums JOIN Harvard_mediums ON met_mediums.medium = Harvard_mediums.medium")
    common_mediums = cur.fetchall()
    medium_lst = []
    for medium in common_mediums:
        medium_lst.append(medium[0])

    cur.execute("SELECT met_mediums.medium FROM met_mediums ")
    met_mediums = cur.fetchall()
    for medium in met_mediums:
        current_medium = medium[0]
        if current_medium not in medium_lst:
            medium_lst.append(current_medium)
    
    cur.execute("SELECT Harvard_mediums.medium FROM Harvard_mediums")
    harvard_medium = cur.fetchall()
    for medium in harvard_medium:
        current_medium = medium[0]
        if current_medium not in medium_lst:
            medium_lst.append(current_medium)



    medium_dict = {}
    for medium in medium_lst:
        medium_dict[medium] = 0

    
    cur.execute("SELECT met_mediums.medium FROM met_mediums JOIN met_database ON met_mediums.id = met_database.medium_id")
    met_medium_each = cur.fetchall()
    for medium in met_medium_each:
        medium_dict[medium[0]] += 1


    cur.execute("SELECT Harvard_mediums.medium FROM Harvard_mediums JOIN Harvard_data ON Harvard_mediums.id = Harvard_data.Medium_id")
    met_medium_each = cur.fetchall()
    for medium in met_medium_each:
        medium_dict[medium[0]] += 1

    cur.execute("SELECT objType_id FROM selected_works")
    met_wiki_each = cur.fetchall()
    medium_dict["unspecified object"] = 0
    for num in met_wiki_each:
        if num == 2:
            medium_dict["Paintings"]+=1
        else:
            medium_dict["unspecified object"] += 1


    conn.commit()
    return(medium_dict)

def calc_period(db_name, cur, conn):
    cur.execute("SELECT met_periods.period, Harvard_periods.period\
                FROM met_periods JOIN Harvard_periods ON met_periods.period = Harvard_periods.period")
    common_periods = cur.fetchall()
    period_lst = []
    for period in common_periods:
        period_lst.append(period[0])

    cur.execute("SELECT met_periods.period FROM met_periods ")
    met_periods = cur.fetchall()
    for period in met_periods:
        current_period = period[0]
        if current_period not in period_lst:
            period_lst.append(current_period)
    
    cur.execute("SELECT Harvard_periods.period FROM Harvard_periods")
    harvard_period = cur.fetchall()
    print(harvard_period)
    for period in harvard_period[1:]:
        try:
            current_period = period[0]
        except:
            continue
        if current_period not in period_lst:
            period_lst.append(current_period)
    
    
    
    period_dict = {}

    
    for period in period_lst:
        period_dict[period] = 0

    

    
    cur.execute("SELECT met_periods.period FROM met_periods JOIN met_database ON met_periods.id = met_database.Period_id")
    met_period_each = cur.fetchall()
    for period in met_period_each:
            period_dict[period[0]] += 1
    

    cur.execute("SELECT Harvard_periods.period FROM Harvard_periods JOIN Harvard_data ON Harvard_periods.id = Harvard_data.Period_id")
    met_period_each = cur.fetchall()
    for period in met_period_each:
        if period[0] is not None:
            period_dict[period[0]] += 1

    conn.commit()
    return period_dict

def calc_culture(db_name, cur, conn):
    cur.execute("SELECT met_cultures.culture, Harvard_cultures.culture\
                FROM met_cultures JOIN Harvard_cultures ON met_cultures.culture = Harvard_cultures.culture")
    common_cultures = cur.fetchall()
    culture_lst = []
    for culture in common_cultures:
        culture_lst.append(culture[0])

    cur.execute("SELECT met_cultures.culture FROM met_cultures ")
    met_cultures = cur.fetchall()
    for culture in met_cultures:
        current_culture = culture[0]
        if current_culture not in culture_lst:
            culture_lst.append(current_culture)
    
    cur.execute("SELECT Harvard_cultures.culture FROM Harvard_cultures")
    harvard_culture = cur.fetchall()
    for culture in harvard_culture:
        try:
            current_culture = culture[0]
        except:
            continue
        if current_culture not in culture_lst:
            culture_lst.append(current_culture)

    culture_dict = {}
    for culture in culture_lst:
        culture_dict[culture] = 0

    
    cur.execute("SELECT met_cultures.culture FROM met_cultures JOIN met_database ON met_cultures.id = met_database.culture_id")
    met_culture_each = cur.fetchall()
    for culture in met_culture_each:
        culture_dict[culture[0]] += 1


    cur.execute("SELECT Harvard_cultures.culture FROM Harvard_cultures JOIN Harvard_data ON Harvard_Cultures.id = Harvard_data.Culture_id")
    met_culture_each = cur.fetchall()
    for culture in met_culture_each:
        culture_dict[culture[0]] += 1


    conn.commit()
    return culture_dict

def visual_medium(medium_dict):
    lst = []
    counts = []
    for k,v in medium_dict.items():
        if k == "N/A":
            continue
        lst.append(k)
        counts.append(v)
    
    #make visualization 
    plt.barh(lst,counts,align = 'center')
    plt.title("Number of artworks per medium") 
    plt.xlabel("Count per Medium") 
    plt.ylabel("Medium Name")
    plt.show()

def visual_culture(culture_dict):
    lst = []
    counts = []
    for k,v in culture_dict.items():
        if k == "N/A":
            continue
        lst.append(k)
        counts.append(v)
    
    #make visualization 
    plt.barh(lst,counts,align = 'center')
    plt.title("Number of artworks per culture")
    plt.xlabel("Count per culture")
    plt.ylabel("Culture name")
    plt.show()


def visual_period(period_dict):
    lst = []
    counts = []
    for k,v in period_dict.items():
        if k == "N/A":
            continue
        lst.append(k)
        counts.append(v)
    
    #make visualization 
    plt.barh(lst,counts,align = 'center')
    plt.title("Number of artworks per Period")
    plt.xlabel("Count per period")
    plt.ylabel("Period name")
    plt.show()

def main():
    cur, conn = open_database("all_database.db")
    calculation_data = {}
    calculation_data["medium_sum_data"] = calc_mediums("all_database.db", cur, conn)
    calculation_data["period_sum_data"] = calc_period("all_database.db", cur, conn)
    calculation_data["culture_sum_data"] = calc_culture("all_database.db", cur, conn)
    write_json("calculation_results.JSON", calculation_data)
    medium_dict = calc_mediums("all_database.db", cur, conn)
    visual_medium(medium_dict)
    culture_dict = calc_culture("all_database.db", cur, conn)
    visual_culture(culture_dict)

    period_dict = calc_period("all_database.db", cur, conn)
    visual_period(period_dict)

if __name__ == "__main__":
    main() 


