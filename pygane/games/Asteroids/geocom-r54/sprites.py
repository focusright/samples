import math
import random

import pygame

import lib
from config import conf
from sound import sound
from locals import *

# Needs to be set to a Game object before we can use these sprites
game = None


class SpriteGroup(pygame.sprite.Group):
    '''A container for sprites.'''
    pass


class ShipGroup(pygame.sprite.GroupSingle):
    '''A container for the ship'''

    def __getattr__(self, attr):
        '''If a ship exists, get that attribute, otherwise do nothing.'''
        
        if self:
            return getattr(self.sprite, attr)
        else:
            return lib.none_func
            


class Sprite(pygame.sprite.Sprite):
    '''Abstract sprite class.'''
    
    TRANS = 0xCC # Transparency index
    
    def __init__(self, location, size, r, vel):
        '''Create an abstract ceneterd sprite at location (x, y) with
        size (l, w), direction r, and speed vel (negative for reverse).
        You can give these values 0 if they're unneed except for size.'''
        
        x, y = location
        
        pygame.sprite.Sprite.__init__(self)
        
        self.x, self.y, self.r, self.vel = float(x), float(y), float(r), float(vel)
        
        self.image = pygame.Surface(size)
        
        self.image.set_alpha(self.TRANS)
        self.image.set_colorkey(TRANSPARENT)
        
        self.image.fill(TRANSPARENT)
            
        self.rect = self.image.get_rect(center=location)
        
        game.sprites.add(self)
        
    def update(self):
        '''Move the sprite according to the vel and r properties'''
        
        if self.vel:
        
            self.x = (self.x - self.vel * math.sin(self.r)) % WIDTH
            self.y = (self.y - self.vel * math.cos(self.r)) % game.play_height
            
            self.rect.center = (self.x, self.y)

            
class ExplodingSprite(Sprite):
    
    SHRAPNEL_MIX = 6
    SHRAPNEL_MAX = 16
    
    SHRAPNEL_RADIUS = 3
    
    def kill(self):
        
        self.explode()
        Sprite.kill(self)
        
    def explode(self):
        
        # Explode if we have fancy mode on or we're a ship, but not if sheilds
        # are on, since this can cause massive amounts of shrapnel
        if conf.effects or type(self) is Ship:        
        
            try:
                colour = self.colour
            except AttributeError:
                colour = self.COLOUR
            
            num_particles = random.randint(self.SHRAPNEL_MIX, self.SHRAPNEL_MAX)
            
            for i in range(num_particles):
                Shrapnel((self.x, self.y), colour, self.SHRAPNEL_RADIUS)

            
class Particle(Sprite):
    '''Abstract class for any round object that flies in a straight line off and is
    destroyed on contact with the edge of the screen'''
    
    WIDTH = 0
    
    def __init__(self, location, radius, r, vel, colour):
        
        Sprite.__init__(self, location, (radius*2, radius*2), r, vel)
        
        pygame.draw.circle(self.image, colour, (radius, radius), radius, self.WIDTH)
    
    def update(self):

        # Sprite.update needs to be overwritten because it wraps things to
        # the other side of the screen
        self.x -= self.vel * math.sin(self.r)
        self.y -= self.vel * math.cos(self.r)
        self.rect.center = (self.x, self.y)
        
        # Destroy on boundry
        if (0 > self.x or self.x > (WIDTH - 1)) \
           or (0 > self.y or self.y > (game.play_height - 1)):
            self.kill()


class Shrapnel(Particle):
    
    SPEED_SLOW = 8
    SPEED_FAST = 18
    
    def __init__(self, location, colour, radius):
        
        r = random.uniform(0, math.pi * 2)
        vel = random.randint(self.SPEED_SLOW, self.SPEED_FAST)
        
        Particle.__init__(self, location, radius, r, vel, colour)
        
        game.shrapnel.add(self)
        

