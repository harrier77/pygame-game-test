import pygame
#from dumbmenu import dumbmenu as dm
from pygame.locals import*
from sys import exit
from miefunzioni import gui
from miefunzioni import html

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
            return (100, 100, 100)
        
    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos
#-----------------------------------EofClass

class mio_menu:
        def __init__(self):
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
                self.screen = pygame.display.set_mode((screen_width,screen_height))
                #screen=pygame.display.set_mode((1366,768),FULLSCREEN)
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
#-----------------------------------------------------------------------------


def main():
	oggetto=mio_menu()
	font = pygame.font.SysFont("Comic Sans MS", 18)       

	with open ("trama.html", "r") as myfile:
	    miohtml=myfile.read().replace('\n', '')

	
	
	options = [Option("NEW GAME", (840, 105),oggetto.screen), \
			Option("LOAD GAME", (840, 155),oggetto.screen), \
			Option("OPTIONS", (840, 205),oggetto.screen),
			Option("EXIT", (840, 245),oggetto.screen)
			]
		
	oggetto=mio_menu()
	running_loop = True
	while running_loop:
		html.write(oggetto.screen,font,pygame.Rect(120,100,450,900),miohtml)
		coda_eventi=pygame.event.get()
		for event in coda_eventi:
			if event.type == pygame.QUIT:
				running_loop = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running_loop = False
		for option in options:
			if option.rect.collidepoint(pygame.mouse.get_pos()):
			    option.hovered = True
			    if (option.text=="EXIT") and (pygame.mouse.get_pressed()[0]):
				running_loop = False
			    elif (option.text=="NEW GAME") and (pygame.mouse.get_pressed()[0]):
				import giocatore_animato
				running_loop = False
				giocatore_animato.main()        

			else:
			    option.hovered = False
			option.draw()
		pygame.display.update()
        
        



if __name__ == '__main__':
        main()