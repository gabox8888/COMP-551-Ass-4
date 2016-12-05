#! /usr/bin/python

import requests
import json
import csv

# species,huc8,day,month,year,lat,long,status

# Main method
def main() :
    csvArr = []
    params = {'species':'melanostomus','limit' : 100, 'offset': 0}
    complete = 0
    while complete == 0:
        req = requests.get("https://nas.er.usgs.gov/api/v1/occurrence/search",params=params)
        reqJSON = json.loads(req.content.decode("utf-8"))
        if reqJSON['count'] == 0: break
        results = reqJSON['results']
        for i in results:
            temp = []
            temp.append(i['species'])
            temp.append(i['huc8'])
            temp.append(i['day'])
            temp.append(i['month'])
            temp.append(i['year'])
            temp.append(i['decimalLatitude'])
            temp.append(i['decimalLongitude'])
            temp.append(i['status'])
            csvArr.append(temp)
        params['offset'] += 100
    print(csvArr)
    with open("../data/gobby_data.csv", "w",newline='') as f:
        writer = csv.writer(f,delimiter=',')
        writer.writerows(csvArr)

if __name__ == "__main__" : main()