class Shot(Particle):
    
    RADIUS = 4
    SHIP_SHOT_COLOUR = (0xFF, 0x00, 0x66)
    ENEMY_SHOT_COLOUR = (0x00, 0xFF, 0x99)
    SPEED = 8
    
    def __init__(self, location, r, speed=None, enemy=False):
        '''Create a shot at location with direction r. Speed and group can be
        set when shots are generated for special purposes'''
        
        if speed is None:
            speed = self.SPEED
            
        if enemy:
            colour = self.ENEMY_SHOT_COLOUR
            group = game.enemies
        else:
            colour = self.SHIP_SHOT_COLOUR
            group = game.shots
        
        Particle.__init__(self, location, Shot.RADIUS, r, speed, colour)
        group.add(self)
        
    def kill(self, r=None): # Here, the r is for when the shot is treated like an enemy
        Particle.kill(self)
        

class Ship(ExplodingSprite):
    
    LENGTH = 30
    SIDES = 10
    COLOUR = WHITE 
    WIDTH = 3
    
    EXHAUST_COLOUR = (0xCC, 0xCC, 0xCC)
    EXHAUST_LIFESPAN = 7
    
    NOSE_LENGTH = 2 * LENGTH / 3 # Precalculated values
    REAR_LENGTH = LENGTH / 6 # Precalulated values
    
    RECT_WIDTH = 2 * NOSE_LENGTH
    
    SPEED = 3.0
    ACCEL = 0.3
    DECEL = 0.06
    
    ROTATION_FACTOR = 50
    
    WARP_OFFSET = 10 # In pixels
    
    SHOT_DELAY = 150.0 # in ms
    SHOT_MAX = 3
    
    RAPID_DELAY = 65.0 # in ms
    
    SHRAPNEL_MIX = 20
    SHRAPNEL_MAX = 30
    
    SHRAPNEL_RADIUS = 12
    
    def __init__(self, location, r):
        
        width = (self.RECT_WIDTH, self.RECT_WIDTH)
        
        Sprite.__init__(self, location, width, r, 0)
        
        self.nose = None # calculated on update
        self.tail = None # calculated on update
        self.last_r = not self.r # start off not equal to r
        self.last_shot = 0.0 # in ms
        self.shots = 0

        for oldship in game.ship:
            oldship.destroy()
        
        game.ship.add(self)        
    
    def update(self):
        
        # This update is quite special and does not need to call Sprite.update()
        
        # If self.r == self.last_r, we don't need to update the sprite image
        if self.r != self.last_r:
            
            self.image.fill(TRANSPARENT)
        
            sin_r = math.sin(self.r)
            cos_r = math.cos(self.r)
            sin_r_point = cos_r # math.sin(self.internal_r + math.pi/2)
            cos_r_point = - sin_r # math.cos(self.internal_r + math.pi/2)
            
            self.nose = Ship.NOSE_LENGTH - Ship.NOSE_LENGTH * sin_r, Ship.NOSE_LENGTH - Ship.NOSE_LENGTH * cos_r
            rear = Ship.NOSE_LENGTH + Ship.REAR_LENGTH * sin_r, Ship.NOSE_LENGTH + Ship.REAR_LENGTH * cos_r
            
            tail_x, tail_y = Ship.NOSE_LENGTH + Ship.LENGTH / 3 * sin_r,  Ship.NOSE_LENGTH + Ship.LENGTH / 3 * cos_r
            #self.tail = tail_x, tail_y
            
            self.p1 = tail_x + Ship.SIDES * sin_r_point, tail_y + Ship.SIDES * cos_r_point
            self.p2 = tail_x - Ship.SIDES * sin_r_point, tail_y - Ship.SIDES * cos_r_point
            
            pygame.draw.polygon(self.image, Ship.COLOUR, (self.p1, rear, self.p2, self.nose), Ship.WIDTH)
            
            self.last_r = self.r
        
        # Warp factor (i. e. we jump to the other side of the screen not on boundry
        # touch, but on boundry touch + WARP_OFFSET)
        if self.vel:
            
            self.x = self.WARP_OFFSET + ((self.x - self.vel * math.sin(self.r) - self.WARP_OFFSET) \
                                    % (WIDTH - 2 * self.WARP_OFFSET))
            self.y = self.WARP_OFFSET + ((self.y - self.vel * math.cos(self.r) - self.WARP_OFFSET) \
                                    % (game.play_height - 2 * self.WARP_OFFSET))
            
            self.rect.center = (self.x, self.y)
            
            self.display_vel = self.vel
        
            # Decelerate
            if self.vel > 0:
                self.vel = max(self.vel - self.DECEL, 0)
            elif self.vel < 0:
                self.vel = min(self.vel + self.DECEL, 0)
        else:
            self.display_vel = self.vel
            
    def forward(self):
        self.vel = min(self.vel + self.ACCEL, self.SPEED)
        if conf.effects:
            self.do_exhaust((self.r + math.pi) % (math.pi * 2))
        
    def reverse(self):
        self.vel = max(self.vel - self.ACCEL, -self.SPEED)
        if conf.effects:
            self.do_exhaust(self.r)
        
    def do_exhaust(self, r):
        for point in (self.p1, self.p2):
            exh_location = self.rect.x + point[0], self.rect.y + point[1]
            Exhaust(exh_location, r, self.EXHAUST_COLOUR, self.EXHAUST_LIFESPAN)
            
    def right(self):   
        self.r = (self.r - math.pi / self.ROTATION_FACTOR) % (math.pi * 2)
        
    def left(self):  
        self.r = (self.r + math.pi / self.ROTATION_FACTOR) % (math.pi * 2)
        
    def shoot(self, rapid=False):
        
        time = pygame.time.get_ticks()
        
        if rapid:
            condition = (time - self.last_shot) > Ship.RAPID_DELAY
        else:
            condition = len(game.shots) < self.SHOT_MAX \
                      and (time - self.last_shot) > Ship.SHOT_DELAY
        
        if condition:
            sound.play('laser')
            shot_location = self.rect.x + self.nose[0], self.rect.y + self.nose[1]
            Shot(shot_location, self.r)
            self.last_shot = time
            
              
    def destroy(self):
        '''Clean death with no explosion'''
        Sprite.kill(self)
        

