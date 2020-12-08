import math

def translate_polygon(polygon, vector) :
	translated_polygon = []
	for point in polygon :
		new_point = (point[0] + vector[0], point[1] + vector[1])
		translated_polygon.append(new_point)
	
	return translated_polygon

def rotate_polygon(polygon, center, angle) :
	angle = math.radians(angle)
	rotated_polygon = []
	for point in polygon :
		new_point = (point[0] - center[0], point[1] - center[1])
		new_point = (new_point[0] * math.cos(angle) - new_point[1] * math.sin(angle), 
					 new_point[0] * math.sin(angle) + new_point[1] * math.cos(angle))
		new_point = new_point[0] + center[0], new_point[1] + center[1]
		rotated_polygon.append(new_point)

	return rotated_polygon

def linspace(start, stop, num_steps):
    values = []
    delta = (stop - start) / num_steps
    for i in range(num_steps):
        values.append(start + i * delta)
    return values
