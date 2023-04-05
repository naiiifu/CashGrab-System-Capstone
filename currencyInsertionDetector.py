import RPi.GPIO as GPIO
import time

TRIG_PIN = 2
ECHO_PIN = 13

SECONDS_TO_MICRO = 1 / 100000

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

THRESHOLD = 11

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
    
    startTime = time.time()
    # find duration of the pulse
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start_time = time.time()
        if pulse_start_time - startTime > 1:
            return 9999 # any arbitrary large number
            
    startTime = time.time()
    
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end_time = time.time()
        if pulse_end_time - startTime > 1:
            return 9999 # any arbitrary large number

    pulse_duration = pulse_end_time - pulse_start_time

    distance = round(pulse_duration * 17150, 2)
    # print(distance)
    return distance

def DetectInsertion():
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(2 * SECONDS_TO_MICRO)

    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(10 * SECONDS_TO_MICRO)

    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulseDuration = __GetPulseDuration()

    return pulseDuration <= THRESHOLD
    
    
def detect_loop():
    while(True):
        if(DetectInsertion()):
            break
    return True
        


if __name__ == '__main__':
    while True:
        print(DetectInsertion())
