import pygame

import sys
sys.path.append(".\\miogummworld") 
sys.path.append(".\\miogummworld\\gamelib") 
from pygame.sprite import Sprite
from pygame.locals import *
import gummworld2
from gummworld2 import geometry

#-----------------------------------------------
class Bestia(object):
    #------------------------------------
    def __init__(self, map_pos):
        """Kind of a man-shaped guy."""
        self.image = pygame.Surface((20,50))
        cinghiale= pygame.image.load('animation/boar/boar_left_walk.001.gif')
        self.image = cinghiale
        self.north= pygame.image.load('animation/boar/boar_back_walk.000.gif')
        self.south= pygame.image.load('animation/boar/boar_front_walk.000.gif')
        self.SW= pygame.image.load('animation/boar/boar_SW.000.gif')
        self.NW= pygame.image.load('animation/boar/boar_NW.000.gif')
        
        self.east=pygame.transform.flip(self.west, True, False)
        self.SE=pygame.transform.flip(self.SW, True, False)
        self.NE=pygame.transform.flip(self.NW, True, False)
        
        self.rect = self.image.get_rect()
        #self.hitbox = Rect(0,0,20,50)
        self.hitbox=self.rect
        self.position = map_pos
        self.baricentro=self.position[0]+self.hitbox.width/2,self.position[1]+self.hitbox.height/2
        print self.position
        print self.baricentro
        print self.rect
    
    @property
    def west(self):
        return self.image
#---------------------------------------------------

pers=Bestia((300,200))
pygame.init()
# set up the window
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Prototipo')
BGCOLOR = (180, 180, 180)
mypers=pers.north
img=pers.south
while True:
        pygame.draw.circle(windowSurface, Color('pink'), pers.baricentro, 100)
        windowSurface.blit(img,pers.position)
        #windowSurface.blit(pers.south,pers.position)
        for event in pygame.event.get(): # event handling loop
                # handle ending the program
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_F4:
                        auto=True
                
                if event.type==pygame.MOUSEBUTTONDOWN:
                        #pygame.draw.circle(windowSurface, Color('pink'), pers.baricentro, 100)
                        mousepos=pygame.mouse.get_pos()
                        angolo= geometry.angle_of(pers.baricentro,mousepos)
                        #print "angolo"+str(angolo)
                        ore=(angolo*100/360)*12
                        #print "ore"+str(ore)
                        if ore>100 and ore<200:
                                print 'NE'
                                #windowSurface.blit(pers.NE,pers.position)
                                img=pers.NE
                                #mypers=pers.east
                        elif ore>400 and ore<500:
                                print "SE"
                                #windowSurface.blit(pers.SE,pers.position)
                                img=pers.SE
                        elif ore>700 and ore<800:
                                print "SW"
                                #windowSurface.blit(pers.SW,pers.position)
                                img=pers.SW
                        elif ore>1000 and ore<1100:
                                print "NW"
                                #windowSurface.blit(pers.NW,pers.position)
                                img=pers.NW
                        elif ore>1100 or ore<100:
                                print "N"
                                #windowSurface.blit(pers.north,pers.position)
                                img=pers.north
                        elif ore>500 and ore<700:
                                print "S"
                                #windowSurface.blit(pers.south,pers.position)
                                img=pers.south
                        elif ore>200 and ore<400:
                                print "E"
                                #windowSurface.blit(pers.east,pers.position)
                                img=pers.east
                        elif ore>800 and ore<1000:
                                print "W"
                                #windowSurface.blit(pers.west,pers.position)
                                img=pers.west
        pygame.display.update()