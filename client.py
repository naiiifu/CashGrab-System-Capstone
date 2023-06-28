import json
import socketio
import subprocess
import imageCaptureSaver as Camera
import cv2
import base64


def createJson(line):
    # Extract relevant data from the "Accepted" line
    data = line.split(":")[1].split(".")[0].strip()
    value = int(data)
    json_data = {"inserted": value}
    return json_data


# Initialize the Socket.io client
sio = socketio.Client()
sio.connect('http://207.23.166.214:8080')

# Define a callback function to handle the 'json' event
@sio.on('json')
def handle_json(json_data):

    print(f'Received JSON data: {json_data}')
    # Start the control.py script as a subprocess
    # proc = subprocess.Popen(['python', 'control.py', json_data], stdout=subprocess.PIPE, text=True)

    # # Continuously read the output from the subprocess
    # for line in proc.stdout:
    #     print(line.strip())
    #     if line.startswith("Accepted"):#send amount accepeted to webapp
    #         json_data = createJson(line)
    #         #print(json_data['inserted'])
    #         sio.emit('result',json_data)


# Connect to the server

# sio.emit('result', "hello");
# Wait for responses from the server
image = Camera.CaptureImage()
cv2.imwrite("pic.jpg", image)

myImg = cv2.imread("pic.jpg")
frame = cv2.imencode('.jpg', myImg)[1]
data = base64.b64encode(frame)
print('data')
sio.emit('image', data)
print("waiting on port 3001")
sio.wait()
