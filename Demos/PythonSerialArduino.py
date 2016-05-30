import serial

arduinoSerialPortName = "/dev/cu.usbmodem1411"
connected = False
arduino = serial.Serial(arduinoSerialPortName, 9600,timeout=0.05)

## wait for connection
while not connected:
    arduino.write("connected") # send ping
    arduinoSays = arduino.readline()[:-2]
    if len(arduinoSays) > 0: print arduinoSays
    if arduinoSays == "connected": #look for arduino ack
        connected = True

## values to send and receive back
myString = "hello"
myInt = 50
myFloat = 50.5
myArray = [5,6,10,11]

## string
arduino.write(myString)
arduinoSays = arduino.readline()[:-2]
print arduinoSays
if arduinoSays == myString:
    print "string successful"

## integer
arduino.write(str(myInt))
arduinoSays = arduino.readline()[:-2]
print arduinoSays
if int(arduinoSays) == myInt:
    print "integer successful"
    
## float
arduino.write(str(myFloat))
arduinoSays = arduino.readline()[:-2]
print arduinoSays
if float(arduinoSays) == myFloat:
    print "float successful"
    
## array of integers
arduino.write(str(myArray))
arduinoSays = arduino.readline()[:-2]
arduinoSays = [int(i) for i in arduinoSays.split(',')]
print arduinoSays
if arduinoSays == myArray:
    print "array successful"

arduino.close()