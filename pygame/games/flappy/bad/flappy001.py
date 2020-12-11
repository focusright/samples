import pygame

size = w, h = 400, 600
screen = pygame.display.set_mode((size))
pygame.display.set_caption("Flappy Py")


class Sprite(pygame.sprite.Sprite):
    def __init__(self, file, x, y):
        super(Sprite, self).__init__()
        self.x = x
        self.y = y
        self.image = load(file)
        self.rect = pygame.Rect(self.x, self.y, 32, 32)
        g.add(self)

    # def update(self):
    #     self.rect = pygame.Rect(self.x, self.y, 32, 32)



def load(file):
    return pygame.image.load(file + ".png")


def gravity():
    flappy.rect.top += 1

g = pygame.sprite.Group()
bg = Sprite("bg", 0, 0)
flappy = Sprite("flappy", 50, 300)
def main():

    # jump controlo variables:
    # - after you press
    moveup = 0
    # how high can go
    startcounter = 0
    # How hight flappy jumps
    topjump = 40
    # how speed it jumps
    jumpspeed = 3

    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    loop = 1
    while loop:

        if moveup:
            flappy.rect.top -= jumpspeed
            startcounter += 1
            print(startcounter)
        if startcounter == topjump:
            startcounter = 0
            moveup = 0


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = 0
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    moveup = 1
                    startcounter = 1

        g.draw(screen)
        g.update()
        if not moveup:
            gravity()
        pygame.display.update()
        clock.tick(120)

    pygame.quit()


main()


