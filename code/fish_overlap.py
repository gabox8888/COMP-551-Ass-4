#! /usr/bin/python

import requests
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import datetime
import numpy
import csv

def parse_data_epa(csvFile):
    csvDic = csv.DictReader(open(csvFile))
    maxT = (datetime.datetime(2017,1,1)-datetime.datetime(1990,1,1)).total_seconds()
    fishDictionary = {}
    for row in csvDic:
        # if row['Activity Medium'] == 'Biological':
        date = datetime.datetime.strptime(row['Activity Start'], "%m/%d/%Y %H:%M")
        since = (date-datetime.datetime(1990,1,1)).total_seconds()
        since /= maxT
        if row['Subject Taxon'] in fishDictionary:
            fishDictionary[row['Subject Taxon']][0].append(float(row['Station Latitude']))
            fishDictionary[row['Subject Taxon']][1].append(float(row['Station Longitude']))
            fishDictionary[row['Subject Taxon']][2].append(since)
        else:
            fishDictionary[row['Subject Taxon']] = [[float(row['Station Latitude'])],[float(row['Station Longitude'])],[since]]
    return fishDictionary

def discard_data(fishDictionary):
    copy = dict(fishDictionary)
    for i in fishDictionary:
        if len(fishDictionary[i][0]) < 1000:
            del copy[i]
    return copy

def parse_data_carp(csvFile):
    csvDic = csv.DictReader(open(csvFile))
    carpList = [[],[]]
    for row in csvDic:
        carpList[0].append(float(row['decimalLongitude']))
        carpList[1].append(float(row['decimalLatitude']))
    return carpList

def parse_data_new(csvFile):
    csvDic = csv.DictReader(open(csvFile))
    carpList = [[],[]]
    for row in csvDic:
        carpList[0].append(float(row['POINT_X']))
        carpList[1].append(float(row['POINT_Y']))
    return carpList

def parse_data_more_carp(csvFile):
    csvDic = csv.DictReader(open(csvFile))
    carpList = [[],[]]
    for row in csvDic:
        carpList[0].append(float(row['POINT_X']))
        carpList[1].append(float(row['POINT_Y']))
    return carpList

def plot_points(fishDictionary,silver,grass,bighead):
    plt.scatter(silver[0], silver[1], s=100, c=(0,0,0))
    plt.scatter(grass[0], grass[1], s=100, c=(0,0,0))
    plt.scatter(bighead[0], bighead[1], s=100, c=(0,0,0))
    for i in fishDictionary:
        # plt.scatter(fishDictionary[i][0], fishDictionary[i][1], s=80, c=numpy.random.rand(3,1))
        if "Hypophthalmichthys" in i :
           plt.scatter(fishDictionary[i][0], fishDictionary[i][1], s=300, c=(0,0,0))
        else:
            plt.scatter(fishDictionary[i][0], fishDictionary[i][1], s=80 , c=(1,0,1))
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # for i in fishDictionary:
    #     # plt.scatter(fishDictionary[i][0], fishDictionary[i][1], s=80, c=numpy.random.rand(3,1))
    #     if "Hypophthalmichthys" in i :
    #         ax.scatter(fishDictionary[i][0], fishDictionary[i][1],fishDictionary[i][2], c=(0,0,0))
    #     else:
    #         ax.scatter(fishDictionary[i][0], fishDictionary[i][1], fishDictionary[i][2], c=(1,0,1))
    

    plt.show()

def plot_points_new(more_carp,absence,silver,grass,bighead):
    plt.scatter(silver[0], silver[1], s=100, c=(1,0,0))
    plt.scatter(grass[0], grass[1], s=100, c=(0,1,0))
    plt.scatter(bighead[0], bighead[1], s=100, c=(0,0,1))
    plt.scatter(more_carp[0], more_carp[1], s=100, c=(1,0,1))
    plt.scatter(absence[0], absence[1], s=100, c=(0,0,0))
    plt.show()



def save_data(data,csvFile):
    with open(csvFile, "w",newline='') as f:
        writer = csv.writer(f,delimiter=',')
        writer.writerows(data)

# Main method
def main() :
    silver = parse_data_carp('../data/Silver-Carp2.csv')
    grass = parse_data_carp('../data/Grass-Carp2.csv')
    bighead = parse_data_carp('../data/Bighead-Carp2.csv')
    # plot_points(parse_data_epa('../data/raw_fish_epa.csv'),silver,grass,bighead)

    carp = parse_data_new('../data/other-carp.csv')
    absence = parse_data_new('../data/absence-points.csv')

    plot_points_new(carp,absence,silver,grass,bighead)
    

if __name__ == "__main__" : main()