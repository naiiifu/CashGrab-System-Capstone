import json

import subprocess


#for testing running control.py as a process
json_data = "{\"state\":1, \"cost\":350}"
result = subprocess.run(['python', 'control.py', json_data], capture_output=True, text=True)
print(result)
