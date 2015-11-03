import serial

vibArray = [11,10,6,5]
soa = 100
dur = 120
onset = [soa*i for i in range(len(vibArray))] 
offset = [onset[i]+dur for i in range(len(vibArray))]

## make serial connection to arduino
arduinoSerialPortName = "/dev/cu.usbmodem1421"
connected = False
arduino = serial.Serial(arduinoSerialPortName, 115200,timeout=2)
## wait for connection
while not connected:
    arduino.write("connected") # send ping
    arduinoSays = arduino.readline().strip()
    print arduinoSays
    if arduinoSays == "connected": #look for arduino ack
        connected = True

## pass stimulus values to arduino
arduino.write(str(len(vibArray)))
arduino.write(str(vibArray));
arduino.write(str(onset));
arduino.write(str(offset));

## tell arduino to go
arduino.write("go")

finished = False
while not finished:
    arduinoSays = arduino.readline().strip()
    print arduinoSays
    if arduinoSays == 'finished':
        finished = True

## close the port and end the program
arduino.close()