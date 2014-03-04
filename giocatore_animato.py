from giocatore_con_collisioni import *

class giocatore_animato(giocatore_con_collisioni):
	def __init__(self):
		print "Inizializzazione oggetto giocatore_animato..."
		giocatore_con_collisioni.__init__(self)
		self.animated_object=self.crea_giocatore_animato()
		self.file_mappa='mappe/mappa_x25.tmx'
		self.vedi_collisioni=True
		self.pos_cruscotto=[1,1]
		
#-----------------------------------------------------------------------------------	

	def crea_giocatore_animato(self):
		# load the "standing" sprites (these are single images, not animations)
		front_standing = pygame.image.load('gameimages/crono_front.gif')
		back_standing = pygame.image.load('gameimages/crono_back.gif')
		left_standing = pygame.image.load('gameimages/crono_left.gif')
		right_standing = pygame.transform.flip(left_standing, True, False)

		playerWidth, playerHeight = front_standing.get_size()
		# creating the PygAnimation objects for walking/running in all directions
		animTypes = 'back_run back_walk front_run front_walk left_run left_walk'.split()
		animObjs = {}
		for animType in animTypes:
		    imagesAndDurations = [('gameimages/crono_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
		    animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)
		# create the right-facing sprites by copying and flipping the left-facing sprites
		animObjs['right_walk'] = animObjs['left_walk'].getCopy()
		animObjs['right_walk'].flip(True, False)
		animObjs['right_walk'].makeTransformsPermanent()
		animObjs['right_run'] = animObjs['left_run'].getCopy()
		animObjs['right_run'].flip(True, False)
		animObjs['right_run'].makeTransformsPermanent()
		moveConductor = pyganim.PygConductor(animObjs)
		moveConductor.play()
		return animObjs

#-----------------------------------------------------------------------------------	

	def metti_fotogrammi_giocatore_animato(self):
		for event in self.coda_eventi:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RIGHT:
					self.giocatore_animato=self.animated_object['right_walk']
					if self.corsa:
						self.giocatore_animato=self.animated_object['right_run']
				elif event.key == pygame.K_LEFT:
					self.giocatore_animato=self.animated_object['left_walk']
					if self.corsa:
						self.giocatore_animato=self.animated_object['left_run']
				elif event.key == pygame.K_DOWN:
					self.giocatore_animato=self.animated_object['front_walk']
					if self.corsa:
						self.giocatore_animato=self.animated_object['front_run']
				elif event.key == pygame.K_UP:
					self.giocatore_animato=self.animated_object['back_walk']
					if self.corsa:
						self.giocatore_animato=self.animated_object['back_run']
		if self.cammina:
			animated_image= self.giocatore_animato.ritorna_fotogramma()
			self.sprite_layers[self.layer_giocatore].remove_sprite(self.giocatore_sprite)
			#NB: self.image.rect viene gestita dall'oggetto giocatore_base
			self.giocatore_sprite=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_image, self.image_rect)
			self.sprite_layers[self.layer_giocatore].add_sprite(self.giocatore_sprite)
		self.playerpos=(self.giocatore_sprite.rect.x-25,self.giocatore_sprite.rect.y-5)
	
	#  -----------------------------------------------------------------------------
	def scrivi_trasparente_sprite(self,testo="Hello There"):
		b=self.scritta_trasparente(testo)[0]
		livello=self.idx_coll_layer-1
		self.sprite_layers[livello].add_sprite(b)
	
	def scritta_trasparente(self,testo):
		sfondo = pygame.Surface([800,50], pygame.SRCALPHA, 32)
		sfondo = sfondo.convert_alpha()
		font = pygame.font.Font(None, 22)
		text = font.render(testo, 1, (250, 250, 250))
		sfondo.blit(text,(0,0))
		self.pos_cruscotto[0]=self.playerpos[0]*0.70
		self.pos_cruscotto[1]=self.playerpos[1]*0.70
		#self.pos_cruscotto[0]=self.cam_world_pos_x*0.10
		#self.pos_cruscotto[1]=self.cam_world_pos_y*0.10
		
		bg_scritta_trasp_rect=sfondo.get_rect()
		bg_scritta_trasp_rect.x=self.pos_cruscotto[0]
		bg_scritta_trasp_rect.y=self.pos_cruscotto[1]
		b=tiledtmxloader.helperspygame.SpriteLayer.Sprite(sfondo,bg_scritta_trasp_rect)
		return b,sfondo
	
	def scrivi_cruscotto_blit(self,testi=("hello")):
		y=0
		for r in testi:
			b=self.scritta_trasparente(r)[1]
			y=y+15
			self.screen.blit(b,(10,y))

		

	def main(self):		
		
		# init pygame and set up a screen
		world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(self.file_mappa)
		assert world_map.orientation == "orthogonal"

		self.screen_width = min(900, world_map.pixel_width)
		self.screen_height = min(600, world_map.pixel_height)
		self.screen=self.cambia_pieno_schermo('0')
		
		self.vedi_collisioni=False
		
		if not self.vedi_collisioni:
			world_map=self.togli_collisioni(world_map)
		
		self.carica_mattonelle_in_layers(world_map)

		# variables for the main loop
		self.clock = pygame.time.Clock()
		self.running_loop = True
		self.metti_giocatore()
		if not self.vedi_collisioni:
			#self.bg_scritta_trasp_rect.top=20
			scritta_cruscotto=['Collisioni disattivate, livello '+str(self.idx_coll_layer),' ']
			#self.scrivi_trasparente_sprite(scritta_cruscotto)
	

		#Inizio while loop
		while self.running_loop:
			self.is_walkable()
			self.gestione_eventi()
			self.muovi_giocatore()
			self.metti_fotogrammi_giocatore_animato()
			self.disegna_frecce('sprite')
			
			# clear screen, might be left out if every pixel is redrawn anyway
			self.screen.fill((0, 0, 0))
			self.render_the_map()
			self.scrivi_cruscotto_blit(scritta_cruscotto)
			pygame.display.flip()
			self.clock.tick(500)
		
#EndofCLass------------------------


#-----------------------------------------------------------------------------------			

if __name__ == '__main__':
	pygame.init()
	oggetto = giocatore_animato()
	oggetto.playerpos=(100,100)

	oggetto.file_mappa="D:\\games\\tmwa\\maps\\001-2.tmx"
	oggetto.main()