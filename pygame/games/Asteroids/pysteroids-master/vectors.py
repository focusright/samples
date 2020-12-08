import math

class Vector2D(object) :
	
	def __init__(self, x = None, y = None) :
		self.x = x
		self.y = y

	def create_from_angle(self, angle, magnitude, return_instance = False) :
		angle = math.radians(angle) - math.pi / 2
		x = math.cos(angle) * magnitude
		y = math.sin(angle) * magnitude
		self.x = x
		self.y = y

		if return_instance :
			return self

	def tuple(self) :
		return (self.x, self.y)

	def add(self, vector) :
		if isinstance(vector, self.__class__) :
			self.x += vector.x 
			self.y += vector.y
		else :
			self.x += vector[0]
			self.y += vector[1]

	def mult(self, vector) :
		if isinstance(vector, self.__class__) :
			self.x *= vector.x 
			self.y *= vector.y
		else :
			self.x *= vector[0]
			self.y *= vector[1]

	def distance(self, vector) : 
		if isinstance(vector, self.__class__) :
			return math.hypot(self.x - vector.x, self.y - vector.y)
		else :
			return math.hypot(self.x - vector[0], self.y - vector[1])