import RPi.GPIO as GPIO
import time

TRIG_PIN = 7
ECHO_PIN = 11

SECONDS_TO_MICRO = 1 / 100000

GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

THRESHOLD = 5

FILTER_LENGTH = 5
averageFilter = []

for i in range(0, FILTER_LENGTH):
    averageFilter.append(0.0)

def __AddToFilter(newValue):
    for i in range(0, len(averageFilter) - 1):
        averageFilter[i] = averageFilter[i + 1]
    
    averageFilter[len(averageFilter) - 1] = newValue

def __GetRunningAverage():
    return sum(averageFilter / len(averageFilter))

def __GetPulseDuration():
    pulse_start_time = 0.0
    pulse_end_time = 0.0
    
    # find duration of the pulse
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start_time = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time

    distance = round(pulse_duration * 17150, 2)
    return distance

def DetectInsertion():
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(2 * SECONDS_TO_MICRO)

    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(10 * SECONDS_TO_MICRO)

    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulseDuration = __GetPulseDuration()

    return pulseDuration <= THRESHOLD