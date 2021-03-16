# Import all the necessary libraries
from time import *
from datetime import datetime as dt
from pickleshare import *
import adafruit_mcp3xxx.mcp3008 as MCP
from multiprocessing import Process
import shutil
import os
import urllib3
import json

# Locally imported files.
from moistureSensor import MoistureSensor
from TemperatureSensor import TemperatureSensor
import lcddriver
 

# Checks to see if there is internet connectivity.
def check_connection(host='https://google.com'):
    http = urllib3.PoolManager()
    try:                                            # Try to connect to google.
        r = http.request('GET', host)
        return True
    except urllib2.URLError as e:                   # Cetch error if no internet connectivity.
        print(e)
        return False

# Stores data locally.
def store_locally(db, data):
    db['data'] = data
    print(db['data'])

# Saves data to removable drive.
def store_to_removable(src, destination):
    try:
        lcd.lcd_display_string("Transferring Data", 1)
        lcd.lcd_display_string("Please do not remove the USB", 2)
        lcd.lcd_display_string("", 3)
        lcd.lcd_display_string("", 4)
        if os.path.exists(destination):
            shutil.rmtree(destination)
            shutil.copytree(data, destination)
        else:
            shutil.copytree(data, destination)
        lcd.lcd_display_string("Transfer Complete", 1)
        lcd.lcd_display_string("", 2)
        return 1
    except:
        lcd.lcd_display_string("Currently Unable to", 1)
        lcd.lcd_display_string("Transfer Data to Drive", 2)
        lcd.lcd_display_string("", 3)
        lcd.lcd_display_string("", 4)
        return 0

def main():
    # Declare paths.
    src = './CompostMonitoringData'
    destination = '/media/pi/537D-B88D/Sensor_Data'                 # Change the destination according to your uSB address.
    save_timer = 0
    
    # Declare the lcd display screen.
    lcd = lcddriver.lcd()

    # Declaring the objects.
    moisture_one = MoistureSensor(MCP.P0)
    moisture_two = MoistureSensor(MCP.P1)
    moisture_three = MoistureSensor(MCP.P3)
    temp_one = TemperatureSensor(0)
    temp_two = TemperatureSensor(1)
    temp_three = TemperatureSensor(2)

    # Calibrates the sensors in parallel.
    p1 = Process(target=moisture_one.calibrate())
    p1.start()
    p2 = Process(target=moisture_two.calibrate())
    p2.start()
    p3 = Process(target=moisture_three.calibrate())
    p3.start()

    p1.join()
    p2.join()
    p3.join()

    db = PickleShareDB('./CompostMonitoringData')

    while (True):
        # Sets up the temperature variables.
        temperature_one = temp_one.read_temp()    
        temperature_two = temp_two.read_temp()
        temperature_three = temp_three.read_temp()
        current_M1_Val = moisture_one.mapSensorVals()
        current_M2_Val = moisture_two.mapSensorVals()
        current_M3_Val = moisture_three.mapSensorVals()
        

        dt_string = dt.now().strftime("%d/%m/%Y %H:%M:%S")

        # Loads the json from the database.
        if 'data' not in db.keys():
            db['data'] = []
        
        # Stores existing data from pickleShare db into existing_data.
        existing_data = db['data']

        # Creates a dict of the current vals.
        curr_data = {
            'moisture_value_1': current_M1_Val,
            'moisture_value_2': current_M2_Val,
            'moisture_value_3': current_M3_Val,
            'temp_value_1': temperature_one,
            'temp_value_2': temperature_two,
            'temp_value_3': temperature_three,
            'time': dt_string,
        }

        # Appends the new data.
        existing_data.append(curr_data)
        
        # if(check_connection()):
        #     db.clear()

        store_locally(db, existing_data)

        # Prints the current values.
        print("Current value", current_M1_Val, current_M2_Val, current_M3_Val, '\n\tCurrent Time:', dt_string)
        print("Current Temps:\n\t" + str(temperature_one) + "\n\t" + str(temperature_two) + "\n\t" + str(temperature_three))

        avg_moisture_val = (current_M1_Val + current_M2_Val + current_M3_Val) / 3
        avg_temperature = (temperature_one + temperature_two + temperature_three) / 3
        
        # Display the values on the lcd.
        lcd.lcd_display_string("Avg Val: " + str(avg_moisture_val) + " " + str(avg_temperature) , 1)
        lcd.lcd_display_string("Probe 1: " + str(current_M1_Val) + " " + str(temperature_one), 2)
        lcd.lcd_display_string("Probe 2: " + str(current_M2_Val) + " " + str(temperature_two), 3)
        lcd.lcd_display_string("Probe 3: " + str(current_M3_Val) + " " + str(temperature_three), 4)

        save_timer += 1;
        # Tries to save data to removable drive every 30 minutes.
        if(save_timer == 1800):
            store_to_removable(src, destination)
            if store_to_removable == 1:
                save_timer = 0
            else:
                # If it can't save it tries every 10 minutes
                save_timer = 1200
        
        time.sleep(5)

main()