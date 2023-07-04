from gpiozero import DistanceSensor
import time


TRIG_PIN = 6
ECHO_PIN = 13

TRIG_PIN2 = 3
ECHO_PIN2 = 14  

ultrasonic = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN)
ultrasonic2 = DistanceSensor(echo=ECHO_PIN2, trigger=TRIG_PIN2)

def get_distance_sensor1():
    return ultrasonic.distance

def get_distance_sensor2():
    return ultrasonic2.distance

if __name__ == '__main__':
    while (1):
        print("*****")
        print(get_distance_sensor1())
        print(get_distance_sensor2())
        print("*****")
        time.sleep(1)
    

    pass