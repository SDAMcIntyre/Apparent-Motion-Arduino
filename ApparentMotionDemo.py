import serial

## USER INPUT ------------------------------ ##
arduinoSerialPortName = "/dev/cu.usbmodem1421"
stimArray = [5,6,10,11]
soa = 100
dur = 120
## ----------------------------------------- ##

onset = [soa*i for i in range(len(stimArray))] 
offset = [onset[i]+dur for i in range(len(stimArray))]

## make serial connection to arduino
arduino = serial.Serial(arduinoSerialPortName, 9600,timeout=0.05)
connected = False
while not connected:
    arduino.write("ping") # send ping
    arduinoSays = arduino.readline().strip(); print arduinoSays
    if arduinoSays == "ack": #look for arduino ack
        connected = True

## send stimulus values to arduino

## number of stimuli
while not arduinoSays == "stim":
    arduino.write("stim")
    arduinoSays = arduino.readline().strip(); print arduinoSays
nStimSent = False
while not nStimSent:
    nStim = len(stimArray)
    arduino.write(str(nStim))
    arduinoSays = arduino.readline().strip(); print arduinoSays
    if int(arduinoSays) == nStim:
        nStimSent = True
    
## stimulus array
while not arduinoSays == "stim":
    arduinoSays = arduino.readline().strip(); print arduinoSays
stimArraySent = False
while not stimArraySent:
    arduino.write(str(stimArray))
    arduinoSays = arduino.readline().strip();
    arduinoSays = [int(i) for i in arduinoSays.split(',')]
    print arduinoSays
    if arduinoSays == stimArray:
        stimArraySent = True
    
## onset times
while not arduinoSays == "stim":
    arduinoSays = arduino.readline().strip(); print arduinoSays
onsetSent = False
while not onsetSent:
    arduino.write(str(onset))
    arduinoSays = arduino.readline().strip();
    arduinoSays = [int(i) for i in arduinoSays.split(',')]
    print arduinoSays
    if arduinoSays == onset:
        onsetSent = True

## offset times
while not arduinoSays == "stim":
    arduinoSays = arduino.readline().strip(); print arduinoSays
offsetSent = False
while not offsetSent:
    arduino.write(str(offset))
    arduinoSays = arduino.readline().strip();
    arduinoSays = [int(i) for i in arduinoSays.split(',')]
    print arduinoSays
    if arduinoSays == offset:
        offsetSent = True

## tell arduino to go
while not arduinoSays == "stimulus":
    arduino.write("go")
    arduinoSays = arduino.readline().strip(); print arduinoSays

## get response from arduino
while not arduinoSays == "response":
    arduinoSays = arduino.readline().strip(); 
    if len(arduinoSays) > 0:
        print arduinoSays
gotResponse = False
while not gotResponse:
    arduinoSays = arduino.readline().strip()
    print arduinoSays
    response = int(arduinoSays)
    if response == 0 or response == 1:
        gotResponse = True

## close the port and end the program
arduino.close()