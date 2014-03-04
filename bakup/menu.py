import pygame
#from dumbmenu import dumbmenu as dm
from miefunzioni import dumbmenu as dm
from motore_gioco import *

from pygame.locals import*
from sys import exit



def main():
        imm_sfondo = "immagini/pergamena.jpg"
        imm_sfondo2 = "immagini/pergamena3.jpg"
         
        pygame.init()

        # Just a few static variables
        red   = 255,  0,  0
        green =   0,255,  0
        blue  =   0,  0,255
        black = 0,0,0
        white= 255,255,255
        giallo=255,255,128

        video=pygame.display.Info()
        screen_width= video.current_w
        screen_height= video.current_h

        screen = pygame.display.set_mode((screen_width,screen_height), FULLSCREEN)
        #screen=pygame.display.set_mode((1366,768),FULLSCREEN)
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((giallo))
        sfondo1 = pygame.image.load(imm_sfondo).convert()
        sfondo1_ridotto =pygame.transform.scale(sfondo1,(650,768)) 
        sfondo2 = pygame.image.load(imm_sfondo2).convert()
        sfondo2_ridotto=pygame.transform.scale(sfondo2,(650,768))
        size = width, height = 500,300
        screen.blit(background, (0,0))
        screen.blit(sfondo1_ridotto,(0,0))
        screen.blit(sfondo2_ridotto,(650,0))
        #screen = pygame.display.set_mode(size)
        #screen.fill(blue)
        pygame.display.update()
        pygame.key.set_repeat(500,30)
        #miofont = pygame.font.Font("font/Minecraftia.ttf", 26)
        #label = miofont.render("Some text!", 1, (255,255,0))
        choose=0
        choose = dm.dumbmenu(screen, [
                                'NUOVA PARTITA',
                                'CARICA PARTITA',
                                'CONTENUTI SPECIALI',
                                'OPZIONI',
                                'SCHERMO PIENO',
                                'Esci'], 150,150,"Arial",44,0.6,black,white)
        
        oggetto = mia_mappa_oggetto()
        oggetto.layer_giocatore=1

        if choose== 0:
            oggetto.layer_giocatore=1
            oggetto.idx_layer_collisioni=3
            oggetto.poligoni=True
            oggetto.carica_mappa("mappe/mappa_x25.tmx",'fullscr')
        elif choose == 1:
            oggetto.layer_giocatore=3
            oggetto.carica_mappa('mappe/prova2.tmx','fullscr')
        elif choose == 2:
            oggetto.carica_mappa('mappe/001-1.tmx','fullscr')
        elif choose == 3:
            oggetto.carica_mappa('mappe/prova.tmx','fullscr')
        elif choose == 4:
            oggetto.carica_mappa('mappe/mappaluca.tmx','fullscr')
        elif choose == 5:
            print "You choose 'Quit Game'."
            pygame.quit()
            exit()
        
        main() #ricarica il menu dopo l'uscita dalla mappa scelta

if __name__ == '__main__':
        main()