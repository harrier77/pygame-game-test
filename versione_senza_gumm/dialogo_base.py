# coding: utf-8                     
# Questa èl a classe per un dialogo base, 
#
#----------------------------------------------------------

from giocatore_animato import *
from miefunzioni import gui

class vuota():
	def esci(self):
		exit()

	
class mio_dialogo():
	def __init__(self,rect=pygame.Rect(20,20,600,30),oggetto_chiamante=vuota()):
		self.oggetto_chiamante=oggetto_chiamante
		title = gui.Label(" ")
		c=gui.Table(width=rect.width,height=rect.height)
		tabella = gui.Table(width=rect.width,height=rect.height)
		self.dialog=gui.Dialog(title,tabella)
		
		tabella.tr()
		b1=gui.Button("Menu")
		b1.connect(gui.CLICK,self.esci,None)
		tabella.td(b1)
		
		b2=gui.Button("Cruscotto")
		b2.connect(gui.CLICK,self.toggle_cruscotto)
		tabella.td(b2)
		
		b3=gui.Button("Nascondi collisioni si/no")
		b3.connect(gui.CLICK,self.nascondi_collisioni)
		tabella.td(b3)
		
		b4=gui.Button("Collisioni si/no")
		b4.connect(gui.CLICK,self.ignora_collisioni)
		tabella.td(b4)
		
		b5=gui.Button("Aiuto")
		tabella.td(b5)
		
		b5=gui.Button("Esci")
		b5.connect(gui.CLICK,self.esci,None)
		tabella.td(b5)
		self.app = gui.App()
		self.app.init(c)
		self.app.rect= rect
		

	def esci(self,param):
		if hasattr(self.oggetto_chiamante,"esci"):
			self.oggetto_chiamante.esci()
		if hasattr(self.oggetto_chiamante,"running_loop"):
			self.oggetto_chiamante.running_loop=False
	
	def toggle_cruscotto(self):
		print "cruscotto"
		if hasattr(self.oggetto_chiamante,"is_cruscotto"):
			if not self.oggetto_chiamante.is_cruscotto:
				self.oggetto_chiamante.is_cruscotto=True
			else:
				self.oggetto_chiamante.is_cruscotto=False
		self.dialog.close()
	
	def nascondi_collisioni(self):
		if self.oggetto_chiamante.sprite_layers[self.oggetto_chiamante.idx_coll_layer].visible:
			self.oggetto_chiamante.sprite_layers[self.oggetto_chiamante.idx_coll_layer].visible=False
		else:
			self.oggetto_chiamante.sprite_layers[self.oggetto_chiamante.idx_coll_layer].visible=True
		self.dialog.close()
			
	def ignora_collisioni(self):
		if self.oggetto_chiamante.ignora_collisioni:
			self.oggetto_chiamante.ignora_collisioni=False
		else:
			self.oggetto_chiamante.ignora_collisioni=True
		self.dialog.close()

def main():
	pygame.init()
	oggetto = giocatore_animato()
	oggetto.file_mappa="..\..\\tmwa\\maps\\004-2.tmx"
	world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(oggetto.file_mappa)
	oggetto.screen=oggetto.cambia_pieno_schermo('0')
	oggetto.clock = pygame.time.Clock()
	oggetto.carica_mattonelle_in_layers(world_map)
	mio_dialogo_ogg=mio_dialogo()
	mio_dialogo_ogg.oggetto=oggetto


	while oggetto.running_loop:
		oggetto.screen.fill(0)
		oggetto.render_the_map()
		oggetto.gestione_eventi()
		for event in oggetto.coda_eventi:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					oggetto.running_loop = False
				elif event.key == pygame.K_F4:
					mio_dialogo_ogg.dialog.open()
			mio_dialogo_ogg.app.event(event)
		mio_dialogo_ogg.app.paint()
		pygame.display.flip()


if __name__ == '__main__':
	main()