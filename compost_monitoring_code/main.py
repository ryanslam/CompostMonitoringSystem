import time
import urllib3
import csv
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

def writeToCSV(filename, data):
    with open(filename, "w+") as csvfile:
        writer = csv.writer(csvfile)
        now = time.strftime('%d-%m-%Y %H:%M:%S')
        writer.writerow([now, data])

def main():
    moistureOne = MoistureSensor(MCP.P0)
    moistureOne.calibrate()

    while (True):
        currentM1Val = moistureOne.mapSensorVals()
        if(checkConnection()):
            writeToCSV('/home/pi/Desktop/compost_monitoring_project/test.csv', currentM1Val)
        print("Current value", currentM1Val)
        time.sleep(5)

main()