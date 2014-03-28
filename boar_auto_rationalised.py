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
                animTypes = 'left_walk back_walk front_walk NW SW'.split()
                self.animObjs = {}
                for animType in animTypes:
                    imagesAndDurations = [('animation/boar/boar_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
                    self.animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)

                # create the right-facing sprites by copying and flipping the left-facing sprites
                self.animObjs['right_walk'] = self.animObjs['left_walk'].getCopy()
                self.animObjs['right_walk'].flip(True, False)
                self.animObjs['right_walk'].makeTransformsPermanent()
                self.animObjs['SE'] = self.animObjs['SW'].getCopy()
                self.animObjs['SE'].flip(True, False)
                self.animObjs['SE'].makeTransformsPermanent()
                self.animObjs['NE'] = self.animObjs['NW'].getCopy()
                self.animObjs['NE'].flip(True, False)
                self.animObjs['NE'].makeTransformsPermanent()

                #animObjs['right_run'] = animObjs['left_run'].getCopy()
                #animObjs['right_run'].flip(True, False)
                #animObjs['right_run'].makeTransformsPermanent()

                # have the animation objects managed by a conductor.
                # With the conductor, we can call play() and stop() on all the animtion
                # objects at the same time, so that way they'll always be in sync with each
                # other.
                self.moveConductor = pyganim.PygConductor(self.animObjs)

#Classe               

class Ciclo(object):
        
        def miotimer(self):
                print "timer lanciato"
                self.lanciato=True
                threading.Timer(10.0, self.avvia).start()

        def avvia(self):
                self.auto=True
                self.lanciato=False
                
        def calcola_direzione(self,pos,mousepos):
            angolo= geometry.angle_of(pos,mousepos)
            ore=(angolo*100/360)*12
            if ore>100 and ore<200:
                    #print 'NE'
                    direzione='NE'
            elif ore>400 and ore<500:
                    #print "SE"
                    direzione='SE'
            elif ore>700 and ore<800:
                    #print "SW"
                    direzione='SW'
            elif ore>1000 and ore<1100:
                    #print "NW"
                    direzione='NW'
            elif ore>1100 or ore<100:
                    #print "N"
                    direzione='back'
            elif ore>500 and ore<700:
                    #print "S"
                    direzione='front'
            elif ore>200 and ore<400:
                    #print "E"
                    direzione='right'
            elif ore>800 and ore<1000:
                    #print "W"
                    direzione='left'
            return direzione
        
        
        def scegli_fotogramma_animazione(self,miocing,direzione):
            if len(self.listap)>0:  ##inizia la camminata
                pos= self.listap.pop(0)
                self.x,self.y=pos
                miocing.moveConductor.play()
                if direzione=='left':
                    self.fotogramma=miocing.animObjs['left_walk'].ritorna_fotogramma()
                elif direzione=='front':
                    self.fotogramma=miocing.animObjs['front_walk'].ritorna_fotogramma()
                elif direzione=='right':
                    #miocing.animObjs['right_walk'].blit(windowSurface, (x, y))
                    self.fotogramma=miocing.animObjs['right_walk'].ritorna_fotogramma()
                elif direzione=='back':
                    #miocing.animObjs['back_walk'].blit(windowSurface, (x, y))
                    self.fotogramma=miocing.animObjs['back_walk'].ritorna_fotogramma()
                elif direzione=='SW':
                    self.fotogramma=miocing.animObjs['SW'].ritorna_fotogramma()
                elif direzione=='NW':
                    self.fotogramma=miocing.animObjs['NW'].ritorna_fotogramma()
                elif direzione=='SE':
                    self.fotogramma=miocing.animObjs['SE'].ritorna_fotogramma()
                elif direzione=='NE':
                    self.fotogramma=miocing.animObjs['NE'].ritorna_fotogramma()
                return self.fotogramma
        
        @property
        def is_walking(self):
            if len(self.listap)>0:
                return True
            else:
                return False
        
        def imposta_posizione_via_mouse(self,event):
            if event.type==pygame.MOUSEBUTTONDOWN:
                mousepos=pygame.mouse.get_pos()
                self.direzione=self.calcola_direzione((self.x,self.y),mousepos)
                self.listap=calcola_passi(or_pos=(self.x,self.y),target_pos=mousepos)
        
        def muovi_cinghiale(self,miocing):
            if self.auto: ##verifica se deve procedere a calcolare una nuova sequenza di passi
                        if self.contatore_destinazioni>len(self.lista_destinazioni)-1: self.contatore_destinazioni=0 ##resetta il contatore della lista delle destinazioni automatiche
                        self.listap=calcola_passi(or_pos=(self.x,self.y),target_pos=self.lista_destinazioni[self.contatore_destinazioni])
                        tpos=self.listap[len(self.listap)-1] ##calcola la direzione della destinazione da raggiungere
                        self.direzione=self.calcola_direzione((self.x,self.y),tpos)
                        self.contatore_destinazioni=self.contatore_destinazioni+1 ##incrementa il contatore delle destinazioni
                        self.auto=False ##arresta il cinghiale quando ha fatto una singola camminata

            if self.is_walking: self.scegli_fotogramma_animazione(miocing,self.direzione)
            if self.lanciato==False: self.miotimer()
            return self.fotogramma
            
            
            
        def main(self):
                pygame.init()
                screen = pygame.display.set_mode((800, 600), 0, 32)
                pygame.display.set_caption('Cinghiale in movimento')
                miocing=Cinghiale()
                BGCOLOR = (180, 180, 180)
                mainClock = pygame.time.Clock()
                self.lista_destinazioni=[(400,200),(400,300),(500,300),(350,300)]
                self.x=100
                self.y=100
                i_luoghi=0
                i=0
                self.contatore_destinazioni=0
                self.listap=calcola_passi(or_pos=(self.x,self.y),target_pos=self.lista_destinazioni[i])
                angolo=1
                fotogramma=pygame.image.load('animation/boar/boar_left_walk.000.gif')
                self.auto=True
                self.lanciato=False
                while True:
                    screen.fill(BGCOLOR)
                    screen.blit(fotogramma, (self.x, self.y))
                    pygame.display.flip()
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
                                self.auto=True
                        elif event.type == KEYUP:
                                pass
                        self.imposta_posizione_via_mouse(event)
                    fotogramma=self.muovi_cinghiale(miocing)
                    mainClock.tick(50) # Feel free to experiment with any FPS setting.

#fine della Classe
                    
                    
              
                    

ciclo=Ciclo()
ciclo.main()