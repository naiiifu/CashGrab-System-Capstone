import RPi.GPIO as GPIO
import time

#UNTESTEDD!!!

# Set up the GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)  # Motor A1
GPIO.setup(12, GPIO.OUT)  # Motor A2
GPIO.setup(13, GPIO.OUT)  # Motor B1
GPIO.setup(15, GPIO.OUT)  # Motor B2

# Move motors forward
def __forward():
    GPIO.output(11, GPIO.HIGH)
    GPIO.output(12, GPIO.LOW)
    GPIO.output(13, GPIO.HIGH)
    GPIO.output(15, GPIO.LOW)

# Move motors backward
def __backward():
    GPIO.output(11, GPIO.LOW)
    GPIO.output(12, GPIO.HIGH)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.HIGH)

# Stop motors
def __stop():
    GPIO.output(11, GPIO.LOW)
    GPIO.output(12, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)

def moveToPhoto():
    try:
        __forward()
        time.sleep(5)  #need to find time
        __stop()
    except Exception:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()


def moveToStorage():
    try:
        __forward()
        time.sleep(5)  #need to find time
        __stop()
    except Exception:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()



def reject():
    try:
        __backward()
        time.sleep(5)  #need to find time
        __stop()
    except Exception:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
