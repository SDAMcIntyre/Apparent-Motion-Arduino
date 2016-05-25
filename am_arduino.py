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
    stimArray = create_pin_array(stimToUse,[5,6,10,11])
    
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

def load_play_tactvis(arduino,tactToUse,visToUse,tactReverse,visReverse,
                    isoi,duration,direction,orientation,responseRequired,printMessages):
    '''
    The first tactile and first visual stimuli will always start at the same time
    arduino: existing serial port connection to arduino
    tactToUse: an array listing which of the six tactors to use e.g. [1,2,3,4,5,6] for all
    visToUse: an array listing which of the six lights to use e.g. [1,2,3,4,5,6] for all
    tactReverse: array listing which tactors to reverse the direction e.g. [3,4] to reverse 3 and 4, [] for no reversal
    visReverse: array listing which lights to reverse the direction e.g. [3,4] to reverse 3 and 4, [] for no reversal
    isoi: inter-stimulus onset interval in milliseconds - the time between activation of each motor/LED
    duration: time in milliseconds that the motors/LEDs remain active
    direction: direction of the unscrambled portion of motion; 0 = distal, 1 = proximal
    orientation: the orientation of the stimulator relative to the participant; 0 = first motor/light is most distal, 1 = first motor/light is most proximal
    responseRequired: do you want to wait for the participant to press a button after the stimulus is presented?
    printMessages: do you want to print messages from the arduino?
    
    '''
    ## convert to 0 index
    tactToUse = [x-1 for x in tactToUse]
    tactReverse = [x-1 for x in tactReverse]
    visToUse = [x-1 for x in visToUse]
    visReverse = [x-1 for x in visReverse]
    
    ## determine order based on orientation and desired direction:
    tactToUse = sorted(tactToUse,None,None,orientation-direction)
    visToUse = sorted(visToUse,None,None,orientation-direction)
    
    ## reverse:
    tactReverse = sorted(tactReverse,None,None,1-orientation-direction)
    visReverse = sorted(visReverse,None,None,1-orientation-direction)
    tactToUse = rev_order(tactToUse,tactReverse)
    visToUse = rev_order(visToUse,visReverse)
    
    ## arduino pins to use for stimulus
    tactArray = create_pin_array(tactToUse,[3,5,6,9,10,11])
    visArray = create_pin_array(visToUse,[33,35,37,39,41,43])
    print('\ntactile pins: {}' .format(tactArray))
    print('\nvisual pins: {}' .format(visArray))
    
    ## calculate onset and offset times based on isoi and duration
    tactOnset = [isoi*i for i in range(len(tactArray))]
    tactOffset = [tactOnset[i]+duration for i in range(len(tactArray))]
    visOnset = [isoi*i for i in range(len(visArray))]
    visOffset = [visOnset[i]+duration for i in range(len(visArray))]
    stimData = sorted(zip(tactOnset+visOnset, tactOffset+visOffset, tactArray+visArray))
    
    ##-- send stimulus values to arduino --
    onset = [val[0] for val in stimData]
    offset = [val[1] for val in stimData]
    stimArray = [val[2] for val in stimData]
    
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

def rev_order(stimToUse,stimReverse):
    r = 0
    for n in range(len(stimToUse)):
        if stimToUse[n] in stimReverse:
            stimToUse[n] = stimReverse[r]
            r+=1
    return stimToUse

def create_pin_array(stimToUse,allPins):
    stimArray = []
    for n in stimToUse:
        stimArray += [allPins[n]]
    return stimArray

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
    isoi = 1000
    duration = 1000
    print('trying')
    response = load_play_stim(arduino,[1,2,3,4],isoi,duration,direction,0,False,True)
    #response = load_play_tactvis(arduino,[1,2,3,4,5,6],[1,2,3,4,5,6],[],[],
#                    isoi,duration,direction,0,False,True)
    print('correct: {}' .format(response == direction))



