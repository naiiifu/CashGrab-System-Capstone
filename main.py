import json
import currencyInsertionDetector
import motorcontrol
import imageCaptureSaver
import currencyDetection
import lcd_control 
import socketio
import threading
import queue
import time
import numpy as np
from datetime import datetime

WEB_APP = 0
CREATE_VALIDATION_SET = False


# Cancellation flag for child thread
cancel_flag = threading.Event()

def Transaction(json_data, com_queue):
    data = json.loads(json_data)
    cost = data['cost']

    # Counters for distance_sensor1 and distance_sensor2
    sensor1_counter = 0
    sensor2_counter = 0

    # Parameters for averaging and filtering
    NUM_MEASUREMENTS = 5  # Number of distance measurements to average

    # Arrays to store distance measurements
    sensor1_measurements = np.zeros(NUM_MEASUREMENTS)
    sensor2_measurements = np.zeros(NUM_MEASUREMENTS)

    while True:
        secondsSinceLastStop = 100
        timeMotorResumed = 0

        # distance between sensor and the bill on the conveyor belt is 4.8cm
        MIN_DISTANCE_IN_M1 = 0.04
        MIN_DISTANCE_IN_M2 = 0.04
        count_threshold1 = 7
        count_threshold2 = 7

        while not cancel_flag.is_set():
            secondsSinceLastStop = datetime.now().timestamp() - timeMotorResumed

            # Retrieve distance measurements and store in arrays
            #sensor1_measurements[:-1] = sensor1_measurements[1:]
            #sensor2_measurements[:-1] = sensor2_measurements[1:]
            #sensor1_measurements[-1] = currencyInsertionDetector.get_distance_sensor1()
            #sensor2_measurements[-1] = currencyInsertionDetector.get_distance_sensor2()

            # Apply filtering techniques (e.g., moving average)
            #sensor1_filtered = np.mean(sensor1_measurements)
            #sensor2_filtered = np.mean(sensor2_measurements)
            print("*****")
            print(currencyInsertionDetector.get_distance_sensor1())
            print(currencyInsertionDetector.get_distance_sensor2())
            print("*****")
            if currencyInsertionDetector.get_distance_sensor1() < MIN_DISTANCE_IN_M1:
                sensor1_counter += 1
            else:
                sensor1_counter = 0

            if currencyInsertionDetector.get_distance_sensor2() < MIN_DISTANCE_IN_M2:
                sensor2_counter += 1
            else:
                sensor2_counter = 0

            if (
                sensor1_counter >= count_threshold1 and
                sensor2_counter >= count_threshold2
                #sensor1_filtered < MIN_DISTANCE_IN_M1 and
                #sensor2_filtered < MIN_DISTANCE_IN_M2
            ):
                print("detected")
                detectTime = datetime.now().timestamp()
                motorcontrol.stop_motor()
                timeMotorResumed = datetime.now().timestamp()
                break



            motorcontrol.motor_fwd()

        if cancel_flag.is_set():
            motorcontrol.cleanup()
            cancel_flag.clear()
            break

        if CREATE_VALIDATION_SET:
            imageCaptureSaver.singlePhoto()

        image_arr = imageCaptureSaver.CaptureImage()
        (amount, error) = currencyDetection.Detect(image_arr)

        if amount <= 0:
            print("rejected")
            for i in range(400):
                motorcontrol.motor_bwd()
        else:
            cost = cost - amount
            print(f'Accepted: {amount}. Amount left to pay: {cost}')
            
            # display amount left to pay by customer on LCD
            lcd_control.LCD_display_amount_due(cost)

            if WEB_APP:
                sio.emit('result', {"inserted": amount})
            for i in range(160):
                motorcontrol.motor_fwd()
            for i in range(60):
                motorcontrol.stop_motor()

        if cost <= 0:
            print(f'Transaction Complete!')
            motorcontrol.stop_motor()
            break


if __name__ == "__main__":
    keyPath = "./piValidation.json"
    print("setting up")
    currencyDetection.SetUp(keyPath)
    print("ready")
    
    if not WEB_APP:
        json_data = "{\"cost\":1000}"
        com_queue = queue.Queue()
        child_thread = threading.Thread(target=Transaction, args=(json_data, com_queue))
        child_thread.start()
        print("not web app")

    else:
        # Initialize the Socket.io client
        sio = socketio.Client()
        sio.connect('http://142.58.165.151:8080')
        
        @sio.on('cancel')
        def handle_cancel(msg):                                         
           print(f'cancel msg: {msg}')
           cancel_flag.set()

        # Define a callback function to handle the 'json' event
        @sio.on('json')
        def handle_json(json_data):

            print(f'Received JSON data: {json_data}')

            data = json.loads(json_data)
            cost = data['cost']

            if (cost > 0):
                # Create a child thread
                cancel_flag.clear()
                com_queue = queue.Queue()
                child_thread = threading.Thread(target=Transaction, args=(json_data, com_queue))

                # Start the child thread
                child_thread.start()

            else:
                # Cancel child_thread
                cancel_flag.set()

        

        sio.wait()