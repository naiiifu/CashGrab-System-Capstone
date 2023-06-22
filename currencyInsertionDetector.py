import RPi.GPIO as GPIO
from gpiozero import DistanceSensor
from gpiozero import Servo
import time
from datetime import datetime

TRIG_PIN = 2
ECHO_PIN = 13
SERVO_PIN = 17

SECONDS_TO_MICRO = 1 / 100000

ultrasonic = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN)

# distance between sensor and the bill on the conveyor belt is 4.8cm
MIN_DISTANCE_IN_M = 0.05

FILTER_LENGTH = 5
averageFilter = []


for i in range(0, FILTER_LENGTH):
    averageFilter.append(0.0)


def __AddToFilter(newValue):
    for i in range(0, len(averageFilter) - 1):
        averageFilter[i] = averageFilter[i + 1]
    
    averageFilter[len(averageFilter) - 1] = newValue


def __GetRunningAverage():
    return sum(averageFilter) / len(averageFilter)


def is_bill_present():
    # get distance reading from sensor
    distanceInM = ultrasonic.distance
    #print("Ultrasonic sensor distance reading (m): ")
    #print(distanceInM)

    # append distance reading to running average filter
    #__AddToFilter(distanceInM)
    # take a sensor reading every 2s, reduce sleep time later
    #time.sleep(0.25)
    # running avg 
    #return __GetRunningAverage() < MIN_DISTANCE_IN_M
    return distanceInM < MIN_DISTANCE_IN_M



def motor_fwd():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    motor = GPIO.PWM(SERVO_PIN, 50) # GPIO 17 for PWM with 50Hz
    motor.start(2.5)
    motor.ChangeDutyCycle(10) #forward
    time.sleep(0.25)  
    #time.sleep(0.25)  0.25s is good


def motor_bwd():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    motor = GPIO.PWM(SERVO_PIN, 50) # GPIO 17 for PWM with 50Hz
    motor.start(2.5)
    motor.ChangeDutyCycle(5)#backward
    time.sleep(4)  #need to find time
    motor.stop()


def stop_motor():
    motor = GPIO.PWM(SERVO_PIN, 50) # GPIO 17 for PWM with 50Hz
    motor.stop()
    time.sleep(2)


def detect_loop():
    secondsSinceLastStop = 100
    timeMotorResumed = 0
    detectTime = 0
    counter = 0

    while True: 
        print("distance: ")
        print(ultrasonic.distance)
        print("timeMotorResumed:")
        print(timeMotorResumed)
        
        secondsSinceLastStop = datetime.now().timestamp() - timeMotorResumed
        print("secondsSinceLastStop:")
        print(secondsSinceLastStop)

        if ultrasonic.distance < MIN_DISTANCE_IN_M and secondsSinceLastStop > 3:
            print("detected")
            detectTime = datetime.now().timestamp()
            time.sleep(2)
            stop_motor() 
            timeMotorResumed = datetime.now().timestamp()
        else:
            motor_fwd()


if __name__ == '__main__':
    motor_bwd()
    detect_loop()
    # while True:
    #     detect_loop()
    #     print(DetectInsertion())
