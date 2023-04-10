import json

import subprocess


#for testing running control.py as a process
result = 1
json_data = "{\"state\":1, \"cost\":350}"
while(result >0
        result = subprocess.run(['python', 'control.py', json_data], capture_output=True, text=True)
    print(result)

