from config import conf
from functools import cmp_to_key

if conf.psyco:
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

import os
import math
import random

os.environ["SDL_VIDEO_CENTERED"] = "1"

import pygame

pygame.mixer.pre_init(44100, -16, 2, 1024 * 3) #pygame crackle fix for win32
pygame.init()

import lib
import sprites

from menu import Menu
from sound import sound

from locals import *

class Game(object):
    
    STARTING_LIVES = 3    
    PANEL_FONT_SIZE = 14
    PANEL_SCORE_TEXT = "Score: %d"
    
    SHIELD_INITIAL_TIMEOUT = 250 # Plus the frames in sprites.Shield.FADEAWAY
    SHIELD_TIMEOUT = 6500
    RAPID_FIRE_TIMEOUT = 8500
    
    DEATH_DELAY = 1500
    
    SHIELD_INITIAL = 1
    SHIELD = 2
    RAPID_FIRE = 3
    BURST = 4
    ONEUP = 5
    
    CARGO_EMPTY = 'Empty'
    
    # Special Item Codes
    SPECIAL_ITEMS = {SHIELD_INITIAL: {'name': 'Initial Shields', 'delay': 250, 'colour': sprites.Ship.COLOUR},
                     SHIELD: {'code': 'S', 'name': 'Shields', 'delay': 5000, 'colour': sprites.Shot.SHIP_SHOT_COLOUR},
                     RAPID_FIRE: {'code': 'R', 'name': 'Rapid Fire', 'delay': 8500},
                     BURST: {'code': 'B', 'name': 'Burst', 'delay': 1500}}#,
