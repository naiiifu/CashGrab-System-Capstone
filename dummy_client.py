import json
import subprocess

#simplified version of client to test subprocess pipe communication

def createJson(line):
    # Extract relevant data from the "Accepted" line
    data = line.split(":")[1].split(".")[0].strip()
    value = int(data)
    json_data = {"inserted": value}
    return json_data
 


json_data = "{\"state\":1, \"cost\":350}" #sample transaction

# Start the control.py script as a subprocess
proc = subprocess.Popen(['python', 'control.py', json_data], stdout=subprocess.PIPE, text=True)

# Continuously read the output from the subprocess
for line in proc.stdout:
    print(line.strip())
    if line.startswith("Accepted"):#send amount accepeted to webapp
        json_data = createJson(line)
        print(json_data['inserted'])
        #sio.emit('result',json_data)
