import pygame
from pygame.locals import*
from sys import exit
from miefunzioni import gui
from miefunzioni import html

from giocatore_animato import *

#Class which manages onmouse hover events
class Option:
    hovered = False
    def __init__(self, text, pos,screen):
        self.text = text
        self.pos = pos
        self.screen=screen
        self.set_rect()
        self.draw()
    def draw(self):
        self.set_rend()
        self.screen.blit(self.rend, self.rect)
    def set_rend(self):
        menu_font = pygame.font.Font(None, 40)
        self.rend = menu_font.render(self.text, True, self.get_color())
    def get_color(self):
        if self.hovered:
            return (255, 255, 255)
        else:
            return (0, 0, 0)
    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos
#-----------------------------------EofClass

class mio_menu(giocatore_animato):
	def __init__(self):
		giocatore_animato.__init__(self)
		print "Inzializzazione oggetto menu..."

	def metti_sfondi(self):
		imm_sfondo = "immagini/pergamena.jpg"
		imm_sfondo2 = "immagini/pergamena3.jpg"
		
		giallo=255,255,128
		background = pygame.Surface(self.screen.get_size())
		background = background.convert()
		background.fill((giallo))
		sfondo1 = pygame.image.load(imm_sfondo).convert()
		sfondo1_ridotto =pygame.transform.scale(sfondo1,(650,768)) 
		sfondo2 = pygame.image.load(imm_sfondo2).convert()
		sfondo2_ridotto=pygame.transform.scale(sfondo2,(650,768))
		size = width, height = 500,300
		self.screen.blit(background, (0,0))
		self.screen.blit(sfondo1_ridotto,(0,0))
		self.screen.blit(sfondo2_ridotto,(650,0))
	
	def crea_opzioni(self):
		self.options = [Option("NEW GAME", (150, 105),self.screen), \
			Option("LOAD GAME", (150, 155),self.screen), \
			Option("OPTIONS", (150, 205),self.screen),
			Option("EXIT", (150, 245),self.screen)
			]
	
	def gestione_opzioni(self):
		for option in self.options:
			if option.rect.collidepoint(pygame.mouse.get_pos()):
				option.hovered = True
				if (option.text=="EXIT") and (pygame.mouse.get_pressed()[0]):
					self.running_loop = False
				elif (option.text=="NEW GAME") and (pygame.mouse.get_pressed()[0]):
					oldsurface=pygame.Surface.copy(self.screen)
					self.main()        
					self.screen.blit(oldsurface,(0,0))
					pygame.display.update()
					self.running_loop = True
	
			else:
			    option.hovered = False
			option.draw()
#-----------------------------------------------------------------------------


def main():
	oggetto=mio_menu()
	pygame.init()
	
	oggetto.screen=oggetto.cambia_pieno_schermo('fullscr')
	pygame.mouse.set_cursor(*pygame.cursors.tri_left)
	font = pygame.font.SysFont("Comic Sans MS", 18)
	oggetto.metti_sfondi()	
	with open ("trama.html", "r") as myfile:
	   miohtml=myfile.read().replace('\n', '')

	oggetto.crea_opzioni()
	html.write(oggetto.screen,font,pygame.Rect(120,300,400,400),miohtml)
	pygame.display.update()
	while oggetto.running_loop:
		oggetto.gestione_eventi()
		oggetto.gestione_opzioni()
		pygame.display.update(pygame.Rect(150, 105, 200, 200))



if __name__ == '__main__':
        main()