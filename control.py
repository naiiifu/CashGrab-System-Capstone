import json
import sys

# Define state constants
WAIT_S = 0
SENSOR_S = 1
TRANSACTION_S = 2
REJECT_S = 3
CANCEL_S = 4

# Function to read the state from the socket
def read_socket(json_data):
    # Read a JSON packet from the socket
    json_data = input()
    data = json.loads(json_data)

    # Extract the 'state' value from the JSON data
    state = data['state']

    # Return the state as an integer
    return int(state)

# Function to handle the SENSOR_S state
def handle_sensor_state(data):
    print(data)
    # Do something when in SENSOR_S state
    pass

# Function to handle the TRANSACTION_S state
def handle_transaction_state(data):
    print(data)
    # Do something when in TRANSACTION_S state
    pass

# Function to handle the REJECT_S state
def handle_reject_state(data):
    # Do something when in REJECT_S state
    print(data)
    pass

# Function to handle the CANCEL_S state
def handle_cancel_state(data):
    # Do something when in CANCEL_S state
    print(data)
    pass

if __name__ == '__main__':
    # Set the initial state to WAIT_S
    current_state = WAIT_S
    print("Control.py running")
    # Get the JSON data from the command-line argument
    json_data = sys.argv[1]
    current_state = read_socket(json_data)
    print(current_state)
    while True:
        # Read the state from the socket
        print("loop")

        # Check the current state and execute the appropriate action
        if current_state == WAIT_S:
            print("waited twice breaking")
            break
            # Do something when in WAIT_S state
            pass
        elif current_state == SENSOR_S:
            handle_sensor_state()
            current_state = WAIT_S
        elif current_state == TRANSACTION_S:
            handle_transaction_state()
            current_state = WAIT_S
        elif current_state == REJECT_S:
            handle_reject_state()
            current_state = WAIT_S
        elif current_state == CANCEL_S:
            handle_cancel_state()
            current_state = WAIT_S
        else:
            print(f'Invalid state value: {current_state}')
            current_state = WAIT_S