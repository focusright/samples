import atexit
import os

import pickle    
from locals import *

class __Config(object):
    
    CONFIGFILE = ".geocom"
    
    # This is essentially the API
    DEFAULT = {'conf_version': 2, # increment on update of the conf interface
               'highscores': [], # (name, score) pairs
               'psyco': True,
               'debug': False,
               'effects': True,
               'fullscreen': False,
               'sound': True}
    
    MAX_NAME_LEN = 25
    
    def __init__(self):
        
        self.__dict__['filename'] = os.path.join(os.path.expanduser('~'), self.CONFIGFILE)
        
        try:
        
            if os.access(self.filename, os.F_OK):
                
                f = open(self.filename, 'rb')
                data = pickle.load(f)
                f.close()
                
                # Make sure we're compatible
                if data['conf_version'] != self.DEFAULT['conf_version']:
                    raise Exception
                
                for key, value in self.DEFAULT.iteritems():
                    # Recover lost data or data from an old version
                    if not data.has_key(key):
                        data[key] = value
                
            else:
                raise Exception # set default, below
            
        except:
            data = self.DEFAULT
        
        self.__dict__['_data'] = data
        
    def _save(self):
        
        # Called on exit by registering with atexit.regster() 
        
        try:
            pickle
        except NameError:
            import pickle
        
        try:
            f = open(self.filename, 'wb')
            pickle.dump(self._data, f)
            f.close()
        except:
            pass
    
    def __getattr__(self, name):
        try:
            return self.__dict__['_data'][name]
        except KeyError(e):
            raise AttributeError(e)
        
    def __setattr__(self, name, value):
        
        if name in self.__dict__['_data']:
            self.__dict__['_data'][name] = value
        else:
            raise AttributeError(name)
        
    def __delattr__(self, name):
        raise AttributeError(name)
        
    def is_highscore(self, score):
        '''Will this score make it in to the high score list?'''
        
        if len(self.highscores) < HIGHSCORES_AMOUNT:
            return True
        
        return score > self.highscores[-1][1]
    
    def register_highscore(self, name, score):
        '''Register a highscore'''
        
        name = name[:self.MAX_NAME_LEN]
        
        self.highscores.append((name, score))
        # Sort the list
        self.highscores.sort(lambda a, b: cmp(b[1], a[1]))
        # Truncate to HIGHSCORES_AMOUNT items
        del self.highscores[HIGHSCORES_AMOUNT:]

        
conf = __Config()

# Register conf._save() at exit
atexit.register(conf._save)
