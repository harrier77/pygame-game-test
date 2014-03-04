# coding: utf-8                     
# Questa è la classe che crea una figura sulla mappa
# e la muove con le frecce, serve a testare i movimenti
#----------------------------------------------------------

from mappa_base import *




class giocatore_base(mappa_base):
	def __init__(self):
		print "Inizializzazione oggetto giocatore_base..."
		mappa_base.__init__(self)
		# renderer
		self.screen_width=800
		self.screen_height=600
		self.layer_giocatore=1
		self.playerpos=(150,150)

	#  -----------------------------------------------------------------------------
	def crea_giocatore(self):
		#self.setta_posizione_camera_iniz()
		imagesAndDurations = [('gameimages/crono_front.gif',0.2),('gameimages/crono_front.gif',0.2)]
		animObj = pyganim.PygAnimation(imagesAndDurations)
		moveConductor = pyganim.PygConductor(animObj)
		moveConductor.play()
		return animObj
	#-------------------------------------------------------------------------------
	
	def metti_giocatore(self):
		self.giocatore_fermo=self.crea_giocatore()
		self.giocatore_animato=self.giocatore_fermo
		fermo_image= self.giocatore_fermo.ritorna_fotogramma()
		self.image_rect=fermo_image.get_rect()
		self.giocatore_sprite=tiledtmxloader.helperspygame.SpriteLayer.Sprite(fermo_image,self.image_rect)
		self.sprite_layers[self.layer_giocatore].add_sprite(self.giocatore_sprite)
		self.giocatore_sprite.rect.x=self.playerpos[0]
		self.giocatore_sprite.rect.y=self.playerpos[1]		
	#-------------------------------------------------------------------------------
	def muovi_giocatore(self):
		if self.cammina:
			self.giocatore_sprite.rect.x=self.giocatore_sprite.rect.x+self.direction_x*self.speed
			self.giocatore_sprite.rect.y=self.giocatore_sprite.rect.y+self.direction_y*self.speed
		if self.corsa:
			self.giocatore_sprite.rect.x=self.giocatore_sprite.rect.x+self.direction_x*self.speed*2
			self.giocatore_sprite.rect.y=self.giocatore_sprite.rect.y+self.direction_y*self.speed*2
		
		self.playerpos=(self.giocatore_sprite.rect.x-25,self.giocatore_sprite.rect.y-5)
#EndOfCLass------------------------		
		

def main():		
	pygame.init()
	oggetto = giocatore_base()
	giocatore=oggetto.crea_giocatore()

	world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode('mappe/mappa_x25.tmx')
	assert world_map.orientation == "orthogonal"
	# init pygame and set up a screen

	oggetto.screen_width = min(900, world_map.pixel_width)
	oggetto.screen_height = min(600, world_map.pixel_height)
	oggetto.screen=oggetto.cambia_pieno_schermo('0')
	oggetto.carica_mattonelle_in_layers(world_map)
	
	# variables for the main loop
	oggetto.clock = pygame.time.Clock()
	oggetto.running_loop = True
	oggetto.metti_giocatore()
	
	#Inizio while loop
	while oggetto.running_loop:
		oggetto.gestione_eventi()
		oggetto.muovi_giocatore()
		oggetto.disegna_frecce('sprite')
		# clear screen, might be left out if every pixel is redrawn anyway
		oggetto.screen.fill((0, 0, 0))
		oggetto.render_the_map()
		pygame.display.flip()
		oggetto.clock.tick(1000)
#EofFucntion main()		

if __name__ == '__main__':
	main()