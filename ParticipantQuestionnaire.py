from psychopy import core, gui, data
import time, os#, numpy, random
#from math import *

## -- get input from experimenter --

participantInfo = {'01. Participant Code':'P00', 
            '02. Experimental Group':['','neuropathic','older','younger'], 
            '03. Age':0, 
            '04. Sex':['Male','Female'], 
            '05. Height (cm)':0, 
            '06. Weight (kg)':0,
            '07. Probe activation duration':5,
            '08. Smoking status':['','never','previous','current'], 
            '09. Neuropathy diagnosis?':[False,True], 
            '10. Diabetes':['none','type1','type2'],
            '11. Ulceration present/history (if neuropathic)':'no ulceration',
            '12. Folder for saving data':'test'}
participantInfo['13. Date and time']= data.getDateStr(format='%Y-%m-%d_%H-%M-%S') #add the current time
dlg = gui.DlgFromDict(participantInfo, title='Participant details', fixed=['13. Date and time'])
if dlg.OK:
    pass
else:
    core.quit() # the user hit cancel so exit

nssInfo = {'14A. Unsteadiness in gait':[False,True],
        '14B. Pain burning or aching of the feet or legs':[False,True],
        '14C. Prickling sensation of the feet or legs':[False,True],
        '14D. Numbness in feet or legs':[False,True]}
dlg = gui.DlgFromDict(nssInfo, title='Neuropathy Symptom Score')
if dlg.OK:
    nssResponses = [int(i=='True') for i in nssInfo.values()]
    nss = sum(nssResponses)
    participantInfo['14. Neuropathy Symptom Score (0-4)'] = nss
    participantInfo.update(nssInfo)

classicTests = {'15A. Monofilament arch (grams)':0,
                '15B. Monofilament leg (grams)':0,
                '16A. Neurothesiometer arch (Volts)':0,
                '16B. Neurothesiometer leg (Volts)':0,
                '17. Nerve conduction velocity (mps)':0}
dlg = gui.DlgFromDict(classicTests, title='Classic tests')
if dlg.OK:
    participantInfo.update(classicTests)

## -- make folder/files to save data --
dataFolder = './'+participantInfo['12. Folder for saving data']+'/'
if not os.path.exists(dataFolder):
    os.makedirs(dataFolder)
participantData = open(dataFolder + participantInfo['01. Participant Code'] + '_participantData.csv', 'w')
for (k,v) in sorted(participantInfo.items()):
   participantData.write('{},{}\n'.format(k,v))
participantData.close()