import json
import currencyInsertionDetector
import motorcontrol
import imageCaptureSaver
import counterfeitDetection
import currencyDetection
import lcd_control 
import socketio
import threading
import queue
import time
import numpy as np
from datetime import datetime
import base64
import time


import cv2 as cv

WEB_APP = 1
CREATE_VALIDATION_SET = False


# Cancellation flag for child thread
cancel_flag = threading.Event()


def SensorMotorLoop(csvWriter = None):
    secondsSinceLastStop = 100
    timeMotorResumed = 0

    # distance between sensor and the bill on the conveyor belt is 4.8cm
    # new value chosen based on data taken from the sensors. ask me if u want to see the data -chris
    MIN_DISTANCE_IN_M1 = 0.06
    MIN_DISTANCE_IN_M2 = 0.06
    count_threshold1 = 1
    count_threshold2 = 1
    
    startTime = datetime.now().timestamp()

    while not cancel_flag.is_set():
        secondsSinceLastStop = datetime.now().timestamp() - timeMotorResumed

        sampleTime = datetime.now().timestamp()
        sensor1Dist = currencyInsertionDetector.get_distance_sensor1()
        sensor2Dist = currencyInsertionDetector.get_distance_sensor2()

        if (
            sensor1Dist <= MIN_DISTANCE_IN_M1 and
            sensor2Dist <= MIN_DISTANCE_IN_M2
        ):
            print("detected")

            # very hacky. determined through binary search and trial and error
            # feel free to change if need be -chris
            time.sleep(17/64)

            motorcontrol.stop_motor()
            detectTime = datetime.now().timestamp()
            timeMotorResumed = datetime.now().timestamp()
            break
        
        motorcontrol.motor_fwd()

def Transaction(json_data, com_queue):
    data = json.loads(json_data)
    cost = data['cost']
    lcd_control.LCD_display_amount_due(cost)

    # Counters for distance_sensor1 and distance_sensor2
    sensor1_counter = 0
    sensor2_counter = 0

    # Parameters for averaging and filtering
    NUM_MEASUREMENTS = 5  # Number of distance measurements to average

    # Arrays to store distance measurements
    sensor1_measurements = np.zeros(NUM_MEASUREMENTS)
    sensor2_measurements = np.zeros(NUM_MEASUREMENTS)

    while True:
        SensorMotorLoop()

        if cancel_flag.is_set():
            motorcontrol.stop_motor()
            cancel_flag.clear()
            break

        print("start image capture")
        if CREATE_VALIDATION_SET:
            imageCaptureSaver.singlePhoto()

        image_arr = imageCaptureSaver.CaptureImage()

        print("start currecny value detection")
        (amount, error) = currencyDetection.Detect(image_arr)

        print("start counterfeit detection")
        (result, percent) = counterfeitDetection.detectCF(image_arr,amount)

        print("going to payment update")
        if amount <= 0 or result:
            print("rejected")
            # for i in range(400):
            #     motorcontrol.motor_bwd()
            for i in range(160):
                motorcontrol.motor_fwd()
        else:
            cost = cost - amount
            print(f'Accepted: {amount}. Amount left to pay: {cost}')
            
            # display amount left to pay by customer on LCD
            lcd_control.LCD_display_amount_due(cost)

            if WEB_APP:
                #image = imageCaptureSaver.CaptureImage()
                #image = currencyDetection.DownScale(image, 16)
                # Get the current timestamp
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                # Create the filename using the timestamp
                filename = f"{timestamp}.jpg"
                # Set the directory path
                directory = "/home/admin/Desktop/Image_Captures/"
                # Save the image with the timestamped name
                cv.imwrite(directory + filename, image_arr)
                # cv.imwrite("pic.jpg", image_arr)
                # myImg = cv.imread("pic.jpg")
                # frame = cv.imencode('.jpg', myImg)[1]
                # data = base64.b64encode(frame)
                # print('data')
                
                # sio.emit('image', data)
                # time.sleep(2)
                sio.emit('result', {"inserted": amount})                

                # print("waiting on port 3001")
                # sio.wait()
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
        while True:
            try:
                # Initialize the Socket.io client
                sio = socketio.Client()
                sio.connect('http://localhost:8080', namespaces=['/'])
                print("Connected\n")

                
                # Connection successful, break the loop
                break
            except Exception as e:
                # Connection failed, print error and retry after a delay
                print(f"Connection failed: {str(e)}")
                print("Retrying in 3 minutes...")
                time.sleep(180)
        
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
