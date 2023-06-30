import RPi.GPIO as GPIO
import time

SERVO_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)  # PWM frequency = 50Hz
servo.start(0)  # Start PWM with duty cycle of 0

def motor_fwd():
    servo.ChangeDutyCycle(10)  # Forward position (10% duty cycle)
    time.sleep(0.1)

def motor_bwd():
    servo.ChangeDutyCycle(5)  # Backward position (5% duty cycle)
    time.sleep(0.1)

def stop_motor():
    servo.ChangeDutyCycle(0)  # Stop position (0% duty cycle)
    time.sleep(0.1)



if __name__ == "__main__":
    try:
        while True:
            motor_fwd()
            stop_motor()
            time.sleep(1)
            motor_bwd()
            stop_motor()
            time.sleep(1)
    except KeyboardInterrupt:
        stop_motor()
