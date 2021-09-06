#https://www.cantorsparadise.com/why-a-spinning-donut-is-a-pure-math-e4dccc6294b0
#https://www.a1k0n.net/2011/07/20/donut-math.html

import pygame
import math
import random
from pygame.locals import *
from sys import exit
pygame.init()

WIDTH = 500
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
WHITE = (255,255,255)
BLACK = (0,0,0)
font = pygame.font.SysFont('arial', 10, bold=True)

x_space = 10 #width of character
y_space = 12 #height of character
columns = int(WIDTH / x_space)
rows = int(HEIGHT / y_space)

x_offset = WIDTH / 2
y_offset = HEIGHT / 2

r1 = 80 #radius 2D circle
r2 = 150 #distance from center / radius torus
A, B = 1, 1 #rotation angles x- and z-axis
K2 = 5000 #distance from viewer to donut
K1 = WIDTH * K2 * 3/(8*(r1+r2)) #distance from viewer to screen

chars = [".", ",", "-", "~", ":", ";", "=", "!", "*", "#", "$", "@"]

def draw(x, y, char):
    text = font.render(char, True, WHITE)
    screen.blit(text, (x, y))

while True:
    screen.fill((BLACK))
    cosB, sinB = math.cos(B), math.sin(B)
    cosA, sinA = math.cos(A), math.sin(A)

    #store characters
    output = []
    for i in range(rows):
        col1 = []
        for j in range(columns):
            col1.append(" ")
        output.append(col1)

    #store z-values
    zbuffer = []
    for i in range(rows):
        col2 = []
        for j in range(columns):
            col2.append(0)
        zbuffer.append(col2)


    for T in range(0, 628, 12):
        cosT, sinT = math.cos(T/100), math.sin(T/100)
        x2 = r2 + r1 * cosT #x coordinate 2D cricle
        y2 = r1 * sinT #y coordinate 2D circle

        for P in range(0, 628, 4):
            cosP, sinP = math.cos(P/100), math.sin(P/100)

            x = x2 * (cosB * cosP + sinA * sinB * sinP) - y2 * cosA * sinB
            y = x2 * (cosP * sinB - cosB * sinA * sinP) + y2 * cosA * cosB
            z = K2 + r1 * sinA * sinT + cosA * sinP * x2
            ooz = 1 / z # = one over z


            #x and y projection on screen
            xp = math.floor(-x * K1 * ooz)
            yp = math.floor(-y * K1 * ooz)

            #luminance
            l = cosP * cosT * sinB - cosA * cosT * sinP - sinA * sinT + cosB * (cosA * sinB - cosT * sinA * sinP)
            if l > -0.8:
                l = abs(l)
                yc = int((yp + y_offset) / y_space)
                xc = int((xp + x_offset) / x_space)
                if ooz > zbuffer[yc][xc]: #check if point is closer towards viewer than previous stored point
                    zbuffer[yc][xc] = ooz
                    L = round(l*5) #MLee: this 5 should be 8 but 8 crashes
                    #print(len(chars), L)
                    output[yc][xc] = chars[L]

    for a in range(rows):
        for b in range(columns):
            draw(b*x_space, a*y_space, output[a][b])

    #prevent A an B to go up to infinity
    if (A > 6.283 and A < 6.2831):
        A = 0
        B = 0
    else:
        A += 0.06
        B += 0.04


    for event in pygame.event.get():
        if event.type == QUIT:
            exit()


    pygame.display.update()