#                     ONEUP: {'code': '1', 'name': CARGO_EMPTY}}
    
    def __init__(self):
        
        self.set_screen()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(GAME)
        
        self.clock = pygame.time.Clock()
        
        panel_height = (lib.get_text_height(self.PANEL_FONT_SIZE) + 1)
        self.play_height = HEIGHT - panel_height 

        self.panel_img = pygame.surface.Surface((WIDTH, panel_height))
        self.panel_img.fill(BACKGROUND)
        pygame.draw.line(self.panel_img, WHITE, (0, 0), (WIDTH - 1, 0))
        
        self.panel_y = self.play_height + 1
        
        self.panel_score_x = WIDTH - lib.get_text_width(self.PANEL_SCORE_TEXT % 999999999, \
                                                        self.PANEL_FONT_SIZE) - 2
        
        # Make sprites.py aware of us
        sprites.game = self
        
    
    def set_screen(self):
        '''Sets (resets) the self.screen variable with the proper fullscreen'''

        if conf.fullscreen:
            fullscreen = pygame.FULLSCREEN
        else:
            fullscreen = 0
            
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), fullscreen)

        
    def begin(self):
        
        menu = Menu(self)
        
        while True:
            
            # Display the menu
            menu.show()
            
            # Start a new game
            self.stage = 1
            self.score = 0
            self.lives = self.STARTING_LIVES
            
            # Create groups
            self.sprites = sprites.SpriteGroup()
            self.enemies = sprites.SpriteGroup()
            self.powerups = sprites.SpriteGroup()
            self.shots = sprites.SpriteGroup()
            self.shrapnel = sprites.SpriteGroup()
            
            # One item only group for the ship, passed attr's down to the ship
            # if it cat
            self.ship = sprites.ShipGroup()
            
            # Cargo bay is originally empty
            self.cargo_bay = False
            
            # There are originally no timers
            self._timers = []
            
            sound.play("music", -1)
            
            # Returns false on game over
            while self.play():
                pass
            
            sound.stop("music")
     
            
    def play(self):
        ''' Returns false on game over, true on end of level'''

        self.background = lib.draw_background(self.play_height)           
        secret, endgame = False, False
        self.kills, self.deaths = 0, 0
        
        self.spawn_ship()
        
        self.ship_move = {}
        for move in ('forward', 'reverse', 'right', 'left', 'shoot'):
            self.ship_move[move] = False
            
        enemies = [sprites.Triangle, sprites.Square, sprites.Circle, \
                   sprites.ShootingTriangle, sprites.HardenedSquare, \
                   sprites.HardenedCircle, sprites.Pentagram]
        
        while True:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    key_down = (event.type == pygame.KEYDOWN)
                    if event.key == pygame.K_UP:
                        self.ship_move['forward'] = key_down
                    elif event.key == pygame.K_DOWN:
                        self.ship_move['reverse'] = key_down
                    elif event.key == pygame.K_LEFT:
                        self.ship_move['left'] = key_down
                    elif event.key == pygame.K_RIGHT:
                        self.ship_move['right'] = key_down
                    elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL or event.key == pygame.K_SPACE:
                        self.ship_move['shoot'] = key_down
                    elif event.key == pygame.K_s:
                        secret = key_down
                    elif key_down and event.key == pygame.K_SPACE:
                        if not self.special:
                            self.do_special()
                    elif key_down and event.key == pygame.K_TAB:
                        conf.fullscreen = not conf.fullscreen
                        self.set_screen()
                    elif key_down and event.key in range(pygame.K_1, pygame.K_1 + len(enemies)):
                        if conf.debug:
                            x_pos = random.randint(0, WIDTH - 1)
                            y_pos = random.randint(0, self.play_height - 1)
                            enemies[int(event.unicode) - 1]((x_pos, y_pos))
                    elif key_down and event.key == pygame.K_d:
                        if not conf.fullscreen and not conf.psyco and conf.debug:
                            import pdb
                            pdb.set_trace()
                    elif key_down and event.key == pygame.K_ESCAPE:
                        sound.play('explode')
                        self.ship.kill()
                        self.animate_until(0, self.shrapnel, self.shots)
                        pygame.event.clear()
                        return False                        
                    elif key_down and event.key == pygame.K_z:
                        if conf.debug:
                            x_pos = random.randint(50, WIDTH - 51)
                            y_pos = random.randint(50, self.play_height - 51)
                            sprites.Powerup((x_pos, y_pos))
                    elif key_down and event.key == pygame.K_LSHIFT:
                        if conf.debug:
                            self.spawn_ship()
            
            self.draw()
            ship = self.ship.sprite
                    
            if ship:
                for move, value in self.ship_move.items():
                    if value:
                        getattr(ship, move)()
                        
                if self.special == self.RAPID_FIRE:
                    ship.shoot(True)
                    
                if secret or self.special == self.BURST:
                    num_particles = random.randint(2, 5)
                    for i in xrange(num_particles):
                        r = random.uniform(0, math.pi * 2)
                        speed = random.randint(6, 16)
                        sprites.Shot((ship.x, ship.y), r, speed)
                        
            collisions = pygame.sprite.groupcollide(self.shots, self.enemies, False, False)
            
            # Shot -> enemy collisions
            for shot, enemy in collisions.items():
                enemy = enemy[0] # we only want one hit enemy if there are multiple
                if lib.detect_collision(shot, enemy):
                    if enemy.alive():
                        enemy.kill(shot.r)
                        sound.play('explode')
                        if not enemy.alive():
                            self.kills += 1
                    shot.kill()
               
            # Ship -> enemy collisions
            if ship and self.special not in (self.SHIELD_INITIAL, self.SHIELD):
                for enemy in pygame.sprite.spritecollide(ship, self.enemies, False):
                    if lib.detect_collision(ship, enemy):
                        enemy.kill(ship.r)
                        if not enemy.alive():
                            self.kills += 1
                        ship.kill()
                        sound.play('explode')
                        self.deaths += 1
                        self.force_timers()
                        ship = False
                        if not conf.debug:
                            self.set_timer(1500, self.spawn_ship)
                        break
            
            # Regular shield -> enemy collision (i. e. not initial shields)
            if ship and self.special == self.SHIELD:
                for enemy in pygame.sprite.spritecollide(self.shield, self.enemies, False):
                    if lib.detect_collision(self.shield, enemy):
                        enemy.kill(ship.r)
            
            # Ship -> powerup collision
            if ship:
                for powerup in pygame.sprite.spritecollide(ship, self.powerups, False):
                    if lib.detect_collision(ship, powerup):
                        powerup.kill()
                        if powerup.type == self.ONEUP:
                            self.lives += 1
                        else:
                            self.cargo_bay = powerup.type
            
            if not conf.debug:
                num_enemies = len(self.enemies)
            
                if (num_enemies == 0) or (num_enemies < 3 and (random.randint(0, 350) == 0)):
                    x_pos = random.randint(0, WIDTH - 1)
                    y_pos = random.randint(0, self.play_height - 1)
                    random.choice(enemies)((x_pos, y_pos))
                    
                if (len(self.powerups) == 0) and (random.randint(0, 1500) == 0):
                    x_pos = random.randint(50, WIDTH - 51)
                    y_pos = random.randint(50, self.play_height - 51)
                    sprites.Powerup((x_pos, y_pos))

    def draw(self):
        '''Draw and update the game'''
        
        self._check_timers()        
        
        self.screen.blit(self.background, (0, 0))
        
        self.sprites.update()
        self.sprites.draw(self.screen)
        
        self.draw_panel()
        
        pygame.display.update()
        self.clock.tick(FRAME_RATE)

    @staticmethod
    def cmp(a, b):
        return (a[0] > b[0]) - (a[0] < b[0]) 

    def set_timer(self, time, callback, *args, **kwargs):
        '''Set a timer to call the function callback after time ms have elapsed.'''
        self._timers.append((pygame.time.get_ticks() + time, callback, args, kwargs))
        #self._timers.sort(lambda x, y: cmp(x[0], y[0]))
        self._timers.sort(key=cmp_to_key(Game.cmp))
        
    def _check_timers(self):
        '''Check timers and run callbacks if one has expired.'''
        time = pygame.time.get_ticks()
        while self._timers and (self._timers[0][0] <= time):
            expire_time, callback, args, kwargs = self._timers.pop(0)
            callback(*args, **kwargs)
            
    def force_timers(self):
        '''Force timers to finish'''
        while self._timers:
            time, callback, args, kwargs = self._timers.pop()
            callback(*args, **kwargs)

    def animate_until(self, time, *groups):
        '''Animate for the following amount of time and/or until groups are
        empty (calculated concurrently).'''
        
        stop_time = pygame.time.get_ticks() + time

        while True:
        
            self.draw()
            
            if pygame.time.get_ticks() >= stop_time:
                for group in groups:
                    if group:
                        break
                else:
                    return
        
                
    def draw_panel(self):
        
        self.screen.blit(self.panel_img, (0, self.play_height))
        
        #score_text = self.PANEL_SCORE_TEXT % 2313242
        
        
        #score = lib.render_text(score_text, self.PANEL_FONT_SIZE)
        #self.screen.blit(score, (self.panel_score_x, self.panel_y))
        
        cargo_bay_text = self.CARGO_EMPTY
        
        if self.cargo_bay:
            cargo_bay_text = self.SPECIAL_ITEMS[self.cargo_bay]['name']
        
        # Debugging
        sprites = lib.render_text("[FPS: %.3f] [Sprites: %d] [Enemies: %d] [Cargo bay: %s]" \
                                  % (self.clock.get_fps(), len(self.sprites),
                                     len(self.enemies), cargo_bay_text), self.PANEL_FONT_SIZE)
        self.screen.blit(sprites, (2, self.panel_y))
        
        info = lib.render_text("You've killed %d baddies in %d deaths" % (self.kills, self.deaths), \
                               self.PANEL_FONT_SIZE)
        
        self.screen.blit(info, (WIDTH - info.get_width() - 2, self.panel_y))
        
    def spawn_ship(self):
        sprites.Ship((WIDTH/2, self.play_height/2), random.uniform(0, 2*math.pi))
        self.clear_special()
        self.do_special(self.SHIELD_INITIAL)
    
    def clear_special(self):
        '''Sets self.special = False, useful as a timer callback function.'''
        self.special = False
        
    def do_special(self, item=None):
        '''Perform a special move, if none is specified, take one from the cargo
        bay. If the cargo bay is empty, do nothing.'''
        
        if item is None:
            item = self.cargo_bay
            self.cargo_bay = False
            
        if not self.special and item:
            
            self.special = item            

            # Special Cases
            if self.special in (self.SHIELD_INITIAL, self.SHIELD):
                self.shield = sprites.Shield(self.SPECIAL_ITEMS[self.special]['colour'])
                self.set_timer(self.SPECIAL_ITEMS[self.special]['delay'], self.shield.kill)
            else:
                # General case
                self.set_timer(self.SPECIAL_ITEMS[self.special]['delay'], self.clear_special)
                
 
        
def main():
    '''Play the game (currently wrapped for profiling purposes)'''
    g = Game()
    g.begin()
        
if __name__ == '__main__':
    
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == 'profile':
        import hotshot
        prof = hotshot.Profile("profile.log")
        prof.runcall(main)
    else:
        main()
