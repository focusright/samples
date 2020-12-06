import pygame
import colors
import math
import random
import helpers
from vectors import Vector2D
from polygon import Polygon

class Asteroid(Polygon) :
	
	def __init__(self, screen, pos = Vector2D(0,0), size = 24, vert_count = 10) :
		self.screen = screen
		self.pos = pos
		self.size = size
		self.color = colors.green
		self.velocity = Vector2D(0, 0)
		self.points = []
		self.generate_random_shape(vert_count)
		self.type = 1
		
	def generate_random_shape(self, _vertices_count = 10) :
		vertices_count = _vertices_count
		mean_radius = self.size
		sigma_radius = self.size / 5
		counter = 0
		for theta in helpers.linspace(0, 2 * math.pi - (2 * math.pi / vertices_count), vertices_count) :
			radius = random.gauss(mean_radius, sigma_radius)
			x = self.pos.x + radius * math.cos(theta)
			y = self.pos.y + radius * math.sin(theta)
			self.points.append((x,y))
			counter += 1

	def set_velocity(self, vel) : #Receives Vector2D
		self.velocity = vel

	def explosion(self) :
		print('Explosion!')

	def update(self) :
		self.pos.add(self.velocity)
		
		# Resets asteroid possition when it's out of the screen
		if self.pos.x > (self.screen.get_width() + self.size) :
			#print('COLLIDED RIGHT')
			self.pos.x -= self.screen.get_width() + (2 * self.size)
			self.translate((-(self.screen.get_width() + (2 * self.size)), 0))
		elif self.pos.x < -self.size :
			#print('COLLIDED LEFT')
			self.pos.x += self.screen.get_width() + (2 * self.size)
			self.translate(((self.screen.get_width() + self.size), 0))
		if self.pos.y > (self.screen.get_height() + (2 * self.size)) :
			#print('COLLIDED BOTTOM')
			self.pos.y -= self.screen.get_height() + (2 * self.size)
			self.translate((0, -(self.screen.get_height() + (2 * self.size))))
		elif self.pos.y < -self.size :
			#print('COLLIDED TOP')
			self.pos.y += self.screen.get_height() + (2 * self.size)
			self.translate((0, (self.screen.get_height() + (2 * self.size))))

		self.translate((self.velocity.x, self.velocity.y))

	def draw(self) :
		stroke = 3
		pygame.draw.polygon(self.screen, self.color, self.points, stroke)


class AsteroidGenerator(object) :
	
	def __init__(self, screen) :
		self.screen = screen
		self.asteroids = []

	def generate(self, count, _size = None, vert_count = 10, _pos = None, type = 1) :
		#print('Generating ' + str(count) + ' asteroids')
		for i in range(count) :
			if _size == None :
				size = random.randint(25, 50)
			else :
				size = _size

			if _pos == None :
				pos = Vector2D(random.randint(0, self.screen.get_width()), random.randint(0, self.screen.get_height() / 2))
			else :
				pos = Vector2D(_pos.x, _pos.y)

			asteroid = Asteroid(self.screen, pos, size, vert_count)
			asteroid.set_velocity(Vector2D(random.randint(1, 3), random.randint(1, 3)))
			asteroid.type = type
			self.asteroids.append(asteroid)
			#print('Asteroid generated in possition ' + str(asteroid.pos.x) + ', ' + str(asteroid.pos.y))

	def generate_debris(self, pos) : #pos is Vector2D type
		#print('Generating debris at: ', pos.x, ', ', pos.y)
		self.generate(3, random.randint(8, 16), 6, pos, 2)

	def draw(self) :
		for asteroid in self.asteroids :
			asteroid.draw()

	def update(self) :
		for asteroid in self.asteroids :
			asteroid.update()