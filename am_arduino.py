def load_play_stim(arduino,stimToUse,isoi,duration,direction,orientation):
    '''
    arduino: existing serial port connection to arduino
    stimToUse: an array listing which of the four solenoid stimuli to use e.g. [1,2,3,4] for 			all
    isoi: inter-stimulus onset interval in milliseconds - the time between activation of each solenoid
    duration: time in milliseconds that the solenoid remains active
    direction: 0 = distal, 1 = proximal
    orientation: the orientation of the stimulator relative to the participant; 0 = first solenoid is most distal, 1 = first solenoid is most proximal
    This function assumes "normal" apparent motion (not scrambled), and sorts the order of solenoid activation on your behalf based on orientation and desired direction
    '''
    stimToUse = [x-1 for x in stimToUse] # return to 0 index
    # determine order based on orientation and desired direction:
    stimToUse = sorted(stimToUse,None,None,orientation-direction) 
    
    stimArray = []
    allPins = [5,6,10,11]
    for pin in stimToUse:
        stimArray += [allPins[pin]]
    
    
    onset = [isoi*i for i in range(len(stimArray))]
    offset = [onset[i]+duration for i in range(len(stimArray))]
    
    ## send stimulus values to arduino
    
    ## number of stimuli
    arduinoSays = ''
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
    
    return response
   
  
 

if __name__ == "__main__":
    import serial
    arduino = serial.Serial('/dev/cu.usbmodem1411', 9600,timeout=0.05)
    direction = 1
    response = load_play_stim(arduino,[1,2,3,4],80,50,direction,0)
    print 'correct:'
    print response == direction