class Shield(Sprite):
    
    RADIUS = Ship.LENGTH
    WIDTH = 5
    TRANS = Ship.TRANS
    
    DESTROY_FACTOR = 150 #in frames
    
    def __init__(self, colour):
            
        Sprite.__init__(self, (0, 0), (self.RADIUS * 2, self.RADIUS * 2), 0, 0)
        self.kill_me = False
        
        pygame.draw.circle(self.image, colour, (self.RADIUS, self.RADIUS), self.RADIUS)
        pygame.draw.circle(self.image, TRANSPARENT, (self.RADIUS, self.RADIUS), self.RADIUS - self.WIDTH)
        
    def update(self):
        
        if game.ship:
            self.rect.center = game.ship.rect.center
            
            if self.kill_me:
                trans = self.TRANS - int(float(self.TRANS) / float(self.DESTROY_FACTOR) * self.kill_me)
                if trans > 0:
                    self.image.set_alpha(trans)
                    self.kill_me += 1
                else:
                    Sprite.kill(self)
                    game.clear_special()
            
        else:
            Sprite.kill(self)
            
    def kill(self):
        self.kill_me = 1
            

class Exhaust(Sprite):
    
    LENGTH = 3
    WIDTH = 1
    SPEED = 1.5
    
    R_FACTOR = 3
    
    def __init__(self, location, r, colour, lifespan):
        
        self.timer = 0
        self.lifespan = lifespan # in frames
        
        r = r + random.uniform(-math.pi/self.R_FACTOR, math.pi/self.R_FACTOR)
        
        Sprite.__init__(self, location, (self.LENGTH * 2, self.LENGTH * 2), r, self.SPEED)
        
        end = self.LENGTH + self.LENGTH * math.sin(self.r), self.LENGTH + self.LENGTH * math.cos(self.r)
        
        pygame.draw.line(self.image, colour, (self.LENGTH, self.LENGTH), end, self.WIDTH)   
        
    def update(self):
        
        Sprite.update(self)
        
        self.timer += 1
        
        if self.timer > self.lifespan:
            self.kill()
            
            
