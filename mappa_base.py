# coding: utf-8                     
# Questa è la classe mappa base basata su schermo base, 
# viene caricata la mappe e gestiti gli eventi di movimento
# e le funzioni che gestiscono il lancio di proiettili da un punto.
# Per usare i proiettili nella mappa serve usare uno sprite
#----------------------------------------------------------

from schermo_base import *

#import winsound
from miefunzioni import pyganim
from pygame.locals import*
from pygame.time import Clock
import tiledtmxloader
#import pprint

#--------------------------
# Classe ausiliaria per gli oggetti 
# non tiled della mappa
#------------------------
class mio_poligono:
        def __init__(self,oggetto_mappa):
                #print "Inizializzazione oggetto mio_poligono"
                self.immagine_rettangolare=pygame.Surface((50, 70), pygame.SRCALPHA)
                self.immagine_rettangolare.fill((255, 0, 0, 200))
                self.rect = self.immagine_rettangolare.get_rect()
                self.start_pos_x=250
                self.start_pos_y=250
                self.layer=1
                
                self.lista_poligoni=[]
               

        def visualizza_su_schermo(self,mioschermo):
                #solo per testare l'esistenza dell'immagine, per mostrare sulla mappa usa aggiungi_a_layers_mappa
                mioschermo.blit(self.immagine_rettangolare,(10,100)) 
        
        def converti_in_sprite(self,image,rect):
                return tiledtmxloader.helperspygame.SpriteLayer.Sprite(image, rect)
        
        def aggiungi_a_layers_mappa(self,oggetto_mappa):
                self.rect.midbottom = (self.start_pos_x, self.start_pos_y)
                immagine_poligono=self.converti_in_sprite(self.immagine_rettangolare,self.rect)
                # retrieve the layers
                sprite_layers=oggetto_mappa.sprite_layers 
                sprite_layers[self.layer].add_sprite(immagine_poligono)

#EofClass

#  -----------------------------------------------------------------------------
# classe mappa_base, vedi intestazione
# -------------------------------------------------------------------------------

class mappa_base(schermo_base):
	def __init__(self):
		schermo_base.__init__(self)
		#print "Inzializzazione oggetto mappa_base..."
		self.renderer = tiledtmxloader.helperspygame.RendererPygame()
		self.layer_giocatore=1
		self.corsa=False
		self.cammina=False
		self.speed=4
		self.direction_x=0
		self.direction_y=0
		self.lista_poligoni=[]
		self.puoi_andare=True
		self.lista_proiettili=['']
		self.file_mappa='mappe/mappa_x25.tmx'
		self.nascondi_collisioni=False
		self.cisonopoligoni=False
		
		self.cam_world_pos_x = 350
		self.cam_world_pos_y = 220

#---------------------------------------------------------
	def load_sound(filename, volume=0.5):
		sound = pygame.mixer.Sound("suoni/fireball.ogg")
		channel = sound.play()

#  -----------------------------------------------------------------------------
	def special_round(self,value):
		#For negative numbers it returns the value floored,
		#for positive numbers it returns the value ceiled.
		# same as:  math.copysign(math.ceil(abs(x)), x)
		# OR:
		# ## versus this, which could save many function calls
		# import math
		# ceil_or_floor = { True : math.ceil, False : math.floor, }
		# # usage
		# x = floor_or_ceil[val<0.0](val)
		if value < 0:
			return math.floor(value)
		return math.ceil(value)
#  -----------------------------------------------------------------------------
	def scrivi_frase_sprite(self,testo="Hello There"):
		b=self.scrivi_frase(testo)
		self.sprite_layers[2].add_sprite(b)
		

		
