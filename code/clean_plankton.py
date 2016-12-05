#! /usr/bin/python

import requests
import json
import csv

def parse_data(csvFile):
    clean_data = []
    csvDic = csv.DictReader(open(csvFile))
    for row in csvDic:
        units = row['Units']
        new_units = None
        is_digit = row['Result Value as Number'].isdigit()
        if units == '#/l' and is_digit:
            new_units = float(row['Result Value as Number']) * 1000
        elif units == '#/ml' and is_digit:
            new_units = float(row['Result Value as Number']) * 1000000
        elif units == '#/m3' and is_digit:
            new_units = float(row['Result Value as Number'])
        
        if new_units != None:
            new_date = row['Activity Start'].split(" ")
            clean_data.append([row['Station Latitude'],row['Station Longitude'],new_date[0],row['Subject Taxon'],new_units])
    return clean_data


def save_data(data,csvFile):
    with open(csvFile, "w",newline='') as f:
        writer = csv.writer(f,delimiter=',')
        writer.writerows(data)

# Main method
def main() :
    save_data(parse_data('../data/plankton.csv'),'../data/clean_plankton.csv')
    

if __name__ == "__main__" : main()