# Python script to retrieve the latest release version information for python packages
# usage example: python3 pypi_release_monitor.py aactivator

import requests
import sys
import json
from requests.exceptions import HTTPError, Timeout

def main():
    try:
        # Use requests to issue a standard HTTP GET request
        url = "https://pypi.org/pypi/"+sys.argv[1]+"/json"  
        result = requests.get(url, timeout=2)
        result.raise_for_status()
        printResults(result)
    except HTTPError as err:
        print("Error: {0}".format(err))
    except Timeout as err:
        print("Request timed out: {0}".format(err))
    

def printResults(resData):
     # Use the built-in JSON function to return parsed data
    try:
        dataobj = resData.json()
        print(dataobj['info']['version'])
    except ValueError as err:
        print("Whoops, JSON Decoding error:"+err)
    

if __name__ == "__main__":
    main()
