# 1 - Import library
import pygame
from pygame.locals import *
import math
import random

#  -----------------------------------------------------------------------------
def initialize():
        # 2 - Initialize the game
        pygame.init()


        width, height = 640, 480
        screen=pygame.display.set_mode((width, height))
        keys = [False, False, False, False]
        return screen

#  -----------------------------------------------------------------------------

def mostra_streghe(screen,coord_cattivi,i):

        if len(coord_cattivi)>0:
                coord=coord_cattivi[0]
        
        if coord[0]<-4:
            if len(coord_cattivi)>0:    
                coord_cattivi.pop(0)
        
        coord[0]+=-40
        verso=random.randint(-1,1)
        
        coord[1]=coord[1]+math.sin(i)*40-10
        if coord[1]<0:
                coord[1]=coord[1]+math.sin(i)*40+10
        
        for coord in coord_cattivi:
                screen.blit(badguyimg, coord)
#  -----------------------------------------------------------------------------                

def ciclo_streghe(screen):
        global badguyimg
        badguyimg = pygame.image.load("immagini/kopa.png")
        coord_cattivi=[[640,100]]
        clock = pygame.time.Clock()
        for i in range(5):
                coord_cattivi.append([640, random.randint(50,430)])
        i=1
        while 1:
                clock.tick(5)
                screen.fill(0)
                i=i+1
                mostra_streghe(screen,coord_cattivi,i)        
                for event in pygame.event.get():
                # check if the event is the X button 
                        if event.type==pygame.QUIT:
                            # if it is quit the game
                            pygame.quit()
                            exit(0)
                pygame.display.flip()    
 
#  -----------------------------------------------------------------------------               
def main():
        screen=initialize()
        ciclo_streghe(screen)
        
#  -----------------------------------------------------------------------------


if __name__ == '__main__':
    main()