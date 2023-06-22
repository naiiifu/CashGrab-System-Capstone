import RPi.GPIO as GPIO
import time
from gpiozero import Servo

#TODO fix awful code and deal with excpetions?

# init motor pins
# servoPIN = 17
# servo = Servo(servoPIN)
SERVO_PIN = 17

isForward = True


# stop motors from running so that camera can take picture of bill
# def motor_stop():


# run motors towards the deposit box until sonar sensor says to stop
# def motor_forward():
#     # servo.value values from 0 to 1.0 are fwd direction
#     counter = 1
#     val = 0
    
#     while isForward:
#         print("servo.value: ")
#         print(servo.value)
#         servo.value = val
#         time.sleep(1)

#         if counter == 1:
#             val = val + 0.1 # test to see if should increment by more than 0.1
#         elif counter == 0:
#             val = val - 0.1

#         if val > 0.8:
#             counter = 0
#         elif val < 0.2:  
#             counter = 1


# # run motors in reverse for bill rejection, find duration for this
# # then, resume forward rotation
# def motor_reject():
#     # servo.value values from -1.0 to 0 are bwd direction
#     counter = 1
#     val = 0
#     while not isForward:
#         print("servo.value: ")
#         print(servo.value)
#         servo.value = val
#         time.sleep(1)

#         if counter == 1:
#             val = val - 0.1 # test to see if should increment by more than 0.1
#         elif counter == 0:
#             val = val + 0.1

#         if val < -0.8:
#             counter = 0
#         elif val > -0.2:
#             counter = 1


def motor_wait_for_camera():
    # wait 5s for camera to take picture of bill
    time.sleep(5)


def moveToPhoto():
    servoPIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    motor = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
    motor.start(2.5)
    motor.ChangeDutyCycle(10)#forward
    time.sleep(5)  #need to find time

        

def stop_motor():
    motor = GPIO.PWM(17, 50) # GPIO 17 for PWM with 50Hz
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



if __name__ == "__main__":
    try:
        # motor_forward()
        # time.sleep(5)
        # isForward = False
        # motor_reject()
        while True:
            moveToPhoto()
            stop_motor()
            time.sleep(5)

    except KeyboardInterrupt:
        cleanup()
    finally:
        cleanup()