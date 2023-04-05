import json
import socketio
import subprocess

# Initialize the Socket.io client
sio = socketio.Client()
sio.connect('http://207.23.185.178:8080')

# Define a callback function to handle the 'json' event
@sio.on('json')
def handle_json(json_data):
    data = json.loads(json_data)
    print(f'Received JSON data: {data}')

    # Call the control.py script with the JSON data as an argument
    result = subprocess.run(['python', 'control.py', json_data], capture_output=True, text=True)
    print(result)
    # Send the result back to the server
    sio.emit('result', result.stdout.strip())

# Connect to the server

sio.emit('result', "hello");
# Wait for responses from the server
print("waiting on port 3001")
sio.wait()