#------------------------------------------------------------------
	def disegna_frecce_sprite(self):
		#print len(self.arrows)
		for i in range(len(self.lista_proiettili)):
			self.sprite_layers[1].remove_sprite(self.lista_proiettili[i])
		for projectile in self.arrows:
			arrow1 = pygame.transform.rotate(self.arrow, 360-projectile[0]*57.29)
			arrow_rect=arrow1.get_rect()
			#arrow_rect.x=projectile[1]
			#arrow_rect.y=projectile[2]
			arrow_rect.centerx=projectile[1]
			arrow_rect.centery=projectile[2]
			self.arrow_new=tiledtmxloader.helperspygame.SpriteLayer.Sprite(arrow1,arrow_rect)
			self.sprite_layers[1].add_sprite(self.arrow_new)
			self.lista_proiettili.append(self.arrow_new)
		
#------------------------------------------------------------------
	def verifica_residuale_tasti_premuti(self):
		keys = pygame.key.get_pressed()
		if (keys[K_LEFT]):
			self.cammina=True
			self.direction_x =-1
		if (keys[K_RIGHT]):
			self.cammina=True
			self.direction_x =1
		if (keys[K_DOWN]):
			self.cammina=True
			self.direction_y =1
		if (keys[K_UP]):
			self.cammina=True
			self.direction_y =-1
			
			

#------------------------------------------------------------------
	def gestione_eventi(self):
		mousemotions = pygame.event.get(MOUSEMOTION)
		if mousemotions: #checks if the list is nonempty
			mousemotion = mousemotions[-1]
		if not hasattr(self, 'cam_world_pos_x'):
			self.setta_posizione_camera_iniz()
			
		self.coda_eventi=pygame.event.get()
		for event in self.coda_eventi:
			if event.type == pygame.QUIT:
				self.running_loop = False
			elif event.type == pygame.USEREVENT:
				continue
			elif event.type == pygame.KEYDOWN:
				#print pygame.key.get_pressed()
				if event.key == pygame.K_ESCAPE:
					self.running_loop = False
				elif event.type == pygame.KEYDOWN:
					self.cammina=True
					if event.key == pygame.K_LEFT:
						self.direction_x =-1
					elif event.key == pygame.K_RIGHT:
						self.direction_x =1
					elif event.key == pygame.K_UP:
						self.direction_y =-1
					elif event.key == pygame.K_DOWN:
						self.direction_y =1
					if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
						self.corsa=True
					if event.key == pygame.K_F1:
						pass
					elif event.key == pygame.K_F2:
						self.collisioni=False
					elif event.key == pygame.K_F3:
						self.scrivi_frase_sprite()
						self.scrivi_trasparente_sprite()
					elif event.key == pygame.K_F9:
						#print self.layer_giocatore
						self.sprite_layers[self.layer_giocatore].remove_sprite(self.giocatore_sprite)
						self.layer_giocatore=self.layer_giocatore+1
						self.scritta_cruscotto.pop(1)
						self.scritta_cruscotto.insert(1,"Livello giocatore:"+str(self.layer_giocatore))

			if event.type == pygame.KEYUP:
				self.cammina=False
				self.corsa=False                
				self.direction_x=0
				self.direction_y=0
			self.verifica_residuale_tasti_premuti()
			if event.type==pygame.MOUSEBUTTONDOWN:
				if pygame.mouse.get_pressed()[2]==1:
					self.lancia_frecce()
					self.load_sound('suoni/fireball.ogg')
			
		if self.puoi_andare:	
			if self.cammina:
				self.cam_world_pos_x=self.cam_world_pos_x+self.direction_x*self.speed 
				self.cam_world_pos_y=self.cam_world_pos_y+self.direction_y*self.speed 
			if self.corsa:
				self.cam_world_pos_x=self.cam_world_pos_x+self.direction_x*self.speed*2 
				self.cam_world_pos_y=self.cam_world_pos_y+self.direction_y*self.speed*2

			self.renderer.set_camera_position_and_size(self.cam_world_pos_x, self.cam_world_pos_y, \
						self.screen_width, self.screen_height)

#--------------------------------------- ---------------------------------
	def render_the_map(self):
		# render the map
		for sprite_layer in self.sprite_layers:
			if sprite_layer.is_object_group:
			# we dont draw the object group layers
			# you should filter them out if not needed
				continue
			else:
				self.renderer.render_layer(self.screen, sprite_layer)
