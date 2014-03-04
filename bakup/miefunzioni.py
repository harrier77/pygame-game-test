import sys
import os
import math


import pygame
import pyganim
import winsound


#  -----------------------------------------------------------------------------

def create_hero(start_pos_x, start_pos_y):
    """
    Creates the hero sprite.
    """
    image = pygame.Surface((50, 70), pygame.SRCALPHA)
    image.fill((255, 0, 0, 200))
    rect = image.get_rect()
    rect.midbottom = (start_pos_x, start_pos_y)
    return tiledtmxloader.helperspygame.SpriteLayer.Sprite(image, rect)

#  -----------------------------------------------------------------------------
"""
def crea_giocatore():

        # load the "standing" sprites (these are single images, not animations)
        front_standing = pygame.image.load('gameimages/crono_front.gif')
        back_standing = pygame.image.load('gameimages/crono_back.gif')
        left_standing = pygame.image.load('gameimages/crono_left.gif')
        right_standing = pygame.transform.flip(left_standing, True, False)

        playerWidth, playerHeight = front_standing.get_size()

        # creating the PygAnimation objects for walking/running in all directions
        animTypes = 'back_run back_walk front_run front_walk left_run left_walk'.split()
        animObjs = {}
        for animType in animTypes:
            imagesAndDurations = [('gameimages/crono_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
            animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)

        # create the right-facing sprites by copying and flipping the left-facing sprites
        animObjs['right_walk'] = animObjs['left_walk'].getCopy()
        animObjs['right_walk'].flip(True, False)
        animObjs['right_walk'].makeTransformsPermanent()
        animObjs['right_run'] = animObjs['left_run'].getCopy()
        animObjs['right_run'].flip(True, False)
        animObjs['right_run'].makeTransformsPermanent()

        # have the animation objects managed by a conductor.
        # With the conductor, we can call play() and stop() on all the animtion
        # objects at the same time, so that way they'll always be in sync with each
        # other.
        moveConductor = pyganim.PygConductor(animObjs)

        moveConductor.play()
        return animObjs

#  -----------------------------------------------------------------------------
"""
"""
def crea_strega():
        #primo_fotogramma=pygame.image.load('koba.png')
        imagesAndDurations = [('immagini/kopa.png',0.2),('immagini/kopa.png',0.2)]
        animObj = pyganim.PygAnimation(imagesAndDurations)
        moveConductor = pyganim.PygConductor(animObj)
        moveConductor.play()
        return animObj
"""
"""
def coord_strega(i):
        x=1000-i
        coord=(x,200)
        return coord
"""
"""
def mybeep():
        Freq = 600 # Set Frequency To 2500 Hertz
        Dur = 30 # Set Duration To 1000 ms == 1 second
        winsound.Beep(Freq,Dur)
"""
"""
def check_collision(hero_pos_x, hero_pos_y, step_x, step_y, \
                                    hero_width, hero_height, coll_layer):

    # create hero rect
    hero_rect = pygame.Rect(0, 0, hero_width, hero_height)
    hero_rect.midbottom = (hero_pos_x, hero_pos_y)

    # find the tile location of the hero
    tile_x = int((hero_pos_x) // coll_layer.tilewidth)
    tile_y = int((hero_pos_y) // coll_layer.tileheight)

    # find the tiles around the hero and extract their rects for collision
    tile_rects = []
    for diry in (-1, 0 , 1):
        for dirx in (-1, 0, 1):
            if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                tile_rects.append(coll_layer.content2D[tile_y + diry][tile_x + dirx].rect)

    # save the original steps and return them if not canceled
    to_return_step_x = step_x
    to_return_step_y = step_y

    # x direction, floor or ceil depending on the sign of the step
    step_x = special_round(step_x)

    # detect a collision and dont move in x direction if colliding
    if hero_rect.move(step_x, 0).collidelist(tile_rects) > -1:
        to_return_step_x = 0 
        mybeep()

    # y direction, floor or ceil depending on the sign of the step
    step_y = special_round(step_y)

    # detect a collision and dont move in y direction if colliding
    if hero_rect.move(0, step_y).collidelist(tile_rects) > -1:
        to_return_step_y = 0
        mybeep()
        
    #print to_return_step_x
    #print to_return_step_y
    # return the step the hero should do
    return to_return_step_x, to_return_step_y

#  -----------------------------------------------------------------------------
"""

#def special_round(value):
   
    # same as:  math.copysign(math.ceil(abs(x)), x)
    # OR:
    # ## versus this, which could save many function calls
    # import math
    # ceil_or_floor = { True : math.ceil, False : math.floor, }
    # # usage
    # x = floor_or_ceil[val<0.0](val)

    #if value < 0:
    #    return math.floor(value)
    #return math.ceil(value)
    
#  -----------------------------------------------------------------------------