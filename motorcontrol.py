import RPi.GPIO as GPIO
import time

#TODO fix awful code and deal with excpetions?


def moveToPhoto():
    servoPIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    motor = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
    motor.start(2.5)
    motor.ChangeDutyCycle(10)#forward
    time.sleep(2.7)  #need to find time
    motor.stop()



def moveToStorage():
    servoPIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    motor = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
    motor.start(2.5)
    motor.ChangeDutyCycle(10)#forward
    time.sleep(5)  #need to find time
    motor.stop()



def reject():
    servoPIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    motor = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
    motor.start(2.5)
    motor.ChangeDutyCycle(5)#backward
    time.sleep(4)  #need to find time
    motor.stop()

        
def cleanup():
    GPIO.cleanup()
        
if __name__ == "__main__":
    try:
        time.sleep(2)
        moveToPhoto()
        print("photo time(fake)")
        time.sleep(4)
        print("bad photo rejecting")
        reject()
        
        
    except KeyboardInterrupt:
        cleanup()
    finally:
        cleanup
        

