# Import statements
import json
import time
import RPi.GPIO as GPIO
import urllib.request
import signal
import atexit

# This function takes the API key and a ZIP code and returns the location ID based off of the ZIP code.
def getLocationID(API, ZIP):
    apiurl = 'http://dataservice.accuweather.com/locations/v1/postalcodes/US/search?apikey=%s&q=%s&details=true' % (API, ZIP)
    with urllib.request.urlopen(apiurl) as url:
        data = json.loads(url.read().decode())
    return data[0]["Key"]

# This function takes the API key and Location ID and returns the current weather conditions.
def getCurrentConditions(API, LOCATION_ID):
    apiurl = 'http://dataservice.accuweather.com/currentconditions/v1/%s?apikey=%s&details=true' % (LOCATION_ID, API)
    with urllib.request.urlopen(apiurl) as url:
        data = json.loads(url.read().decode())
    return data

def openBlinds():
    # loop first over "forward" ramp up/down, then reverse.
    for direction in [+1.0]:
        for step in list(range(STEPS + 1)):
            dutycycle = NOMINAL + direction * RANGE * step / STEPS
            print("D ", direction, " S ", step, " dc ", dutycycle)
            p.ChangeDutyCycle(dutycycle)
            time.sleep(1.0)

def closeBlinds():
    # loop first over "forward" ramp up/down, then reverse.
    for direction in [-1.0]:
        for step in list(range(STEPS + 1)):
            dutycycle = NOMINAL + direction * RANGE * step / STEPS
            print("D ", direction, " S ", step, " dc ", dutycycle)
            p.ChangeDutyCycle(dutycycle)
            time.sleep(1.0)

def blindControl(API, LOCATION_ID):
    try:
        # LOCATION_ID = getLocationID(API, ZIP)
        currentConditions = getCurrentConditions(API, LOCATION_ID)
        if (currentConditions[0]["IsDayTime"]):
            if (currentConditions[0]["WeatherIcon"] < 5):
                openBlinds()
            else:
                closeBlinds()
        else:
            closeBlinds()
            # sleep program for however long sunset to sunrise lasts
    except:
        closeBlinds()
        print("Device not Connected to the Internet")


# Creating variabls for the API key and ZIP code
API = "pPLa1x8d39btcTrcr7Lh0U8JzABk6afA"
ZIP = "41076"
LOCATION_ID = "17810_PC"
#17810_PC
#servo = Servo(1)

atexit.register(GPIO.cleanup)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT, initial=False)
p = GPIO.PWM(17,50) #50HZ
p.start(0)
time.sleep(2)

STEPS=10    # the number of steps either side of nominal
NOMINAL=7.5 # the 'zero' PWM %age
RANGE=1.0   # the maximum variation %age above/below NOMINAL

#NOTE: Might want to initialize NOMINAL to 6.5 (or whatever it is with the blinds closed)
#And then set the direction to +2 in loop. Will likely have to set conditionals to see that
#the blinds are already closed (return dutycycle variable and check its value?)

while True:
    #blindControl(API, LOCATION_ID)
    #time.sleep(30)
    openBlinds()
    time.sleep(5)
    closeBlinds()
    time.sleep(5)


