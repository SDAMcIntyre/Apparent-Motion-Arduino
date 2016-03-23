from psychopy import core, gui, data
from psychopy.tools.filetools import fromFile, toFile
import numpy, random, os, serial, pygame
from math import *
from am_arduino import *

## -- get input from experimenter --
try:
    exptInfo = fromFile('lastParams.pickle') # previous values
    exptInfo['02. Test number'] += 1
except:        # default values
    exptInfo = {'01. Participant Code':'P00', 
                '02. Test number':1, 
                '03. Probes to use (1-4)':'1,2,3,4', 
                '04. Probe separation (cm)':20, 
                '05. Stimulation site':'right foot', 
                '06. First ISOI (ms)':200,
                '07. Probe activation duration (ms)':100,
                '08. Number of staircases':1,
                '09. Number of trials per staircase':40, 
                '10. Practice ISOIs':'500,300', 
                '11. Min ISOI (ms)':5,
                '12. Max ISOI (ms)':500,
                '13. Use GO button':True,
                '14. Provide feedback':True,
                '15. Folder for saving data':'test', 
                '16. Device orientation (0 or 1)':0, 
                '17. Arduino serial port':'/dev/cu.usbmodem1411', 
                '18. Print arduino messages':False}
exptInfo['19. Date and time']= data.getDateStr(format='%Y-%m-%d_%H-%M-%S') #add the current time

dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['19. Date and time'])
if dlg.OK:
    toFile('lastParams.pickle', exptInfo) # save params to file for next time
else:
    core.quit() # the user hit cancel so exit
    

stimToUse = [int(i) for i in exptInfo['03. Probes to use (1-4)'].split(',')]
try:
    preISOI = [int(i) for i in exptInfo['10. Practice ISOIs'].split(',')]
except:
    preISOI = []
## ----

## -- make folder/files to save data --
if exptInfo['09. Number of trials per staircase'] > 0:
    dataFolder = './'+exptInfo['15. Folder for saving data']+'/'
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)
        writeHeaders = True
    else:
        writeHeaders = False
    thresholdData = open(dataFolder + 'thresholdData.csv', 'a')
    if writeHeaders: thresholdData.write('threshold,sd,staircase,order,participant,nProbes,separation,site,dateTime\n')
    fileName = dataFolder + exptInfo['19. Date and time']+'_'+ exptInfo['01. Participant Code']
    trialData = open(fileName+'.csv', 'w') 
    trialData.write('staircase,ISOI,direction,correct\n')
else:
    exptInfo['02. Test number'] -= 1 #practice only so don't increment the test number
    toFile('lastParams.pickle', exptInfo) 
## ----

## -- setup staircases --
staircases=[]
for n in range(exptInfo['08. Number of staircases']):
    thisStair = data.StairHandler(startVal = exptInfo['06. First ISOI (ms)'],
                          stepType = 'log', stepSizes=0.5,
                          minVal=exptInfo['11. Min ISOI (ms)'], 
                          maxVal=exptInfo['12. Max ISOI (ms)'],
                          nUp=1, nDown=3,  #will home in on the 80% threshold
                          nTrials=exptInfo['09. Number of trials per staircase'],
                          extraInfo={'Label':'staircase'+str(n+1)})
    staircases.append(thisStair)
## ----

## -- setup feedback --
if exptInfo['14. Provide feedback']:
    pygame.mixer.pre_init() 
    pygame.init()
    sounds = [pygame.mixer.Sound('incorrect.wav'),pygame.mixer.Sound('correct.wav')]
    feedbackText = ['INCORRECT','CORRECT']
## ----

## -- make serial connection to arduino --
arduino = serial.Serial(exptInfo['17. Arduino serial port'], 9600,timeout=0.05)
arduinoSays = ''
while not arduinoSays == 'ack':
    arduino.write('ping') 
    arduinoSays = arduino.readline().strip()
    if exptInfo['18. Print arduino messages'] and len(arduinoSays)> 0: print('arduino: {}' .format(arduinoSays)) 
