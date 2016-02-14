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
                'orientation':0, 'stimToUse':'1,2,3,4', 'duration':100,
                'preQuestTrials':[], 'nQuestTrials':40, 'startISOI':200}
exptInfo['dateStr']= data.getDateStr() #add the current time

dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['dateStr'])
if dlg.OK:
    toFile('lastParams.pickle', exptInfo) # save params to file for next time
else:
    core.quit() # the user hit cancel so exit

stimToUse = [int(i) for i in exptInfo['stimToUse'].split(',')]
## ----

## -- make a text file to save data --
fileName = './'+exptInfo['dataFolder']+'/' + exptInfo['dateStr']+'_'+
exptInfo['participantCode']+'_' + exptInfo['condition']
dataFile = open(fileName+'.csv', 'w') 
dataFile.write('ISOI,direction,correct\n')
## ----

## -- setup quest --
q = data.QuestHandler(log(exptInfo['startISOI']), log(exptInfo['startISOI']*3/4), 
                        pThreshold = 0.82, nTrials = exptInfo['nQuestTrials'],
                        method='quantile', grain=0.1, range=log(1000),
                        minVal = 0, maxVal = log(1000))
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

## -- run the experiment --
for thisISOI in q:
    core.wait(0.5) # delay of 500ms
    isoi = int(round(exp(thisISOI)))
    print 'ISOI: '
    print isoi
    direction = random.choice([0,1])
    duration = int(round(isoi*1.2)) #exptInfo['duration']
    response = load_play_stim(arduino,stimToUse, isoi, 
                duration, direction, exptInfo['orientation'])
    
    correct = response == direction
    print 'Correct '
    print correct
    q.addResponse(correct, thisISOI)
    dataFile.write('%i,%.3f,%i\n' %(isoi, direction, correct))
## ----

## -- end of experiment --
dataFile.close()

q.saveAsPickle(fileName) #special python binary file to save all the info

# print results
print 'threshold:'
print exp(q.mean())
print 'sd:'
print exp(q.sd())