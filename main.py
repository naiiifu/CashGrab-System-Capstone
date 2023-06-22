import json
import sys
import currencyInsertionDetector as Detector
import motorcontrol as motor
import imageCaptureSaver as camera
  

  # Define state constants
WAIT_S = 0
TRANSACTION_S = 1
REJECT_S = 2
CANCEL_S = 3


def handle_reject_state():
    pass


def handle_cancel_state(data):
#to cancel a transaction in progress
    pass
    
    


testing = False

if len(sys.argv) > 1:
    # Get the JSON data from the command-line argument
    json_data = sys.argv[1]
  
else:
    #for testing purposes
    print("testing mode control.py")
    json_data = "{\"state\":1, \"cost\":30}"
    testing = True

data = json.loads(json_data)
current_state = data['state']
cost = data['cost']

print("setting up")
sys.stdout.flush() # flush the output buffer
#print(f"curret state {current_state}")
(values, frontFeatures, backFeatures) = camera.setup() #DO: move this to client.py and pass values over command line

print("ready")


while True:
    sys.stdout.flush() # flush the output buffer
    if current_state == WAIT_S:
        break
    elif current_state == CANCEL_S:
        handle_cancel_state(cost)
        current_state = WAIT_S
        
    elif current_state == TRANSACTION_S:
        result = Detector.detect_loop()#infinite loop until sensor detects something within threshold
        if (result==False):
            print(f'Fatal error waiting for sensor')
            break
        #something has been detected move bill to camera POV
        motor.moveToPhoto()
        amount = camera.checkImg(values, frontFeatures, backFeatures)
        if amount <= 0:
            # current_state = REJECT_S
            print("rejected")
            motor.reject()

        else:
            cost = cost - amount
            print(f'Accepted: {amount}. Amount left to pay: {cost}')
            motor.moveToStorage()

        if cost<= 0:#TODO handle this in client.py
            print(f'Transaction Complete!')
            break
            
    elif current_state == REJECT_S:
        continue
        # handle_reject_state(current_state)
        #send message to server?
    else:
        print(f'Invalid state value: {current_state}')
        break