## ----

## -- set go button usage --
set_go_button(exptInfo['13. Use GO button'],arduino,exptInfo['18. Print arduino messages'])
## ----

## -- run the experiment --
correctCount = 0
nPracTrials = len(preISOI)
nTrials = nPracTrials + exptInfo['09. Number of trials per staircase']*exptInfo['08. Number of staircases']
directionOrder = [0,1,0,1]
for trialNum in range(nTrials):
    ## turn off go button after first trial
    if trialNum == 1:
        set_go_button(False,arduino,exptInfo['18. Print arduino messages'])
    
    ## get the isoi for this trial
    if trialNum < nPracTrials:
        isoi = preISOI[trialNum]
    else:
        stairNum = (trialNum - nPracTrials+1) % exptInfo['08. Number of staircases']
        if stairNum == 0: random.shuffle(staircases)
        thisStair = staircases[stairNum]
        print(thisStair.extraInfo['Label'])
        isoi = int(round(thisStair.next()))
    print('ISOI: {}ms' .format(isoi))
    
    ## get the direction for this trial
    directionNum = trialNum % len(directionOrder)
    if directionNum == 0: random.shuffle(directionOrder)
    direction = directionOrder[directionNum]
    
    ## play the stimulus and get the response
    response = load_play_stim(arduino, stimToUse, isoi, 
                exptInfo['07. Probe activation duration (ms)'], direction, 
                exptInfo['16. Device orientation (0 or 1)'],responseRequired = True,
                printMessages = exptInfo['18. Print arduino messages'])
    correct = response == direction
    correctCount += int(correct)
    ## provide feedback
    if exptInfo['14. Provide feedback']:
        feedbackSound = sounds[correct]
        ch = feedbackSound.play()
        print(feedbackText[correct])
        while ch.get_busy():
            pass
    
    ## record the data if not a practice trial
    if trialNum < nPracTrials:
        print('practice')
    else:
        thisStair.addResponse(correct, isoi)
        trialData.write('{},{},{},{}\n' .format(thisStair.extraInfo['Label'],isoi, direction, int(correct)))
    print('{} of {} trials complete\n' .format(trialNum+1, nTrials))
## ----

## -- use quest to estimate threshold --
if exptInfo['09. Number of trials per staircase'] > 0:
    for s in staircases:
        s.saveAsPickle(fileName+'_'+s.extraInfo['Label']) #special python binary file to save all the info
        q = data.QuestHandler(log(exptInfo['06. First ISOI (ms)']), 
                                log(exptInfo['06. First ISOI (ms)']), 
                                pThreshold = 0.82, 
                                nTrials = exptInfo['09. Number of trials per staircase'],
                                grain=0.1, 
                                range=10,
                                minVal = log(exptInfo['11. Min ISOI (ms)']), 
                                maxVal = log(exptInfo['12. Max ISOI (ms)']))
        isois = [log(i) for i in s.intensities]
        q.importData(isois,s.data)
        threshold = exp(q.mean())
        tSD = exp(q.sd())
        print('\n'+s.extraInfo['Label'])
        print('threshold: {}' .format(threshold))
        print('sd: {}' .format(tSD))

        thresholdData.write('{},{},{},{},{},{},{},{},{}\n' .format(threshold,tSD,
                            s.extraInfo['Label'],
                            exptInfo['02. Test number'],
                            exptInfo['01. Participant Code'],
                            len(stimToUse),
                            exptInfo['04. Probe separation (cm)'],
                            exptInfo['05. Stimulation site'],
                            exptInfo['19. Date and time']))
    thresholdData.close()
    trialData.close()
else:
    print('Practice only, no data saved.')
    
print ('\n{} of {} correct ({}%).' .format(correctCount,nTrials,100*correctCount/nTrials))