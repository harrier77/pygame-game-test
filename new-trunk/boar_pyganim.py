# test4_pyganim.py - A pyganim test program.
#
# This program shows off the use of a PygConductor to help organize your
# animation objects. Conductors basically let you call PygAnimation methods on
# several PygAnimation objects at once (e.g. You can have all the animation
# objects start playing at the same time.)
#
# The animation images come from POW Studios, and are available under an
# Attribution-only license. Check them out, they're really nice.
# http://powstudios.com/
#
# The walking sprites are shamelessly taken from the excellent SNES game
# Chrono Trigger.
# http://www.videogamesprites.net/ChronoTrigger
import sys
sys.path.append(".\\miogummworld") 
sys.path.append(".\\miogummworld\\gamelib") 

import pygame
from pygame.locals import *
import sys
import time
from miefunzioni import pyganim
import gummworld2
from gummworld2 import geometry

def calcola_passi(or_pos=(300,200),target_pos=(200,200)):

        distanza=int(geometry.distance(or_pos,target_pos))
        lista_posizioni=[]
        for progress_distance in range(1,distanza):  
                p= geometry.step_toward_point(or_pos, target_pos, progress_distance)
                #print p
                lista_posizioni.append(p)
        return lista_posizioni




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

               



                

pygame.init()

# define some constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# set up the window
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Pyganim Test 4')


direction = DOWN # player starts off facing down (front)
miocing=Cinghiale()
#BASICFONT = pygame.font.Font('freesansbold.ttf', 16)
WHITE = (255, 255, 255)
BGCOLOR = (180, 180, 180)

mainClock = pygame.time.Clock()
x = 300 # x and y are the player's position
y = 200
WALKRATE = 2
RUNRATE = 12


running = moveUp = moveDown = moveLeft = moveRight =auto = False




while True:
    windowSurface.fill(BGCOLOR)
    listap=calcola_passi(or_pos=(x,y),target_pos=(200,200))
    for event in pygame.event.get(): # event handling loop

        # handle ending the program
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key in (K_LSHIFT, K_RSHIFT):
                # player has started running
                running = True

            if event.key == K_UP:
                moveUp = True
                moveDown = False
                if not moveLeft and not moveRight:
                    # only change the direction to up if the player wasn't moving left/right
                    direction = UP
            elif event.key == K_DOWN:
                moveDown = True
                moveUp = False
                if not moveLeft and not moveRight:
                    direction = DOWN
            elif event.key == K_LEFT:
                moveLeft = True
                moveRight = False
                if not moveUp and not moveDown:
                    direction = LEFT
            elif event.key == K_RIGHT:
                moveRight = True
                moveLeft = False
                if not moveUp and not moveDown:
                    direction = RIGHT
            elif event.key == K_F4:
                auto=True

        elif event.type == KEYUP:
            if event.key in (K_LSHIFT, K_RSHIFT):
                # player has stopped running
                running = False

            if event.key == K_UP:
                moveUp = False
                # if the player was moving in a sideways direction before, change the direction the player is facing.
                if moveLeft:
                    direction = LEFT
                if moveRight:
                    direction = RIGHT
            elif event.key == K_DOWN:
                moveDown = False
                if moveLeft:
                    direction = LEFT
                if moveRight:
                    direction = RIGHT
            elif event.key == K_LEFT:
                moveLeft = False
                if moveUp:
                    direction = UP
                if moveDown:
                    direction = DOWN
            elif event.key == K_RIGHT:
                moveRight = False
                if moveUp:
                    direction = UP
                if moveDown:
                    direction = DOWN

    if moveUp or moveDown or moveLeft or moveRight:
        # draw the correct walking/running sprite from the animation object
        #moveConductor.play() # calling play() while the animation objects are already playing is okay; in that case play() is a no-op
        miocing.moveConductor.play()
        if running:
            if direction == UP:
                animObjs['back_run'].blit(windowSurface, (x, y))
            elif direction == DOWN:
                animObjs['front_run'].blit(windowSurface, (x, y))
            elif direction == LEFT:
                animObjs['left_run'].blit(windowSurface, (x, y))
            elif direction == RIGHT:
                animObjs['right_run'].blit(windowSurface, (x, y))
        else:
            # walking
            if direction == UP:
                miocing.animObjs['back_walk'].blit(windowSurface, (x, y))
            elif direction == DOWN:
                miocing.animObjs['front_walk'].blit(windowSurface, (x, y))
            elif direction == LEFT:
                miocing.animObjs['left_walk'].blit(windowSurface, (x, y))
            elif direction == RIGHT:
                miocing.animObjs['right_walk'].blit(windowSurface, (x, y))


        # actually move the position of the player
        if running:
            rate = RUNRATE
        else:
            rate = WALKRATE

        if moveUp:
            y -= rate
        if moveDown:
            y += rate
        if moveLeft:
            x -= rate
        if moveRight:
            x += rate
    elif auto:
        if len(listap)>0:
            pos= listap.pop(0)
            x,y=pos
            miocing.moveConductor.play()
            miocing.animObjs['left_walk'].blit(windowSurface, (x, y))
        else:
            auto=False
    else:
        # standing still
        miocing.moveConductor.stop() # calling stop() while the animation objects are already stopped is okay; in that case stop() is a no-op
        if direction == UP:
            windowSurface.blit(miocing.back_standing, (x, y))
        elif direction == DOWN:
            windowSurface.blit(miocing.front_standing, (x, y))
        elif direction == LEFT:
            windowSurface.blit(miocing.left_standing, (x, y))
        elif direction == RIGHT:
            windowSurface.blit(miocing.right_standing, (x, y))

    # make sure the player does move off the screen
    if x < 0:
        x = 0
    if x > WINDOWWIDTH - miocing.playerWidth:
        x = WINDOWWIDTH - miocing.playerWidth
    if y < 0:
        y = 0
    if y > WINDOWHEIGHT - miocing.playerHeight:
        y = WINDOWHEIGHT - miocing.playerHeight

   
        
    pygame.display.update()
    mainClock.tick(30) # Feel free to experiment with any FPS setting.