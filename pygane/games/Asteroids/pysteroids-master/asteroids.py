import pygame
from pygame.locals import *
import colors
from ship import *
from asteroid import *
from physics import *

# Screen and Color Variables
D_WIDTH = 800
D_HEIGHT = 600
FPS = 60

pygame.init()
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))
pygame.display.set_caption('Pysteroids')
clock = pygame.time.Clock()		
pygame.mouse.set_visible(True)

# Entities initialization
ship = Ship(D_WIDTH / 2, D_HEIGHT - (D_HEIGHT / 4), display)
ag = AsteroidGenerator(display)
ag.generate(4)
cd = CollisionDetector(ship, ag, ship.projectiles)

playing = True
while playing :

	keys = pygame.key.get_pressed()

	for event in pygame.event.get() :
		if event.type == pygame.QUIT :
			 playing = False
			
		# Event handling here--------------------------
		
		# -- Keydown events
		if event.type == pygame.KEYDOWN :
			if event.key == pygame.K_SPACE :
				ship.shoot()

			if event.key == pygame.K_p :
				playing = False
		# -- End Keydown events
		
		# End event handling -------------------------
		
	# Game Logic -------------------------------------
	

	# -- Elements updates
	if keys[pygame.K_a] :
		ship.turn('left')
		
	if keys[pygame.K_d] :
		ship.turn('right')

	if keys[pygame.K_w] :
		ship.boost()

	cd.handle_projectile_hits_asteroid()
	ship.update()
	ag.update()
	# -- End Elements updates
	

	# -- Screen drawing
	ship.draw()
	ag.draw()
	# -- End Screen drawing


	# End Game Logic ---------------------------------

	pygame.display.update()
	clock.tick(FPS)
	display.fill(colors.black)
	
pygame.quit()