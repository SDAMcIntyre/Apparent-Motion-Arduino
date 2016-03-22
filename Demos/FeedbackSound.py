import pygame, random

# setup
pygame.mixer.pre_init() #frequency=44100, size=-16, channels=2, buffer=4096
pygame.init()
sounds = [pygame.mixer.Sound('../incorrect.wav'),pygame.mixer.Sound('../correct.wav')]

#correct = False #random.sample([0,1],1)[0]

# play the sound
for thisSound in sounds:
#thisSound = sounds[correct]
    ch = thisSound.play()
    while ch.get_busy():
        pass 
    pygame.time.delay(100)

# finish
pygame.quit()
