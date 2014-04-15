# coding: utf-8
#                       
# Questa è la classe di partenza, in cui si setta lo schermo pygame,
# è anche definita la funzione per scrivere sul fondo dello schermo
# e le funzioni che gestiscono il lancio di proiettili da un punto.
# Per usare i proiettili nella mappa però si dovrà usare una funzione 
# che si trova in mappa base perchò serve usare uno sprite
#----------------------------------------------------------


import sys
#sys.path.append("..\\") 
sys.path.append("..\\librerie\\gamelib") 


import os
import math
import pygame
from pygame.locals import*
import tiledtmxloader

# ------------------------------------------------------------------------------
# funzione ausiliaria che serve solo per il debug
#  -----------------------------------------------------------------------------
def printer(obj, ident=''):
    """
    Helper function, prints a heirarchy of objects.
    """
    import inspect
    print(ident + obj.__class__.__name__.upper())
    ident += '    '
    lists = []
    for name in dir(obj):
        elem = getattr(obj, name)
        if isinstance(elem, list) and name != 'decoded_content':
            lists.append(elem)
        elif not inspect.ismethod(elem):
            if not name.startswith('__'):
                if name == 'data' and elem:
                    print(ident + 'data = ')
                    printer(elem, ident + '    ')
                else:
                    print(ident + '%s\t= %s' % (name, getattr(obj, name)))
    for objt_list in lists:
        for _obj in objt_list:
            printer(_obj, ident + '    ')        


class Dialogosemplice():
	open=True
	def __init__(self):
		self.text_altezza=100
		self.crossrect=None
	
	def scrivi_frase(self,testo="Hello There"):
		screen=pygame.display.get_surface()
		# Fill background
		background_txt = pygame.Surface((screen.get_size()[0]-10,self.text_altezza))
		#self.background_txt = self.background_txt.convert()
		background_txt.fill((250, 250, 250))
		font = pygame.font.Font(None, 36)
		text = font.render(testo, 1, (10, 10, 10))
		background_txt.blit(text,(10,10))
		bgrect=background_txt.get_rect()
		bgrect.top=screen.get_size()[1]-self.text_altezza
		self.crossrect=bgrect
		cross=pygame.image.load('..\\immagini\\cross.gif')
		background_txt.blit(cross,(bgrect.topright[0]-15,0))
		screen.blit(background_txt,(bgrect.x,bgrect.y))
		self.gestione_eventi()
	
	def gestione_eventi(self):
		event=pygame.event.peek()
		if event.type==pygame.MOUSEBUTTONDOWN:
			pos=pygame.mouse.get_pos()
			if self.crossrect.collidepoint(pos):
				self.open=False
					
		
		


#--------------------------------------------------------------------------------
# classe schermo_base, vedi sopra commento di testa
# --------------------------------------------------------------------------------
class schermo_base:
	dialogo_surface=True
	def __init__(self):
		#print "Inzializzazione oggetto schermo_base..."
		self.screen_width=800
		self.screen_height=500
		self.running_loop=True
		self.text_altezza=100
		self.acc=[0,0]
		self.arrows=[]
		self.arrow = pygame.image.load("..\\immagini\\bulletfire_quad.png")
		self.arrow_new=self.arrow
		self.playerpos=(10,10)

#------------------------------------------------------------------

	def cambia_pieno_schermo(self,fullscr):
		if   pygame.display.get_surface():
			screen=pygame.display.get_surface()
			video=pygame.display.Info()
			self.screen_width= video.current_w
			self.screen_height= video.current_h
			return screen

		if fullscr=='0':
			screen = pygame.display.set_mode((self.screen_width, self.screen_height))
		elif fullscr=='fullscr':
			#self.screen_width=1280
			#self.screen_height=1024
			video=pygame.display.Info()
			self.screen_width= video.current_w
			self.screen_height= video.current_h
			screen = pygame.display.set_mode((self.screen_width, self.screen_height),FULLSCREEN)
		return screen
#------------------------------------------------------------------

	def gestione_eventi(self):
		self.coda_eventi=pygame.event.get()
		for event in self.coda_eventi:
			if event.type == pygame.QUIT:
				self.running_loop = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.running_loop = False
				elif event.key == pygame.K_F4:
					self.dialogo_surface=True
			if event.type==pygame.MOUSEBUTTONDOWN:
				self.lancia_frecce()
				"""pos=pygame.mouse.get_pos()
				if self.crossrect.collidepoint(pos):
					self.dialogo_surface=False"""
