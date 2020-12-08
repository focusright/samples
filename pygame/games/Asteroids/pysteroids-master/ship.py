import pygame
import colors
import math
from vectors import Vector2D
from polygon import Polygon
from helpers import *

class Ship(Polygon) :

	def __init__(self, x, y, screen) :
		self.screen = screen
		self.pos = Vector2D(x, y)
		self.size = 18
		self.color = colors.green
		self.rotation = 0
		self.points = [
						(-self.size, self.size),
						(0, self.size / 3),
						(self.size, self.size),
						(0, -self.size)
					  ]
		self.translate((self.pos.x, self.pos.y))
		self.velocity = Vector2D(0, 0)
		self.projectiles = []

	def shoot(self) :
		p = Projectile(self.pos.x, self.pos.y, self.rotation, self.screen)
		self.projectiles.append(p)
		
	def turn(self, dir) :
		turn_rate = 4
		if dir == 'left' :
			deg = -turn_rate
		elif dir == 'right' :
			deg = turn_rate
		else :
			deg = 0

		self.rotation += deg
		self.rotate((self.pos.x, self.pos.y), deg)

		if self.rotation > 360 :
			self.rotation -= 360
		elif self.rotation < 0 :
			self.rotation += 360

		#print('HDG: ' + str(self.rotation))

	def boost(self) :
		#print(self.velocity.x, ',', self.velocity.y)
		force = Vector2D().create_from_angle(self.rotation, 0.1, True)

		#Limits the speed
		if (((self.velocity.x <= 4) and (self.velocity.x >= -4)) 
			or 
			((self.velocity.y <= 4) and (self.velocity.y >= -4))) :
			self.velocity.add(force)
		
		#print('Velocity: ' + str(self.velocity.x) + ',' + str(self.velocity.y))

	def update(self) :
		#Adds friction
		f = 0.98
		self.velocity.mult((f, f))

		# Resets ship possition when it's out of the screen
		if self.pos.x > (self.screen.get_width() + self.size) :
			#print('COLLIDED RIGHT')
			self.pos.x -= self.screen.get_width() + self.size
			self.translate((-(self.screen.get_width() + self.size), 0))
		elif self.pos.x < -self.size :
			#print('COLLIDED LEFT')
			self.pos.x += self.screen.get_width() + self.size
			self.translate(((self.screen.get_width() + self.size), 0))
		if self.pos.y > (self.screen.get_height() + self.size) :
			#print('COLLIDED BOTTOM')
			self.pos.y -= self.screen.get_height() + self.size
			self.translate((0, -(self.screen.get_height() + self.size)))
		elif self.pos.y < -self.size :
			#print('COLLIDED TOP')
			self.pos.y += self.screen.get_height() + self.size
			self.translate((0, (self.screen.get_height() + self.size)))

		self.pos.x += self.velocity.x #TODO: simplify using V2D add function
		self.pos.y += self.velocity.y

		self.translate(self.velocity.tuple())

		#Update projectiles that have been shot
		offscreen_p = [] #Will contain the projectiles that aren't visible
		for i in range(0, len(self.projectiles)) :
			self.projectiles[i].update()
			if self.projectiles[i].is_offscreen() :
				offscreen_p.append(i)
		
		#Removes projectiles that are out of the screen
		for i_del in range(0, len(offscreen_p)) :
			del self.projectiles[i_del]

	def draw(self) :
		stroke = 3
		pygame.draw.polygon(self.screen, self.color, self.points, stroke)

		#Draws projectiles that have been shot
		for p in self.projectiles :
			p.draw()

class Projectile(object) :

	def __init__(self, x, y, ship_angle, screen) :
		self.screen = screen
		self.speed = 16
		self.direction = ship_angle;
		self.velocity = Vector2D().create_from_angle(self.direction, self.speed, return_instance = True)
		self.pos = Vector2D(x, y)
		self.color = colors.green
		self.size = 4
		self.box = (0,0,0,0)

	def is_offscreen(self) :
		return self.pos.x > self.screen.get_width() or \
			   self.pos.x < 0 or \
			   self.pos.y > self.screen.get_height() or \
			   self.pos.y < 0

	def update(self) :
		self.pos.add(self.velocity)
		self.box = (self.pos.x, self.pos.y, self.size, self.size)

	def draw(self) :
		pygame.draw.ellipse(self.screen, self.color, self.box)