import json
import time
import RPi.GPIO as GPIO
import urllib.request
import signal
import atexit

#Sets status to closed for program to control blinds, assumes blinds are shut on launch.
status = "closed"

#Sets Pin out for GPIO on Stepper
in1 = 17
in2 = 18
in3 = 27
in4 = 22

# setting up stepper
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

# initializing stepper
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)

#It resets any ports you have used in this program back to input mode
def cleanup():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
    GPIO.cleanup()


# This function takes the API key and a ZIP code and returns the location ID based off of the ZIP code.
def getLocationID(API, ZIP):
    apiurl = 'http://dataservice.accuweather.com/locations/v1/postalcodes/US/search?apikey=%s&q=%s&details=true' % (API, ZIP)
    with urllib.request.urlopen(apiurl) as url:
        data = json.loads(url.read().decode())
    return data[0]["Key"]

# This function takes the API key and Location ID and returns the current weather conditions in two variables for decisions
def getCurrentConditions(API, LOCATION_ID):
    apiurl = 'http://dataservice.accuweather.com/currentconditions/v1/%s?apikey=%s&details=true' % (LOCATION_ID, API)
    with urllib.request.urlopen(apiurl) as url:
        data = json.loads(url.read().decode())
        daytimestatus = data[0]["IsDayTime"]
        weathericon = data[0]["WeatherIcon"]

    return daytimestatus,weathericon

#This function will look at the blinds status and perform stepper functions to either open or close.
def open_closeBlinds():

#This if loop will perform opposite function/ if open it will close, if closed it will open
    global status
    try:
        global in1
        global in2
        global in3
        global in4

        # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
        step_sleep = 0.002

        #This is about a half revolution which is what is needed to open to half way.
        step_count = 2048  # 5.625*(1/64) per step, 4096 steps is 360

         # defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
        step_sequence = [[1, 0, 0, 1],
                         [1, 0, 0, 0],
                         [1, 1, 0, 0],
                         [0, 1, 0, 0],
                         [0, 1, 1, 0],
                         [0, 0, 1, 0],
                         [0, 0, 1, 1],
                         [0, 0, 0, 1]]

        motor_pins = [in1, in2, in3, in4]
        motor_step_counter = 0;
        i = 0
        for i in range(step_count):
            for pin in range(0, len(motor_pins)):
                GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
            if status == "closed":
                motor_step_counter = (motor_step_counter - 1) % 8
                print(status)
            elif status == "open":
                motor_step_counter = (motor_step_counter + 1) % 8
                print(status)
            time.sleep(step_sleep)

    except KeyboardInterrupt:
        print("uh oh... something went wrong or you just closed the program... not sure.. -_-  ....")
        exit(1)


#This calls the API for results and based on data will open or close blinds, if API Calls fail for any reason blinds will be shut.
def blindControl(API, LOCATION_ID):
    global status
    try:
        # LOCATION_ID = getLocationID(API, ZIP)
        daytime,weathericon = getCurrentConditions(API, LOCATION_ID)
        if daytime:
            if weathericon < 5:
                print("Opening blinds")
                status = "closed"
                open_closeBlinds()
            else:
                print("Conditions not optimal for blinds open")
                if status == "open":
                    open_closeBlinds()
                else:
                    pass
        else:
            print("Its not daytime dummy.. you will see nothing..")
            if status == "open":
                open_closeBlinds()
            else:
                pass
            # sleep program for however long sunset to sunrise lasts
    except:
        status = "open"
        open_closeBlinds()
        print("Device not Connected to the Internet")


# Creating variabls for the API key and ZIP code
API = "pPLa1x8d39btcTrcr7Lh0U8JzABk6afA"
ZIP = "41076"
LOCATION_ID = "17810_PC"
#17810_PC


atexit.register(cleanup)

#Runs Program
while True:
    blindControl(API, LOCATION_ID)
    time.sleep(30)

    #status = "closed"
    #open_closeBlinds()
    #time.sleep(5)
    #status = "open"
    #open_closeBlinds()
    #time.sleep(5)
