from psychopy import core, gui, data
from psychopy.tools.filetools import fromFile, toFile
import numpy, random, os, serial, pygame
from math import *
from am_arduino import *

## -- get input from experimenter --
parameterFile = 'lastParams-tactvis.pickle'
try:
    exptInfo = fromFile(parameterFile) # previous values
except:        # default values
    exptInfo = {'01. Participant Code':'P00', 
                '02. Stimulation site':'right hand',
                '03. Session number':1, 
                '04. Conditioning':['incongruent','congruent','off'],
                '05. Conditioning time (sec)':5,
                '06. Top-up time (sec)':5,
                '07. Number of trials':10,
                '08. Conditioning motors (1-6)':'1,2,3,4,5,6',
                '09. Conditioning lights (1-6)':'1,2,3,4,5,6',
                '10. Conditioning reversed motors (1-6)':'3,4',
                '11. Test motors (1-6)':'3,4',
                '12. Test lights (1-6)':'',
                '13. ISOI (ms)':100, 
                '14. Duration (ms)':100,
                '15. Use GO button':True,
                '16. Folder for saving data':'Conditioning-Data', 
                '17. Device orientation (0 or 1)':0, 
                '18. Arduino serial port':'/dev/cu.usbmodem1421', 
                '19. Print arduino messages':False}
exptInfo['20. Date and time']= data.getDateStr(format='%Y-%m-%d_%H-%M-%S') #add the current time
dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['20. Date and time'])
if dlg.OK:
    conditioningType = exptInfo['04. Conditioning']
    exptInfo['04. Conditioning'] = ['incongruent','congruent','off']
    toFile(parameterFile, exptInfo) # save params to file for next time
else:
    core.quit() # the user hit cancel so exit
## ----

## -- convert number lists to arrays --
try: condTactToUse = [int(i) for i in exptInfo['08. Conditioning motors (1-6)'].split(',')] 
except: condTactToUse = []
try: condVisToUse = [int(i) for i in exptInfo['09. Conditioning lights (1-6)'].split(',')]
except: condVisToUse = []
try: condTactRev = [int(i) for i in exptInfo['10. Conditioning reversed motors (1-6)'].split(',')]
except: condTactRev = []
if not conditioningType == 'incongruent':
    condTactRev = [] # only reverse if conditioning is incongruent
try: testTactToUse = [int(i) for i in exptInfo['11. Test motors (1-6)'].split(',')]
except: testTactToUse = []
try: testVisToUse = [int(i) for i in exptInfo['12. Test lights (1-6)'].split(',')]
except: testVisToUse = []
## ----

## -- calculate number of sweeps --
presentationDuration = max(len(condTactToUse),len(condVisToUse)) * exptInfo['13. ISOI (ms)'] + exptInfo['14. Duration (ms)']
nCondSweeps = int(ceil(float(exptInfo['05. Conditioning time (sec)']*1000)/presentationDuration))
print('\nConditioning time = {} sec, {} sweeps.' .format( float(nCondSweeps*presentationDuration)/1000, nCondSweeps))
nTopUpSweeps = int(ceil(float(exptInfo['06. Top-up time (sec)']*1000)/presentationDuration))
print('Top-up time = {} sec, {} sweeps.\n' .format( float(nTopUpSweeps*presentationDuration)/1000, nTopUpSweeps))
## ----

## -- make serial connection to arduino --
arduino = serial.Serial(exptInfo['18. Arduino serial port'], 9600,timeout=0.05)
arduinoSays = ''
while not arduinoSays == 'ack':
    arduino.write('ping') 
    arduinoSays = arduino.readline().strip()
    if exptInfo['19. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays)) 
## ----

## -- set go button usage --
set_go_button(exptInfo['15. Use GO button'],arduino,exptInfo['19. Print arduino messages'])
## ----

## -- RUN THE EXPERIMENT -- ##
correctCount = 0
feedbackText = ['INCORRECT','CORRECT']
nSweeps = nCondSweeps
directionOrder = [0,1] # used for randomising direction of tests

for trialNum in range(exptInfo['07. Number of trials']): # main loop
    
    ## -- things to do after the first trial:
    if trialNum == 1:
        ## -- turn off go button 
        set_go_button(False,arduino,exptInfo['19. Print arduino messages'])
        ## -- switch from conditioning to top-up
        nSweeps = nTopUpSweeps
        
    ## -- conditioning/top-up phase -- ##
    if not conditioningType == 'off':
        startingDirection = 0 # or 1
        for sweep in range(nSweeps):
            ## -- alternate direction
            direction = (startingDirection+sweep) % 2
            ## -- play the sweep
            load_play_tactvis(arduino,condTactToUse,condVisToUse,condTactRev,[],
                                exptInfo['13. ISOI (ms)'],exptInfo['14. Duration (ms)'],
                                direction,exptInfo['17. Device orientation (0 or 1)'],
                                False,exptInfo['19. Print arduino messages']) #don't require responses
    ## ----
    
    ## -- test phase -- ##
    ## -- randomise direction
    directionNum = trialNum % len(directionOrder)
    if directionNum == 0: random.shuffle(directionOrder)
    direction = directionOrder[directionNum]
    ## -- play the stimulus
    response = load_play_tactvis(arduino,testTactToUse,testVisToUse,[],[],
                        exptInfo['13. ISOI (ms)'],exptInfo['14. Duration (ms)'],
                        direction,exptInfo['17. Device orientation (0 or 1)'],
                        True,exptInfo['19. Print arduino messages']) #require responses
    ## -- get the response
    correct = response == direction
    print(feedbackText[correct])
    correctCount += int(correct)
    ## ----

## -- end of the experiment -- ##
print('\n{} of {} correct ({}%).' .format(correctCount,
                                        exptInfo['07. Number of trials'],
                                        100*correctCount/exptInfo['07. Number of trials']) )
