import time
from readSensors import ReadSensor

class MoistureSensor(ReadSensor):

    def __init__(self, pinNum):
        super().__init__(pinNum)

    # Calibrate the set moisture sensors.
    def calibrate(self):
        sCalibrateVals = []
        print("Calibrating...")
        for i in range(25):
            sCalibrateVals.insert(i, self.getVal())
            print("\tAdding Val: ", sCalibrateVals[i])
            time.sleep(1)
        
        self.maxVal = max(sCalibrateVals)
        self.minVal = min(sCalibrateVals)

        print("Max Value: ", self.maxVal)
        print("Min Value: ", self.minVal)
        print("\nDone calibrating")

    # Maps the raw input accordingly
    def mapSensorVals(self):
        val = 0
        try:
            val = int((self.getVal() - 0) * (950 - 0) / (self.maxVal - 0) + 0)
        except Exception as e:
            pass
        return val