import json
import currencyInsertionDetector
import motorcontrol
import imageCaptureSaver
import currencyDetection
import socketio
import threading
import queue
import time
from datetime import datetime

WEB_APP = 0
CREATE_VALIDATION_SET = False


# Cancellation flag for child thread
cancel_flag = threading.Event()

def Transaction(json_data, com_queue):
    data = json.loads(json_data)
    cost = data['cost']

    while True:

        secondsSinceLastStop = 100
        timeMotorResumed = 0

        # distance between sensor and the bill on the conveyor belt is 4.8cm
        MIN_DISTANCE_IN_M = 0.05
        # motorcontrol.motor_bwd()
        while not cancel_flag.is_set(): 
            # print("distance: ")
            # print(currencyInsertionDetector.get_distance())
            # print("timeMotorResumed:")
            # print(timeMotorResumed)
        
            secondsSinceLastStop = datetime.now().timestamp() - timeMotorResumed
            # print("secondsSinceLastStop:")
            # print(secondsSinceLastStop)

            if currencyInsertionDetector.get_distance1() < MIN_DISTANCE_IN_M and currencyInsertionDetector.get_distance2() < MIN_DISTANCE_IN_M:
                for i in range(10):
                  motorcontrol.motor_fwd()
                print("detected")
                detectTime = datetime.now().timestamp()
                time.sleep(0.5)
                motorcontrol.stop_motor() 
                timeMotorResumed = datetime.now().timestamp()
                break
        
            else:
                motorcontrol.motor_fwd()
        
        if cancel_flag.is_set():
            motorcontrol.cleanup()
            cancel_flag.clear()
            break
        if(CREATE_VALIDATION_SET):
            imageCaptureSaver.singlePhoto()
        image_arr = imageCaptureSaver.CaptureImage()

        (amount, error) = currencyDetection.Detect(image_arr)

        if amount <= 0:
            print("rejected")
            for i in range(75):
              motorcontrol.motor_bwd()

        else:
            cost = cost - amount
            print(f'Accepted: {amount}. Amount left to pay: {cost}')
            if WEB_APP:
                sio.emit('result', {"inserted": amount})
            for i in range(40):
                motorcontrol.motor_fwd()

        if cost<= 0: #TODO handle this in client.py
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

    else:
        # Initialize the Socket.io client
        sio = socketio.Client()
        sio.connect('http://localhost:8080')

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

        @sio.on('cancel')
        def handle_cancel(msg):
           print(msg)
           cancel_flag.set()

        sio.wait()