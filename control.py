import json
import sys
import currencyInsertionDetector as Detector
import motorcontrol as motor
import featureCurrencyDetection as camera
  

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
    json_data = "{\"state\":1, \"cost\":300}"
    testing = True

data = json.loads(json_data)
current_state = data['state']
cost = data['cost']


#print(f"curret state {current_state}")
(values, frontFeatures, backFeatures) = camera.setup()#TODO: move this to client.py and pass values over command line

if testing:
    print("ready")
else:
    sys.print_to_stdout(f'State {state} cost {cost}')
while True:
    
    if current_state == WAIT_S:
        break
    elif current_state == CANCEL_S:
        handle_cancel_state(cost)
        current_state = WAIT_S
        
    elif current_state == TRANSACTION_S:
        result = Detector.detect_loop()#infinite loop until sensor detects something within threshold
        if (result==False):
            if(testing):
                print(f'Fatal error waiting for sensor')
                
            else:
                sys.print_to_stdout(f'Fatal error waiting for sensor')
            break;
        #something has been detected move bill to camera POV
        motor.moveToPhoto()
        amount = camera.checkImg(values, frontFeatures, backFeatures)
        if amount <= 0:
            
            # current_state = REJECT_S
            motor.reject()

        else:
            motor.moveToStorage()
            cost = cost - amount

        if(testing):
            print(f'Accepted: {amount}')
            
        else:
            sys.print_to_stdout(f'Accepted: {amount}')
            
        if cost<= 0:#TODO handle this in client.py
            if(testing):
                print(f'Transaction Complete!')
                
            else:
                sys.print_to_stdout(f'Transaction Complete!')
    elif current_state == REJECT_S:
        continue
        # handle_reject_state(current_state)
        #send message to server?
    else:
        if(testing):
            print(f'Invalid state value: {current_state}')
            
        else:
            sys.print_to_stdout(f'Invalid state value: {current_state}')
        break;

