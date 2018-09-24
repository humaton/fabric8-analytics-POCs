# Python script to retrieve the latest release version information for python packages
# usage example: python3 pypi_release_monitor_all.py 

import requests
import sys
import json
from requests.exceptions import HTTPError, Timeout
from bs4 import BeautifulSoup

def main():
    try:
        # Use requests to issue a standard HTTP GET request
        url = "https://pypi.org/simple/" 
        result = requests.get(url)
        result.raise_for_status()
        printResults(result)
    except HTTPError as err:
        print("Error: {0}".format(err))
    

def printResults(resData):
     # Use the built-in JSON function to return parsed data
    verPack = []
    nopack = 0
    try:
        soup = BeautifulSoup(resData.text,"lxml")
        for link in soup.findAll('a'):
            nopack = nopack + 1
        print("No. of Packages:"+str(nopack))
        print("Processing Packages....")
        for link in soup.findAll('a'):
            try:
                # Use requests to issue a standard HTTP GET request
                url = "https://pypi.org/pypi/"+link.text+"/json"  
                result = requests.get(url, timeout=2)
                result.raise_for_status()
                dataobj = result.json()
                verPack.append("Package Name: "+link.text+", Latest Version: "+dataobj['info']['version'])
            except HTTPError as err:
                print("Error: {0}".format(err))
            except Timeout as err:
                print("Request timed out: {0}".format(err))      
            print(verPack)       
    except ValueError as err:
        print("Whoops, JSON Decoding error:"+ err)
    
    

if __name__ == "__main__":
    main()