#------------------------------------------------------------------
	def crea_mio_sprite(self,superficie):
		background= pygame.Surface(superficie.get_size())
		background.fill((250, 250, 250))
		myrect=background.get_rect()
		
		background.blit(superficie,(10,10))
		mysprite=pygame.sprite.Sprite() # create sprite
		mysprite.image=background
		mysprite.rect=myrect
		mysprite.rect.topleft = [5, self.screen.get_size()[1]-self.text_altezza]
		
		
		return mysprite
#------------------------------------------------------------------		

	def scrivi_frase(self,testo="Hello There"):
		# Fill background
		background_txt = pygame.Surface((self.screen.get_size()[0]-10,self.text_altezza))
		#self.background_txt = self.background_txt.convert()
		background_txt.fill((250, 250, 250))
		font = pygame.font.Font(None, 36)
		text = font.render(testo, 1, (10, 10, 10))
		background_txt.blit(text,(10,10))
		bgrect=background_txt.get_rect()
		bgrect.top=self.screen.get_size()[1]-self.text_altezza
		self.crossrect=bgrect
		cross=pygame.image.load('..\\immagini\\cross.gif')
		background_txt.blit(cross,(bgrect.topright[0]-15,0))
		b=tiledtmxloader.helperspygame.SpriteLayer.Sprite(background_txt,bgrect)
		return b
		
		
#--------------------------------------------------------------------
	def scritta_trasparente(self,testo):
		sfondo = pygame.Surface([800,50], pygame.SRCALPHA, 32)
		sfondo = sfondo.convert_alpha()
		font = pygame.font.Font(None, 32)
		text = font.render(testo, 1, (250, 250, 250))
		sfondo.blit(text,(0,0))
		
		bg_scritta_trasp_rect=sfondo.get_rect()
		bg_scritta_trasp_rect.x=self.pos_cruscotto[0]
		bg_scritta_trasp_rect.y=self.pos_cruscotto[1]
		b=tiledtmxloader.helperspygame.SpriteLayer.Sprite(sfondo,bg_scritta_trasp_rect)
		return b

#------------------------------------------------------------------
		
	def scrivi_frase_blit(self,testo="Hello There"):
		b=self.scrivi_frase(testo)
		self.screen.blit(b.image,b.rect)
#------------------------------------------------------------------
	def disegna_frecce_blit(self):
		for projectile in self.arrows:
			arrow1 = pygame.transform.rotate(self.arrow, 360-projectile[0]*57.29)
			self.screen.blit(arrow1, (projectile[1], projectile[2])) 
#------------------------------------------------------------------	
	def disegna_frecce_sprite(self):
		print "frecce sprite, il metodo sta in mappa_base.py"

#------------------------------------------------------------------
	def disegna_frecce(self,modo='blit'):
		for bullet in self.arrows:
			self.index_bullet=0
			velx=math.cos(bullet[0])*10
			vely=math.sin(bullet[0])*10
			bullet[1]+=velx
			bullet[2]+=vely
			if bullet[1]<-64 or bullet[1]>self.screen_width or bullet[2]<-64 or bullet[2]>self.screen_height:
			    self.arrows.pop(self.index_bullet)
			self.index_bullet+=1
			if modo=='blit':
				self.disegna_frecce_blit()
			if modo=='sprite':
				self.disegna_frecce_sprite()

#------------------------------------------------------------------
	def lancia_frecce(self):
		mouse_position=pygame.mouse.get_pos()
		self.acc[1]+=1
		#self.arrows.append([math.atan2(position[1]-(playerpos1[1]+32),position[0]-(playerpos1[0]+26)),playerpos1[0]+32,playerpos1[1]+32])
		arcotangente=math.atan2(\
			mouse_position[1]-(self.playerpos[1]+32), \
			mouse_position[0]-(self.playerpos[0]+26)\
			)
			
		self.arrows.append([ arcotangente,self.playerpos[0]+32,self.playerpos[1]+26 ])

#EofClass ------------------------------------------------------


def main():
	pygame.init()
	oggetto = schermo_base()
	# init pygame and set up a screen

	screen_width = 900
	screen_height = 600
	oggetto.screen=oggetto.cambia_pieno_schermo('0')
	dialogo=Dialogosemplice()
	
	

	while oggetto.running_loop:
		oggetto.screen.fill(0)
		if dialogo.open:
			dialogo.scrivi_frase()
		
		oggetto.disegna_frecce()
		
		pygame.display.flip()
		#dialogo.gestione_eventi()
		oggetto.gestione_eventi()
	
	
	
if __name__ == '__main__':
	
	main()
