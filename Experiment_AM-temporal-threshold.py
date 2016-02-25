from psychopy import core, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import time, numpy, random
import serial
from am_arduino import *
from math import *

## -- get input from experimenter --
try:
    exptInfo = fromFile('lastParams.pickle') # previous values
except:        # default values
    exptInfo = {'01. Participant Code':'P00', 
                '02. Probe separation':'34cm', 
                '03. Stimulation site':'right-foot-sole', 
                '04. Probes to use':'1,2,3,4', 
                '05. First ISOI (ms)':200,
                '06. Probe activation duration':5,
                '07. Number of adaptive trials':40, 
                '08. Pre-adaptive ISOIs':[], 
                '09. Use GO button':True,
                '10. Folder for saving data':'test', 
                '11. Device orientation (0 or 1)':0, 
                '12. Arduino serial port':'/dev/cu.usbmodem1411', 
                '13. Print arduino messages':False}
exptInfo['14. Date and time']= data.getDateStr(format='%Y-%m-%d-%H-%M') #add the current time

dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['14. Date and time'])
if dlg.OK:
    toFile('lastParams.pickle', exptInfo) # save params to file for next time
else:
    core.quit() # the user hit cancel so exit

stimToUse = [int(i) for i in exptInfo['04. Probes to use'].split(',')]
## ----

## -- make a text file to save data --
fileName = './'+exptInfo['10. Folder for saving data']+'/' + exptInfo['14. Date and time']+'_'+ exptInfo['01. Participant Code']+'_' + exptInfo['condition']
dataFile = open(fileName+'.csv', 'w') 
dataFile.write('ISOI,direction,correct\n')
## ----

## -- setup staircase --
s = data.StairHandler(startVal = exptInfo['05. First ISOI (ms)'],
                          stepType = 'log', stepSizes=0.5,
                          minVal=1, maxVal=1000,
                          nUp=1, nDown=3,  #will home in on the 80% threshold
                          nTrials=exptInfo['07. Number of adaptive trials'])
## ----

## -- make serial connection to arduino --
arduino = serial.Serial(exptInfo['12. Arduino serial port'], 9600,timeout=0.05)
arduinoSays = ''
while not arduinoSays == 'ack':
    arduino.write('ping') 
    arduinoSays = arduino.readline().strip()
    if exptInfo['13. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays)) 
## ----

## -- set go button usage --
goButtonSet = False
arduinoSays = ''
while not goButtonSet:
    if exptInfo['09. Use GO button']:
        message = 'go button on'
    else:
        message = 'go button off'
    arduino.write(message)
    arduinoSays = arduino.readline().strip()
    if exptInfo['13. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
    if arduinoSays == message: goButtonSet = True
## ----

## -- run the experiment --
trialNum = 0
for suggestedISOI in s:
    trialNum+=1
    
    ## turn off go button after first trial
    if trialNum == 2:
        message = 'go button off'
        arduinoSays = ''
        while not arduinoSays == message:
            arduino.write(message)
            arduinoSays = arduino.readline().strip()
            if exptInfo['13. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
            
        
    isoi = int(round(suggestedISOI))
    print('ISOI: {}ms' .format(isoi))
    direction = random.choice([0,1])
    
    ## play the stimulus and get the response
    response = load_play_stim(arduino,stimToUse, isoi, 
                exptInfo['06. Probe activation duration'], direction, 
                exptInfo['11. Device orientation (0 or 1)'],responseRequired = True,
                printMessages = exptInfo['13. Print arduino messages'])
    
    correct = response == direction
    print('Correct : {}' .format(correct))
    s.addResponse(correct, isoi)
    dataFile.write('{},{},{}\n' .format(isoi, direction, correct))
    print '{} of {} trials complete\n\n' .format(trialNum, exptInfo['07. Number of adaptive trials'])
## ----

## -- end of experiment --
dataFile.close()

s.saveAsPickle(fileName) #special python binary file to save all the info

## -- use quest to estimate threshold --
q = data.QuestHandler(log(exptInfo['05. First ISOI (ms)']), log(exptInfo['05. First ISOI (ms)']), 
                        pThreshold = 0.82, nTrials = exptInfo['07. Number of adaptive trials'],
                        grain=0.1, range=log(1000),
                        minVal = 0, maxVal = log(1000))
isois = [log(i) for i in s.intensities]
q.importData(isois,s.data)
## ----

## -- get threshold --
threshold = exp(q.mean())
tSD = exp(q.sd())
print('threshold: {}' .format(threshold))
print('sd: {}' .format(tSD))