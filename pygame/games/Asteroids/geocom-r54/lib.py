
import os
import random
import pygame
import sys

from locals import *

if pygame.version.vernum < (1, 8):
    
    def detect_collision(sprite1, sprite2):
        '''Detect a collision between two sprites (pre pygame 1.8)'''
        
        # XXX - There may be a faster way to do this. There definitely is with
        # Pygame 1.8 (released March 29th, 2008). This will work for now until
        # I've done some profiling.
        
        shared = sprite1.rect.clip(sprite2.rect)
        
        sp1_x, sp1_y = shared.x - sprite1.rect.x, shared.y - sprite1.rect.y
        sp2_x, sp2_y = shared.x - sprite2.rect.x, shared.y - sprite2.rect.y
        
        for x in xrange(0, shared.width):
            for y in xrange(0, shared.height):
                if sprite1.image.get_at((x + sp1_x, y + sp1_y))[0:3] != TRANSPARENT \
                   and sprite2.image.get_at((x + sp2_x, y + sp2_y))[0:3] != TRANSPARENT:
                        for x in xrange(0, shared.width):
                            return True
        return False
    
else:
    
    def detect_collision(sprite1, sprite2):
        '''Detect a collision between two sprites (pygame 1.8 or later)'''
        
        sp1_mask = pygame.mask.from_surface(sprite1.image, 0)
        sp2_mask = pygame.mask.from_surface(sprite2.image, 0)
        
        offset = sprite2.rect.x - sprite1.rect.x, sprite2.rect.y - sprite1.rect.y
        
        return bool(sp1_mask.overlap(sp2_mask, offset))
    

__font_objs = {}

def __get_font(size):
    
    if size not in __font_objs:
        __font_objs[size] = pygame.font.Font(filename(FONT_FILENAME), size)
        
    return __font_objs[size]
    

def render_text(text, size, colour=WHITE):
    '''Render some text'''
    
    return __get_font(size).render(text, True, colour)

def get_text_height(size):
    '''Check the height of a certain size of text'''
        
    return __get_font(size).get_height()

def get_text_width(text, size):
    '''Check the width of a certain size of text'''
    return __get_font(size).size(text)[0]


def draw_background(height=HEIGHT):
    '''Render the background with height (defaults to screen height).'''
    background = pygame.surface.Surface((WIDTH, height))
    background.fill(BACKGROUND)
    
    # Fill with 1000 stars
    for star in range(1000):
        x_pos = random.randint(0, WIDTH - 1)
        y_pos = random.randint(0, height - 1)
        if (star % 10) == 0:
            # 1 in 10 have a chance of not being white
            colour = random.choice(((0xFF, 0, 0), (0, 0, 0xFF), (0, 0xFF, 0)))
            background.set_at((x_pos, y_pos), colour) # 1 in 15 are red
        else:
            background.set_at((x_pos, y_pos), WHITE)
            
    return background


def filename(name):
    '''Get the path of a data file'''
    
    # Is this The Right Way(tm)?

    # Find out where we are, or in the case of an exe
    if hasattr(sys, 'frozen'):
        basedir = sys.prefix
    else:
        basedir = sys.path[0]

    filename = os.path.join(basedir, DATA_DIRNAME, name)
    
    if not os.access(filename, os.F_OK | os.R_OK):
        print("Could not find file '%s'." % filename)
        raise SystemExit
    
    return filename


def none_func(*args, **kwargs):
    '''Do nothing, gracefully.'''
    pass