class Powerup(ExplodingSprite):
    
    RADIUS = 18
    TEXT_SIZE = 24
    EXHAUST_OFFSET = 4
    EXHAUST_LIFESPAN = 12
    
    COLOUR = (0x00, 0xFF, 0x00)
    
    LIFE_MIN = 2250 # in ms
    LIFE_MAX = 5250 
    
    SHRAPNEL_MIX = 15
    SHRAPNEL_MAX = 25
    
    SHRAPNEL_RADIUS = 7
    
    def __init__(self, location):
        
        life = random.uniform(self.LIFE_MIN, self.LIFE_MAX)
        game.set_timer(life, self.explode_and_kill)
        
        self.type, letter = random.choice([(k, v['code']) for k, v in game.SPECIAL_ITEMS.items() \
                                           if v.has_key('code')])
        
        width = self.RADIUS * 2
        ExplodingSprite.__init__(self, location, (width, width), 0, 0)
        
        pygame.draw.circle(self.image, self.COLOUR, (self.RADIUS, self.RADIUS),
                           self.RADIUS)
        
        text = lib.render_text(letter, self.TEXT_SIZE, TRANSPARENT)
        text_width, text_height = text.get_size()
        self.image.blit(text, (width/2 - text_width/2, width/2 - text_height/2))
        
        game.powerups.add(self)
        
    def update(self):
        
        #if (pygame.time.get_ticks() - self.created_time) > self.life:
        #    # Called after a timeout
        #    ExplodingSprite.kill(self)
        #    
        #else:
        r = random.uniform(0, math.pi * 2)
        exh_location = self.x + (self.RADIUS + self.EXHAUST_OFFSET) * math.sin(r), \
                     self.y + (self.RADIUS + self.EXHAUST_OFFSET) * math.cos(r)
        r = (r + math.pi) % (2 * math.pi)
            
        Exhaust(exh_location, r, self.COLOUR, self.EXHAUST_LIFESPAN)
        
    def explode_and_kill(self):
        if self.alive():
            self.explode()
            self.kill()
        
    def kill(self):
        # no exposion here
        Sprite.kill(self)
            

class Enemy(ExplodingSprite):
    
    SPEED_SLOW = 1 # Override me if desired
    SPEED_FAST = 4 # Override me if desired
    
    LIVES = 1
    
    def __init__(self, location, radius):
        
        self.lives = self.LIVES
        self.colour = self.COLOUR_START
        
        r = random.uniform(0, math.pi * 2)
        vel = random.uniform(self.SPEED_SLOW, self.SPEED_FAST)
        
        Sprite.__init__(self, location, (radius * 2, radius * 2), r, vel)
        
        game.enemies.add(self)
        
    def kill(self, r):
        
        self.lives -= 1
        
        if self.lives == 0:        
            ExplodingSprite.kill(self)
        else:
            self.explode()
            colour = [0, 0, 0]
            for i in range(3):
                start = self.COLOUR_START[i]
                end = self.COLOUR_END[i]
                colour[i] = start + int(float(end - start)/float(self.LIVES - 1) * (self.LIVES - self.lives))
            self.colour = tuple(colour)
        
    
class Square(Enemy):
    
    COLOUR_START = (0x22, 0x22, 0xFF)
    
    INITIAL_RADIUS = 34
    BREAK_UP = ((23, 2), (14, 4))
    
    ROTATION_FACTOR_MAX = 30 # the lower here the faster, minimum = not moving
    
    def __init__(self, location, radius=False, next=False):
        
        if not radius:
            radius = self.INITIAL_RADIUS
            next = self.BREAK_UP            
        
        Enemy.__init__(self, location, radius)    
        
        self.radius = radius
        self.next = next
        
        self.internal_r = 0.0
        self.internal_s = random.uniform(0, math.pi/self.ROTATION_FACTOR_MAX)
      
        
    def update(self):
        
        self.image.fill(TRANSPARENT)
        
        sin_r = math.sin(self.internal_r)
        cos_r = math.cos(self.internal_r)
        sin_r_top = cos_r #math.sin(self.internal_r + math.pi/2)
        cos_r_top = - sin_r #math.cos(self.internal_r + math.pi/2)
        
        p1 = self.radius - self.radius * sin_r, self.radius - self.radius * cos_r
        p2 = self.radius - self.radius * sin_r_top, self.radius - self.radius * cos_r_top
        p3 = self.radius + self.radius * sin_r, self.radius + self.radius * cos_r
        p4 = self.radius + self.radius * sin_r_top, self.radius + self.radius * cos_r_top
        
        # For a subclass
        self.points = (p1, p2, p3, p4)
        
        pygame.draw.polygon(self.image, self.colour, self.points)
        
        self.internal_r = (self.internal_r + self.internal_s) % (math.pi * 2)
        
        Enemy.update(self)
        
    def kill(self, r):
        
        Enemy.kill(self, r)
        
        if self.next and not self.alive():
        
            next = False
            radius, amount = self.next[0]
            
            if len(self.next) > 1:
                next = self.next[1:]
            
            for i in range(amount):
                self.__class__((self.x, self.y), radius, next)
        

