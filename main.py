import json
import currencyInsertionDetector
import motorcontrol
import imageCaptureSaver
import currencyDetection
import socketio
import threading
import queue

WEB_APP = 0

# Cancellation flag for child thread
cancel_flag = threading.Event()

def Transaction(json_data, com_queue):

    data = json.loads(json_data)
    cost = data['cost']

    while True:

        while not cancel_flag.is_set():
            if (currencyInsertionDetector.DetectInsertion()):
                break
        
        if cancel_flag.is_set():
            break

        #something has been detected move bill to camera POV
        motorcontrol.moveToPhoto()

        image_arr = imageCaptureSaver.CaptureImage()
        (amount, error) = currencyDetection.Detect(image_arr)

        if amount <= 0:
            # current_state = REJECT_S
            print("rejected")
            motorcontrol.reject()

        else:
            cost = cost - amount
            print(f'Accepted: {amount}. Amount left to pay: {cost}')
            if WEB_APP:
                sio.emit('result', {"inserted": amount})
            motorcontrol.moveToStorage()

        if cost<= 0: #TODO handle this in client.py
            print(f'Transaction Complete!')
            break



if __name__ == "__main__":
        
    keyPath = "./piValidation.json"
    print("setting up")
    currencyDetection.SetUp(keyPath)
    print("ready")
    
    if not WEB_APP:
        json_data = "{\"cost\":30}"
        com_queue = queue.Queue()
        child_thread = threading.Thread(target=Transaction, args=(json_data, com_queue))
        child_thread.start()

    else:
        # Initialize the Socket.io client
        sio = socketio.Client()
        sio.connect('http://207.23.176.230:8080')

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