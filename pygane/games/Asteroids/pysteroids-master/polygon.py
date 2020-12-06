from vectors import Vector2D
import math

class Polygon(object) :
	
	def __init__(self) :
		self.size = None
		self.rotation = 0
		self.points = []
		self.pos = Vector2D(0, 0)

	##
	# TODO : Make methods accept Tuples and Vector2D Objects
	##
	def translate(self, vector) : 
		translated_polygon = []
		for point in self.points :
			new_point = (point[0] + vector[0], point[1] + vector[1])
			translated_polygon.append(new_point)
	
		self.points = translated_polygon

	def rotate(self, center = (0, 0), angle = 0) :
		angle = math.radians(angle)
		rotated_polygon = []
		for point in self.points :
			new_point = (point[0] - center[0], point[1] - center[1])
			new_point = (new_point[0] * math.cos(angle) - new_point[1] * math.sin(angle), 
						 new_point[0] * math.sin(angle) + new_point[1] * math.cos(angle))
			new_point = new_point[0] + center[0], new_point[1] + center[1]
			rotated_polygon.append(new_point)

		self.points = rotated_polygon