class HardenedSquare(Square):
    '''A tougher square.'''
    
    # Oh, the beauty of class hierarchy
    COLOUR_START = (0x00, 0x99, 0xFF) #(0xCC, 0xCC, 0xCC)
    COLOUR_END = (0xCC, 0xFF, 0xFF) #(0x66, 0x66, 0x66)
    
    LIVES = 3
    
    
        
class Circle(Enemy):
    
    COLOUR_START = (0xFF, 0x66, 0x99)
    COLOUR_END = (0x99, 0x66, 0x99)
    LIVES = 3
    
    SPEED_SLOW = 2.0
    SPEED_FAST = 4.5
    
    RADIUS_MIN = 10
    RADIUS_MAX = 30
    
    def __init__(self, location):
        
        self.radius = random.randint(self.RADIUS_MIN, self.RADIUS_MAX)
    
        Enemy.__init__(self, location, self.radius)
        
        self.redraw = True
        
    def update(self):
        
        if self.redraw:
            
            pygame.draw.circle(self.image, self.colour, (self.radius, self.radius), self.radius)
            
            self.redraw = False
            
        Enemy.update(self)
        
    def kill(self, r):
        
        self.redraw = True
        self.r = r
        Enemy.kill(self, r)
        

class HardenedCircle(Circle):
    
    COLOUR_START = (0x99, 0x00, 0x99)
    COLOUR_END = (0x99, 0x00, 0x00)
    LIVES = 6
    
    SPEED_SLOW = 2.0
    SPEED_FAST = 4.5
    
    def kill(self, r):
        new_r = (r + math.pi) % (2 * math.pi)
        Circle.kill(self, new_r)
    
            

class Triangle(Enemy):
    
    RADIUS = 28
    #LENGTH = math.sqrt((RADIUS ** 2 + (RADIUS/2) ** 2))
    COLOUR_START = (0x99, 0xFF, 0x33)
    COLOUR_END = (0x99, 0x99, 0x33)
    LIVES = 3
    
    SPEED_SLOW = 1.4
    SPEED_FAST = 2.0
    
    ACCURACY_FACTOR = 6
    ROTATION_FACTOR = 150
    
    def __init__(self, location):
        
        length = int(math.ceil(math.sqrt((self.RADIUS ** 2 + (self.RADIUS/2) ** 2))))
        
        Enemy.__init__(self, location, self.RADIUS)
        
    def update(self):
        
        p1 = self.RADIUS - self.RADIUS * math.sin(self.r), self.RADIUS - self.RADIUS * math.cos(self.r)
        p2 = self.RADIUS - self.RADIUS * math.sin(self.r + 2*math.pi/3), self.RADIUS - self.RADIUS * math.cos(self.r + 2*math.pi/3)
        p3 = self.RADIUS + self.RADIUS * math.sin(self.r)/4, self.RADIUS + self.RADIUS * math.cos(self.r)/4
        p4 = self.RADIUS - self.RADIUS * math.sin(self.r + 4*math.pi/3), self.RADIUS - self.RADIUS * math.cos(self.r + 4*math.pi/3)

        self.nose = p1 # For ShootingTriangle
        
        self.image.fill(TRANSPARENT)
        pygame.draw.polygon(self.image, self.colour, (p1, p2, p3, p4))
        
        if game.ship.sprite:
        
            r_to_ship = self.r_to_ship()
            
            pointing_r = (r_to_ship - self.r) % (2*math.pi)
            self.pointing_r = pointing_r
            
            if not ((math.pi - math.pi/self.ACCURACY_FACTOR) < pointing_r < (math.pi + math.pi/self.ACCURACY_FACTOR)):        
                if pointing_r <= math.pi:
                    r = (self.r - math.pi/self.ROTATION_FACTOR)
                else:
                    r = (self.r + math.pi/self.ROTATION_FACTOR)
                self.r = r % (2 * math.pi)
            
        Enemy.update(self)
    
    def r_to_ship(self):
        # Precondition - ship_group.sprite is a ship
        return math.atan2(game.ship.sprite.x - self.x,
                          game.ship.sprite.y - self.y) % (2*math.pi)
            
    def kill(self, r):
        
        if game.ship.sprite:
            self.r = (self.r_to_ship() + random.uniform(-math.pi/self.ROTATION_FACTOR, math.pi/self.ROTATION_FACTOR)) % (2 * math.pi)
            
        Enemy.kill(self, r)


