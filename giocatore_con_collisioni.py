# coding: utf-8                     
# Questa è la classe che gestisce le collisioni sulla mappa
# 
#----------------------------------------------------------

from giocatore_base import *

class giocatore_con_collisioni(giocatore_base):
	def __init__(self):
		print "Inizializzazione oggetto giocatore_con_collisioni..."
		giocatore_base.__init__(self)
		self.idx_coll_layer=3
		self.collisioni=True

	
	def mybeep(self):
		Freq = 600 # Set Frequency To 2500 Hertz
		Dur = 30 # Set Duration To 1000 ms == 1 second
		winsound.Beep(Freq,Dur)
	
	def is_walkable(self):
		"""
		Just checks if a position in world coordinates is walkable.
		"""
		try:
			coll_layer=self.sprite_layers[self.idx_coll_layer]
		except:
			print "livello collisioni" 
			return True
		pos_x=self.giocatore_sprite.rect.x 
		pos_y=self.giocatore_sprite.rect.y 
		tile_x = int(pos_x // coll_layer.tilewidth)
		tile_y = int(pos_y // coll_layer.tileheight)
		if not self.collisioni:
			return True

		if ((coll_layer.content2D[tile_y][tile_x]) or (coll_layer.content2D[tile_y+3][tile_x] )  or (coll_layer.content2D[tile_y][tile_x+1] )):
			return False
		else:
			return True
	
	
	def muovi_giocatore(self):
		old_x=self.giocatore_sprite.rect.x
		old_y=self.giocatore_sprite.rect.y
		
		if self.cammina:
			self.giocatore_sprite.rect.x=self.giocatore_sprite.rect.x+self.direction_x*self.speed
			self.giocatore_sprite.rect.y=self.giocatore_sprite.rect.y+self.direction_y*self.speed
		if self.corsa:
			self.giocatore_sprite.rect.x=self.giocatore_sprite.rect.x+self.direction_x*self.speed*2
			self.giocatore_sprite.rect.y=self.giocatore_sprite.rect.y+self.direction_y*self.speed*2
		
		if not (self.is_walkable()):
			self.giocatore_sprite.rect.x=old_x
			self.giocatore_sprite.rect.y=old_y
			self.puoi_andare=False
		else:
			self.puoi_andare=True

# EndOfClass------------------------		
		

def main():		
	pygame.init()
	oggetto = giocatore_con_collisioni()

	giocatore=oggetto.crea_giocatore()
	
	world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode('mappe/mappa_x25.tmx')
	assert world_map.orientation == "orthogonal"
	# init pygame and set up a screen

	screen_width = min(900, world_map.pixel_width)
	screen_height = min(600, world_map.pixel_height)
	oggetto.screen=oggetto.cambia_pieno_schermo('0')
	oggetto.carica_mattonelle_in_layers(world_map)
	oggetto.setta_posizione_camera_iniz()
	# variables for the main loop
	oggetto.clock = pygame.time.Clock()
	oggetto.running_loop = True
	oggetto.metti_giocatore()
	
	#Inizio while loop
	while oggetto.running_loop:
		oggetto.is_walkable()
		oggetto.gestione_eventi()
		oggetto.muovi_giocatore()
		# clear screen, might be left out if every pixel is redrawn anyway
		oggetto.screen.fill((0, 0, 0))
		oggetto.render_the_map()
		pygame.display.flip()
		

if __name__ == '__main__':
	main()
		
	