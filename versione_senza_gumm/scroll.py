import pygame
from pygame.locals import*
import sys
#sys.path.append("..\\miogummworld") 
#sys.path.append("..\\miogummworld\\gamelib") 
sys.path.append("..\\") 
from sys import exit
import miefunzioni
from miefunzioni import html
from miefunzioni import gui
from giocatore_animato import *
import os


def apri_mappa(nomefile):
	print nomefile
	miog=giocatore_animato()
	#miog.vedi_collisioni=False
	miog.file_mappa="..\..\\tmwa\\maps\\"+nomefile
	miog.main()

def main():
	position = 1, 1
	os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])

	pygame.init()
	giallo=255,255,128
	video=pygame.display.Info()
	screen_width= video.current_w-1
	screen_height= video.current_h-1
	screen = pygame.display.set_mode((screen_width,screen_height))
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((giallo))
	screen.blit(background, (0,0))

	app = gui.App()
	tabella = gui.Table()
	label = gui.Label("Elenco mappe The Mana World")
	vuoto = gui.Label(" ")
	mioscrollo= gui.ScrollArea(tabella,width=screen_width/2,height=screen_height)
	
	#link.connect(gui.CLICK,None,'uno')
	tabella.tr()
	tabella.td(label,colspan=3)
	tabella.tr()
	tabella.td(vuoto,colspan=3)
	tabella.tr()
	tabella.td(gui.Label("File"))
	tabella.td(gui.Label("Minimappe"))



	lista_immagini=os.listdir('..\..\\tmwa\\graphics\\minimaps')
	for fname in lista_immagini:
		n_senza_est = os.path.splitext(fname)[0]
		nome_tmx=n_senza_est+".tmx"
		tabella.tr()
		miobott=gui.Label(nome_tmx)
		tabella.td(miobott)
		miobott.connect(gui.CLICK, apri_mappa, nome_tmx) 
		mia_immagine=gui.Image('..\..\\tmwa\\graphics\\minimaps\\'+fname)
		mia_immagine.connect(gui.CLICK, apri_mappa, nome_tmx) 
		tabella.td(mia_immagine)



	app.init(mioscrollo)

	sfondo_vuoto=screen.copy()
	mioloop=True
	while mioloop:
		coda_eventi=pygame.event.get()
		for event in coda_eventi:
			if event.type == pygame.QUIT:
				mioloop = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					mioloop = False
			app.event(event)
		screen.blit(sfondo_vuoto, (0,0))
		app.paint()
		pygame.display.flip()
		
if __name__ == '__main__':
	main()