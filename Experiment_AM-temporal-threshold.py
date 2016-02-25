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
    exptInfo = {'arduinoSerialPortName':'/dev/cu.usbmodem1411', 
                'dataFolder':'test', 'participantCode':'P00', 
                'condition':'4pins', 'site':'right-foot-sole', 
                'deviceOrientation':0, 'stimToUse':'1,2,3,4', 'stimDuration':5,
                'preStaircaseTrials':[], 'nStaircaseTrials':40, 'startISOI':200,
                'useGoButton':True}
exptInfo['dateStr']= data.getDateStr() #add the current time

dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['dateStr'])
if dlg.OK:
    toFile('lastParams.pickle', exptInfo) # save params to file for next time
else:
    core.quit() # the user hit cancel so exit

stimToUse = [int(i) for i in exptInfo['stimToUse'].split(',')]
## ----

## -- make a text file to save data --
fileName = './'+exptInfo['dataFolder']+'/' + exptInfo['dateStr']+'_'+ exptInfo['participantCode']+'_' + exptInfo['condition']
dataFile = open(fileName+'.csv', 'w') 
dataFile.write('ISOI,direction,correct\n')
## ----

## -- setup staircase --
s = data.StairHandler(startVal = exptInfo['startISOI'],
                          stepType = 'log', stepSizes=0.5,
                          minVal=0, maxVal=1000,
                          nUp=1, nDown=3,  #will home in on the 80% threshold
                          nTrials=exptInfo['nStaircaseTrials'])
## ----

## -- make serial connection to arduino --
arduino = serial.Serial(exptInfo['arduinoSerialPortName'], 9600,timeout=0.05)
connected = False
while not connected:
    arduino.write("ping") # send ping
    arduinoSays = arduino.readline().strip(); print arduinoSays
    if arduinoSays == "ack": #look for arduino ack
        connected = True
## ----

## -- set go button usage --
arduinoSays = ''
while len(arduinoSays) == 0:
    if exptInfo['useGoButton']:
        arduino.write("go button on")
    else:
        arduino.write("go button off")
    arduinoSays = arduino.readline().strip(); print arduinoSays
## ----

## -- run the experiment --
arduinoSays = ''
trialNum = 0
for suggestedISOI in s:
    trialNum+=1
    
    ## turn off go button after first trial
    if trialNum > 1:
        while len(arduinoSays) == 0:
            arduino.write("go button off")
            arduinoSays = arduino.readline().strip(); print arduinoSays
        
    isoi = int(round(suggestedISOI))
    print('ISOI: {}ms' .format(isoi))
    direction = random.choice([0,1])
    
    ## play the stimulus and get the response
    response = load_play_stim(arduino,stimToUse, isoi, 
                exptInfo['stimDuration'], direction, exptInfo['deviceOrientation'],True)
    
    correct = response == direction
    print('Correct : {}' .format(correct))
    s.addResponse(correct, isoi)
    dataFile.write('{},{},{}\n' .format(isoi, direction, correct))
    print '{} of {} trials complete\n\n' .format(trialNum, exptInfo['nStaircaseTrials'])
## ----

## -- end of experiment --
dataFile.close()

s.saveAsPickle(fileName) #special python binary file to save all the info

## -- use quest to estimate threshold -- ##
q = data.QuestHandler(log(exptInfo['startISOI']), log(exptInfo['startISOI']), 
                        pThreshold = 0.82, nTrials = exptInfo['nStaircaseTrials'],
                        grain=0.1, range=log(1000),
                        minVal = 0, maxVal = log(1000))
isois = [log(i) for i in s.intensities]
q.importData(isois,s.data)
# print results
print('threshold: {}' .format(exp(q.mean())))
print('sd: {}' .format(exp(q.sd())))