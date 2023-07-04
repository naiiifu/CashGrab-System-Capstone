import json
import socketio
import subprocess


def createJson(line):
    # Extract relevant data from the "Accepted" line
    data = line.split(":")[1].split(".")[0].strip()
    value = int(data)
    json_data = {"inserted": value}
    return json_data


# Initialize the Socket.io client
sio = socketio.Client()
sio.connect('http://207.23.176.230:8080')

# Define a callback function to handle the 'json' event
@sio.on('json')
def handle_json(json_data):

    print(f'Received JSON data: {json_data}')
    # Start the control.py script as a subprocess
    proc = subprocess.Popen(['python', 'control.py', json_data], stdout=subprocess.PIPE, text=True)

    # Continuously read the output from the subprocess
    for line in proc.stdout:
        print(line.strip())
        if line.startswith("Accepted"):#send amount accepeted to webapp
            json_data = createJson(line)
            #print(json_data['inserted'])
            sio.emit('result',json_data)


# Connect to the server

# sio.emit('result', "hello");
# Wait for responses from the server
print("waiting on port 3001")
sio.wait()