class ShootingTriangle(Triangle):
    
    COLOUR_START = (0xCC, 0x66, 0x33)
    COLOUR_END = (0x66, 0x00, 0x33)
    LIVES = 5
    
    SPEED_SLOW = 1.6
    SPEED_FAST = 1.8
    
    ACCURACY_FACTOR = 16
    ROTATION_FACTOR = 175
    
    SHOT_DELAY = 500 #in ms
    SHOT_FREQUENCY = 75
    SHOT_SPEED = 5
    
    def __init__(self, location):
        
        self.busy = False
        
        Triangle.__init__(self, location)
    
    def update(self):
        
        Triangle.update(self)
        
        if game.ship.sprite and not self.busy \
           and random.randint(1, self.SHOT_FREQUENCY) == self.SHOT_FREQUENCY:
            shot_location = self.rect.x + self.nose[0], self.rect.y + self.nose[1]
            Shot(shot_location, self.r, self.SHOT_SPEED, True)
            self.busy = True
            game.set_timer(self.SHOT_DELAY, self.mark_not_busy)
            
            
    def mark_not_busy(self):
        self.busy = False
        
        
class Pentagram(Enemy):
    
    COLOUR_START = (0xFF, 0x00, 0x33)
    COLOUR_END = (0xFF, 0xCC, 0x33)
    LIVES = 10
    
    INNER_ARM_LENGTH = 12
    OUTER_ARM_LENGTH = 30
    
    ROTATION_FACTOR_MAX = 90 # the lower here the faster, minimum = not moving
    
    SHOT_DELAY = 500 #in ms
    SHOT_FREQUENCY = 75
    SHOT_SPEED = 5
    
    def __init__(self, location):
        
        Enemy.__init__(self, location, self.OUTER_ARM_LENGTH)
        
        self.busy = False
        self.internal_r = 0.0
        self.internal_s = random.uniform(0, math.pi/self.ROTATION_FACTOR_MAX)
        
    def update(self):
        
        points = []
        
        for p_num in range(10):

            if p_num % 2:
                length = self.INNER_ARM_LENGTH
            else:
                length = self.OUTER_ARM_LENGTH
            
            p = self.OUTER_ARM_LENGTH - length * math.sin(self.internal_r + p_num * math.pi/5), \
              self.OUTER_ARM_LENGTH - length * math.cos(self.internal_r + p_num * math.pi/5)
            
            points.append(p)
            
        self.image.fill(TRANSPARENT)
        pygame.draw.polygon(self.image, self.colour, points)
        
        self.internal_r = (self.internal_r + self.internal_s) % (math.pi * 2)
        
        if game.ship.sprite and not self.busy \
           and random.randint(1, self.SHOT_FREQUENCY) == self.SHOT_FREQUENCY:
            for p_num in range(0, 10, 2):
                shot_loc = self.rect.x + points[p_num][0], self.rect.y + points[p_num][1]
                shot_r = self.internal_r + p_num * math.pi/5
                Shot(shot_loc, shot_r, self.SHOT_SPEED, True)
                self.busy = True
            game.set_timer(self.SHOT_DELAY, self.mark_not_busy)
        
        Enemy.update(self)
    
    def kill(self, r):
        self.r = r
        Enemy.kill(self, r)
        
    def mark_not_busy(self):
        self.busy = False
        
        
