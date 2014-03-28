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
import threading

def calcola_passi(or_pos=(300,200),target_pos=(200,200)):

        distanza=int(geometry.distance(or_pos,target_pos))
        lista_posizioni=[]
        for progress_distance in range(1,distanza):  
                p= geometry.step_toward_point(or_pos, target_pos, progress_distance)
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

               

class Ciclo():
        
        def miotimer(self):
                threading.Timer(5.0, self.avvia).start()

        def avvia(self):
                print "avvia"
                self.auto=True
                
        def calcola_direzione(self,pos,mousepos):
            angolo= geometry.angle_of(pos,mousepos)
            ore=(angolo*100/360)*12
            if ore>100 and ore<200:
                    print 'NE'
                    direzione='back'
            elif ore>400 and ore<500:
                    print "SE"
                    direzione='front'
            elif ore>700 and ore<800:
                    print "SW"
                    direzione='front'
            elif ore>1000 and ore<1100:
                    print "NW"
                    direzione='back'
            elif ore>1100 or ore<100:
                    print "N"
                    direzione='back'
            elif ore>500 and ore<700:
                    print "S"
                    direzione='front'
            elif ore>200 and ore<400:
                    print "E"
                    direzione='right'
            elif ore>800 and ore<1000:
                    print "W"
                    direzione='left'
            return direzione
        
        def main(self):
                pygame.init()
                screen = pygame.display.set_mode((800, 600))
                img=pygame.image.load('immagini/kopa.png')
                print img
                while True:
                    screen.blit(img,(200,200))
                    pygame.display.flip()
                    for event in pygame.event.get(): # event handling loop
                        # handle ending the program
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
               
                    
                    
              
                    

ciclo=Ciclo()
ciclo.main()