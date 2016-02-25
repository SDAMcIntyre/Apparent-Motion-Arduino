from psychopy import core, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import time, numpy, random, os
import serial
from am_arduino import *
from math import *

## -- get input from experimenter --
try:
    exptInfo = fromFile('lastParams.pickle') # previous values
    exptInfo['02. Test number'] += 1
except:        # default values
    exptInfo = {'01. Participant Code':'P00', 
                '02. Test number':1, 
                '03. Probes to use (1-4)':'1,2,3,4', 
                '04. Probe separation (cm)':34, 
                '05. Stimulation site':'right foot', 
                '06. First ISOI (ms)':200,
                '07. Probe activation duration':5,
                '08. Number of adaptive trials':40, 
                '09. Pre-adaptive ISOIs':[], 
                '10. Use GO button':True,
                '11. Folder for saving data':'test', 
                '12. Device orientation (0 or 1)':0, 
                '13. Arduino serial port':'/dev/cu.usbmodem1411', 
                '14. Print arduino messages':False}
exptInfo['15. Date and time']= data.getDateStr(format='%Y-%m-%d-%H-%M') #add the current time

dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['15. Date and time'])
if dlg.OK:
    toFile('lastParams.pickle', exptInfo) # save params to file for next time
else:
    core.quit() # the user hit cancel so exit

stimToUse = [int(i) for i in exptInfo['03. Probes to use (1-4)'].split(',')]
## ----

## -- make folder/files to save data --
dataFolder = './'+exptInfo['11. Folder for saving data']+'/'
if not os.path.exists(dataFolder):
    os.makedirs(dataFolder)
    writeHeaders = True
else:
    writeHeaders = False
thresholdData = open(dataFolder + 'thresholdData.csv', 'a')
if writeHeaders: thresholdData.write('threshold,sd,order,participant,nProbes,separation,site,dateTime\n')
fileName = dataFolder + exptInfo['15. Date and time']+'_'+ exptInfo['01. Participant Code']
trialData = open(fileName+'.csv', 'w') 
trialData.write('ISOI,direction,correct\n')
## ----

## -- setup staircase --
s = data.StairHandler(startVal = exptInfo['06. First ISOI (ms)'],
                          stepType = 'log', stepSizes=0.5,
                          minVal=1, maxVal=1000,
                          nUp=1, nDown=3,  #will home in on the 80% threshold
                          nTrials=exptInfo['08. Number of adaptive trials'])
## ----

## -- make serial connection to arduino --
arduino = serial.Serial(exptInfo['13. Arduino serial port'], 9600,timeout=0.05)
arduinoSays = ''
while not arduinoSays == 'ack':
    arduino.write('ping') 
    arduinoSays = arduino.readline().strip()
    if exptInfo['14. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays)) 
## ----

## -- set go button usage --
goButtonSet = False
arduinoSays = ''
while not goButtonSet:
    if exptInfo['10. Use GO button']:
        message = 'go button on'
    else:
        message = 'go button off'
    arduino.write(message)
    arduinoSays = arduino.readline().strip()
    if exptInfo['14. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
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
            if exptInfo['14. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays))
            
        
    isoi = int(round(suggestedISOI))
    print('ISOI: {}ms' .format(isoi))
    direction = random.choice([0,1])
    
    ## play the stimulus and get the response
    response = load_play_stim(arduino,stimToUse, isoi, 
                exptInfo['07. Probe activation duration'], direction, 
                exptInfo['12. Device orientation (0 or 1)'],responseRequired = True,
                printMessages = exptInfo['14. Print arduino messages'])
    
    correct = response == direction
    print('Correct : {}' .format(correct))
    s.addResponse(correct, isoi)
    trialData.write('{},{},{}\n' .format(isoi, direction, correct))
    print '{} of {} trials complete\n\n' .format(trialNum, exptInfo['08. Number of adaptive trials'])
## ----

## -- use quest to estimate threshold --
q = data.QuestHandler(log(exptInfo['06. First ISOI (ms)']), log(exptInfo['06. First ISOI (ms)']), 
                        pThreshold = 0.82, nTrials = exptInfo['08. Number of adaptive trials'],
                        grain=0.1, range=log(1000),
                        minVal = 0, maxVal = log(1000))
isois = [log(i) for i in s.intensities]
q.importData(isois,s.data)
threshold = exp(q.mean())
tSD = exp(q.sd())
print('threshold: {}' .format(threshold))
print('sd: {}' .format(tSD))

## -- save data --
trialData.close()
s.saveAsPickle(fileName) #special python binary file to save all the info
thresholdData.write('{},{},{},{},{},{},{},{}\n' .format(threshold,tSD,
                    exptInfo['02. Test number'],
                    exptInfo['01. Participant Code'],
                    len(stimToUse),
                    exptInfo['04. Probe separation (cm)'],
                    exptInfo['05. Stimulation site'],
                    exptInfo['15. Date and time']))