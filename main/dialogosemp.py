import pygame
import paths
import gummworld2
from gummworld2 import data
class Dialogosemplice():
	open=False
	def __init__(self):
		self.text_altezza=100
		self.crossrect=None
		self.screen=pygame.display.get_surface()
		self.background_txt = pygame.Surface((self.screen.get_size()[0]-10,self.text_altezza))
		self.background_txt.fill((250, 250, 250))
		self.bgrect=self.background_txt.get_rect()
		self.bgrect.top=self.screen.get_size()[1]-self.text_altezza
		self.cross=pygame.image.load('.\\immagini\\cross.gif')
		self.font=pygame.font.Font(data.filepath('font', 'Vera.ttf'), 26)
		self.crossrect=self.cross.get_rect()
		self.crossrect.x=self.bgrect.topright[0]-15
		self.crossrect.y=self.bgrect.y
		self.crossrect.width=self.crossrect.width
		self.crossrect.height=self.crossrect.height
		
	def scrivi_frase(self,testo="Hello There"):	
		#font = pygame.font.Font(None, 32)
		text = self.font.render(testo, 1, (10, 10, 10))
		self.background_txt.blit(text,(10,10))
		self.background_txt.blit(self.cross,(self.crossrect.x,0))
		if self.open:self.screen.blit(self.background_txt,(self.bgrect.x,self.bgrect.y))
		self.gestione_eventi()
	
	def gestione_eventi(self):
		event=pygame.event.peek()
		if event.type==pygame.MOUSEBUTTONDOWN:
			pos=pygame.mouse.get_pos()

			if self.crossrect.collidepoint(pos):
				self.open=False
					
		
