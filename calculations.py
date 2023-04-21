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

def main():
    pass


