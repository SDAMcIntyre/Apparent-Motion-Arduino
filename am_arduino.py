def load_play_stim(arduino,stimToUse,isoi,duration,direction,orientation,responseRequired,printMessages):
    '''
    arduino: existing serial port connection to arduino
    stimToUse: an array listing which of the four solenoid stimuli to use e.g. [1,2,3,4] for all
    isoi: inter-stimulus onset interval in milliseconds - the time between activation of each solenoid
    duration: time in milliseconds that the solenoid remains active
    direction: 0 = distal, 1 = proximal
    orientation: the orientation of the stimulator relative to the participant; 0 = first solenoid is most distal, 1 = first solenoid is most proximal
    responseRequired: do you want to wait for the participant to press a button after the stimulus is presented?
    printMessages: do you want to print messages from the arduino?
    
    This function assumes "normal" apparent motion (not scrambled), and sorts the order of solenoid activation on your behalf based on orientation and desired direction
    '''
    stimToUse = [x-1 for x in stimToUse] # return to 0 index
    ## determine order based on orientation and desired direction:
    stimToUse = sorted(stimToUse,None,None,orientation-direction) 
    
    ## arduino pins to use for stimulus
    stimArray = []
    allPins = [5,6,10,11]
    for pin in stimToUse:
        stimArray += [allPins[pin]]
    
    ## calculate onset and offset times based on isoi and duration
    onset = [isoi*i for i in range(len(stimArray))]
    offset = [onset[i]+duration for i in range(len(stimArray))]
    
    ##-- send stimulus values to arduino --
    
    ## number of stimuli
    arduinoSays = ''
    while not arduinoSays == 'nStim':
        arduino.write('nStim')
        arduinoSays = arduino.readline().strip()
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
    nStimSent = False
    while not nStimSent:
        nStim = len(stimArray)
        arduino.write(str(nStim))
        arduinoSays = arduino.readline().strip()
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
        if int(arduinoSays) == nStim: nStimSent = True
    
    ## stimulus array
    while not arduinoSays == 'stimArray':
        arduino.write('stimArray')
        arduinoSays = arduino.readline().strip()
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
    stimArraySent = False
    while not stimArraySent:
        arduino.write(str(stimArray))
        arduinoSays = arduino.readline().strip();
        arduinoSays = [int(i) for i in arduinoSays.split(',')]
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
        if arduinoSays == stimArray: stimArraySent = True
    
    ## onset times
    while not arduinoSays == 'onset':
        arduino.write('onset')
        arduinoSays = arduino.readline().strip()
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
    onsetSent = False
    while not onsetSent:
        arduino.write(str(onset))
        arduinoSays = arduino.readline().strip();
        arduinoSays = [int(i) for i in arduinoSays.split(',')]
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
        if arduinoSays == onset: onsetSent = True
    
    ## offset times
    while not arduinoSays == 'offset':
        arduino.write('offset')
        arduinoSays = arduino.readline().strip()
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
    offsetSent = False
    while not offsetSent:
        arduino.write(str(offset))
        arduinoSays = arduino.readline().strip();
        arduinoSays = [int(i) for i in arduinoSays.split(',')]
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
        if arduinoSays == offset: offsetSent = True
    
    ## ----
    
    ## -- play the stimulus --
    while not arduinoSays == "stimulus":
        arduino.write("go")
        arduinoSays = arduino.readline().strip()
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
    ## ----
    
    ## -- get response from arduino
    if responseRequired:
        while not arduinoSays == "response":
            arduinoSays = arduino.readline().strip(); 
            if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
        gotResponse = False
        while not gotResponse:
            arduinoSays = arduino.readline().strip()
            if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
            response = int(arduinoSays)
            if response == 0 or response == 1: gotResponse = True
        return response
    else:
        return None
    ## ----

def set_go_button(setting,arduino,printMessages):
    goButtonSet = False
    arduinoSays = ''
    while not goButtonSet:
        if setting:
            message = 'go button on'
        else:
            message = 'go button off'
        arduino.write(message)
        arduinoSays = arduino.readline().strip()
        if printMessages and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
        if arduinoSays == message: goButtonSet = True
    return None

if __name__ == "__main__":
    import serial
    arduino = serial.Serial('/dev/cu.usbmodem1411', 9600,timeout=0.05)
    direction = 1
    response = load_play_stim(arduino,[1,2,3,4],200,5,direction,0,True,True)
    print('correct: {}' .format(response == direction))



