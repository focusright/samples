
import pygame

from locals import *

from config import conf
import lib

class __Sound(object):
    
    def __init__(self):
        
        self._sounds = {}
        
        # Do we have support?
        if pygame.mixer.get_init():
            self._supported = True
        else:
            self._supported = False
            return
        
        for filename in SOUND_FILES:
            sound = filename.rsplit('.', 1)[0]
            self._sounds[sound] = pygame.mixer.Sound(lib.filename(filename))
        
    def play(self, sound, times=0):
        if self._supported and conf.sound:
            try:
                self.stop(sound)
                self._sounds[sound].play(times)
            except KeyError(e):
                raise AttributeError("Invalid sound %s." % sound)
        
    def stop(self, sound):
        if self._supported and conf.sound:
            try:
                self._sounds[sound].stop()
            except KeyError(e):
                raise AttributeError("Invalid sound %s." % sound)

sound = __Sound()
