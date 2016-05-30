import serial
from psychopy import core

arduinoSerialPortName = "/dev/cu.usbmodem1411"
arduino = serial.Serial(arduinoSerialPortName, 9600,timeout=0.05)

sent = range(100)
received = []
core.wait(1)
for i in sent:
    print i
    arduino.write(str(i))
    arduinoSays = arduino.readline().strip()
    if len(arduinoSays) > 0:
        print 'received'
        received += [arduinoSays]
print received
print('{} of {} received.' .format(len(received), len(sent)))