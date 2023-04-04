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

current_state = WAIT_S

# Get the JSON data from the command-line argument
json_data = sys.argv[1]
data = json.loads(json_data)
current_state = data['state']
cost = data['cost']
print(current_state)
(values, frontFeatures, backFeatures) = camera.setup()
while True:

    if current_state == WAIT_S:
        break
    elif current_state == CANCEL_S:
        handle_cancel_state(cost)
        current_state = WAIT_S
    elif current_state == TRANSACTION_S:
        result = Detector.DetectInsertion()
        if (result==False):
            #current_state = TRANSACTION_S
            continue
        motor.moveToPhoto()
        amount = camera.checkImg(values, frontFeatures, backFeatures)
        if amount <= 0:
            current_state = REJECT_S
        #send message to server 
        sys.print_to_stdout(amount)
    elif current_state == REJECT_S:
        handle_reject_state(current_state)
        #send message to server?
    
    else:
        sys.print_to_stdout(f'Invalid state value: {current_state}')

    current_state = WAIT_S