#------------------------------------------------------------------
        def carica_mattonelle_in_layers(self,world_map):
                #self.setta_posizione_camera_iniz()
                # load the images of tiles using tiledtmxloader 
                i=0
                for mio in world_map.layers:
                        if mio.name=="Collision":
                                self.idx_coll_layer=i
                                #print mio.visible

                        i=i+1
                #print "layer collisioni ="+str(self.idx_coll_layer)
		resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()
		resources.load(world_map)
		self.sprite_layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)

                # filter layers
                #self.sprite_layers = [layer for layer in self.sprite_layers if not layer.is_object_group]
                if not self.cisonopoligoni:
                        self.sprite_layers = [layer for layer in self.sprite_layers if not layer.is_object_group]
               
                if self.nascondi_collisioni:
                        self.sprite_layers=[layer for layer in self.sprite_layers if not layer.layer_idx==self.idx_coll_layer]

                       
                    
                        
                if self.cisonopoligoni:         
                        self.carica_poligoni()
#------------------------------------------------------------------
	def setta_posizione_camera_iniz(self):
		# initial cam_offset is for scrolling
		#self.cam_world_pos_x = 350
		#self.cam_world_pos_y = 220
		# set initial cam position and size
		self.screen_width=pygame.display.Info().current_w
		self.screen_height=pygame.display.Info().current_h
		self.renderer.set_camera_position_and_size(self.cam_world_pos_x, self.cam_world_pos_y, \
						self.screen_width, self.screen_height)
		
#------------------------------------------------------------------
        def carica_poligoni(self):
                for index in range (len(self.sprite_layers[4].objects)):
                        poligono1=mio_poligono(self)
                        poligono1.start_pos_x=self.sprite_layers[4].objects[index].x+self.sprite_layers[0].tilewidth
                        poligono1.start_pos_y=self.sprite_layers[4].objects[index].y+self.sprite_layers[0].tileheight
                        poligono1.rect.left=poligono1.start_pos_x
                        poligono1.rect.top=poligono1.start_pos_y
                        self.lista_poligoni.append(poligono1)
        
#--------------------------------------------------------------
        def mostra_poligoni(self):
                for index in range (len(self.lista_poligoni)):
                        self.lista_poligoni[index].aggiungi_a_layers_mappa(self)
                        self.lista_poligoni[index].aggiungi_a_layers_mappa(self)
        
#--------------------------------------- ---------------------------------
	def togli_collisioni(self,world_map):
		i=0
		for mio in world_map.layers:
			if mio.name=="Collision":
				#print "layer collisioni="+str(i)
				self.idx_coll_layer=i
				world_map.layers.pop(i)
			i=i+1
		return world_map

#EofClass



def main():
	oggetto = mappa_base()

	oggetto.file_mappa="..\\tmwa\\maps\\001-1.tmx"
	world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(oggetto.file_mappa)
	
	#world_map=oggetto.togli_collisioni(world_map)

	assert world_map.orientation == "orthogonal"
	# init pygame and set up a screen
	pygame.init()
	screen_width = min(900, world_map.pixel_width)
	screen_height = min(600, world_map.pixel_height)
	oggetto.screen=oggetto.cambia_pieno_schermo('0')
	oggetto.carica_mattonelle_in_layers(world_map)

	#oggetto.setta_posizione_camera_iniz()
	# variables for the main loop
	oggetto.clock = pygame.time.Clock()
	#Inizio while loop
	while oggetto.running_loop:
		oggetto.gestione_eventi()
		# clear screen, might be left out if every pixel is redrawn anyway
		oggetto.screen.fill((0, 0, 0))
		oggetto.render_the_map()
		oggetto.disegna_frecce('sprite')
		pygame.display.flip()
		#end while loop
#EofFunction main()



if __name__ == '__main__':
	
	main()
