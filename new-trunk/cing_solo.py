
import pygame
from pygame.locals import *
import sys
import time
from miefunzioni import pyganim


class Cinghiale():
        def __init__(self):
                # load the "standing" sprites (these are single images, not animations)
                self.front_standing = pygame.image.load('animation/boar/boar_front_walk.001.gif')
                self.back_standing = pygame.image.load('animation/boar/boar_back_walk.001.gif')
                self.left_standing = pygame.image.load('animation/boar/boar_left_walk.001.gif')
                self.right_standing = pygame.transform.flip(self.left_standing, True, False)

                self.playerWidth, self.playerHeight = self.front_standing.get_size()

                # creating the PygAnimation objects for walking/running in all directions
                animTypes = 'left_walk back_walk front_walk'.split()
                self.animObjs = {}
                for animType in animTypes:
                    imagesAndDurations = [('animation/boar/boar_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
                    self.animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)

                # create the right-facing sprites by copying and flipping the left-facing sprites
                self.animObjs['right_walk'] = self.animObjs['left_walk'].getCopy()
                self.animObjs['right_walk'].flip(True, False)
                self.animObjs['right_walk'].makeTransformsPermanent()
                #animObjs['right_run'] = animObjs['left_run'].getCopy()
                #animObjs['right_run'].flip(True, False)
                #animObjs['right_run'].makeTransformsPermanent()

                # have the animation objects managed by a conductor.
                # With the conductor, we can call play() and stop() on all the animtion
                # objects at the same time, so that way they'll always be in sync with each
                # other.
                self.moveConductor = pyganim.PygConductor(self.animObjs)

miocing=Cinghiale()

pygame.init()

# set up the window
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
BGCOLOR = (180, 180, 180)
x,y=100,100
# define some constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
direction = DOWN # player starts off facing down (front)
while True:
        windowSurface.fill(BGCOLOR)
        for event in pygame.event.get(): # event handling loop
                # handle ending the program
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
        miocing.moveConductor.play() 
        if direction == UP:
                miocing.animObjs['back_walk'].blit(windowSurface, (x, y))
        elif direction == DOWN:
                miocing.animObjs['front_walk'].blit(windowSurface, (x, y))
        elif direction == LEFT:
                miocing.animObjs['left_walk'].blit(windowSurface, (x, y))
        elif direction == RIGHT:
                miocing.animObjs['right_walk'].blit(windowSurface, (x, y))
                        
        #windowSurface.blit(miocing.front_standing, (x, y))

        pygame.display.update()
        
