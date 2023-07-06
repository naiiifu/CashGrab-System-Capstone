import main
import csv
import motorcontrol

"""if __name__ == "__main__":
    motorRunning = True
    motorcontrol.motor_fwd()

    while True:
        val = input("")

        if motorRunning:
            motorRunning = False
            motorcontrol.stop_motor()
        else:
            motorRunning = True
            motorcontrol.motor_fwd()"""

if __name__ == "__main__":
    path = "sonarDistance.csv"
    
    motorcontrol.motor_fwd()

    with open(path, 'w') as file:
        writer = csv.writer(file, lineterminator="\n")
    
        writer.writerow(["Time", "Sensor1Dist", "Sensor2Dist"])
        main.SensorMotorLoop(writer)