import time
from datetime import datetime as dt
import urllib3
import json
from pickleshare import *
import adafruit_mcp3xxx.mcp3008 as MCP
from moistureSensor import MoistureSensor

# Checks to see if there is internet connectivity.
def checkConnection(host='https://google.com'):
    http = urllib3.PoolManager()
    try:                                            # Try to connect to google.
        r = http.request('GET', host)        
        return True
    except urllib2.URLError as e:                   # Cetch error if no internet connectivity.
        print(e)
        return False

# Stores the data locally to push into graphite.
def storeLocally(db, data):
    db['data'] = data
    print(db['data'])


def main():
    moistureOne = MoistureSensor(MCP.P0)            # Assigns moisture sensors to pin 0 of analog converter.
    # Calibrates the sensors
    moistureOne.calibrate()
    db = PickleShareDB('./CompostMonitoringData')
    print("Should be empty:", db.items())

    while (True):
        currentM1Val = moistureOne.mapSensorVals()
        dt_string = dt.now().strftime("%d/%m/%Y %H:%M:%S")

        # Loads the json from the database.
        if 'data' not in db.keys():
            db['data'] = []
        
        # Stores existing data from pickleShare db into existing_data.
        existing_data = db['data']

        # Creates a dict of the current vals.
        curr_data = {
            'moisture_value': currentM1Val,
            'time': dt_string
        }

        # Appends the new data.
        existing_data.append(curr_data)

        if(checkConnection()):
            # db.clear()
            pass

        storeLocally(db, existing_data)

        # Prints the current values
        print("Current value", currentM1Val, '\n\tCurrent Time:', dt_string)
        time.sleep(5)

main()