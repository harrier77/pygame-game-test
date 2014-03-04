import sys
import os
import math
import pygame
import winsound
from miefunzioni import pyganim
from pygame.locals import*
from pygame.time import Clock
#from miefunzioni import *
import pprint
from inspect import getmembers


try:
    import _path
except:
    pass

import tiledtmxloader

#  -----------------------------------------------------------------------------
def printer(obj, ident=''):
    """
    Helper function, prints a hirarchy of objects.
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
#--------------------------------------------------------------------------------



#  -----------------------------------------------------------------------------

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

def main():
        x=mia_mappa_oggetto()
        x.layer_giocatore=1
        x.idx_layer_collisioni=3
        x.carica_mappa("mappe/mappa_x25.tmx")
        
#  -----------------------------------------------------------------------------
      
#  -----------------------------------------------------------------------------
class mia_mappa_oggetto:
        
        def __init__(self):
                print "Inzializzazione oggetto..."
                # renderer
                self.screen_width=800
                self.screen_height=600
                self.renderer = tiledtmxloader.helperspygame.RendererPygame()
                self.layer_giocatore=2
                self.animated_object=self.crea_giocatore()
                
                self.giocatore_animato=self.animated_object['front_walk']
                animated_image= self.giocatore_animato.ritorna_fotogramma()
                rect = animated_image.get_rect()
                self.hero_pos_x=300
                self.hero_pos_y=300
                rect.midbottom = (self.hero_pos_x, self.hero_pos_y)
                self.hero=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_image, rect)
                
                self.strega=self.crea_strega()
                animated_strega=self.strega.ritorna_fotogramma()
                animated_strega.get_rect().midbottom=(self.hero_pos_x, self.hero_pos_y)
                self.stregasprite=tiledtmxloader.helperspygame.SpriteLayer.Sprite\
                                        (animated_strega,animated_strega.get_rect())
                #self.sprite_layers[1].add_sprite(self.hero)
                #non va perche' manca la mappa su cui disegnarlo
                
                self.corsa=False
                self.cammina=False
                self.direction_x=0
                self.direction_y=0
                self.x_strega=300
                self.fps='00'
                self.collisioni=True
                self.idx_layer_collisioni=2
                self.lista_poligoni=[]
                self.poligoni=False
        #------------------------------------------------------------------     
        
        
        #---------------------------------------------------------------------
        def crea_giocatore(self):

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

                # have the animation objects managed by a conductor.
                # With the conductor, we can call play() and stop() on all the animtion
                # objects at the same time, so that way they'll always be in sync with each
                # other.
                moveConductor = pyganim.PygConductor(animObjs)

                moveConductor.play()
                return animObjs

        #  -----------------------------------------------------------------------------
        def crea_strega(self):
                #primo_fotogramma=pygame.image.load('koba.png')
                imagesAndDurations = [('immagini/kopa.png',0.2),('immagini/kopa.png',0.2)]
                animObj = pyganim.PygAnimation(imagesAndDurations)
                moveConductor = pyganim.PygConductor(animObj)
                moveConductor.play()
                return animObj
        #------------------------------------------------------------------
        
        def coord_strega(self,i):
                x=1000-i
                coord=(x,200)
                return coord
        #------------------------------------------------------------------
        
        def mybeep(self):
                Freq = 600 # Set Frequency To 2500 Hertz
                Dur = 30 # Set Duration To 1000 ms == 1 second
                winsound.Beep(Freq,Dur)
        #------------------------------------------------------------------
        
        def check_collision(self,hero_pos_x, hero_pos_y, step_x, step_y, \
                                    hero_width, hero_height, coll_layer):
                """
                Checks collision of the hero against the world. Its not the best way to
                handle collision detection but for this demo it is good enough.
                :Returns: steps to add to heros current position.
                """
                
                # create hero rect
                hero_rect = pygame.Rect(0, 0, hero_width, hero_height)
                hero_rect.midbottom = (hero_pos_x, hero_pos_y)

                # find the tile location of the hero
                tile_x = int((hero_pos_x) // coll_layer.tilewidth)
                tile_y = int((hero_pos_y) // coll_layer.tileheight)

                # find the tiles around the hero and extract their rects for collision
                tile_rects = []
                for diry in (-1, 0 , 1):
                        for dirx in (-1, 0, 1):
                            if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                                tile_rects.append(coll_layer.content2D[tile_y + diry][tile_x + dirx].rect)

                # save the original steps and return them if not canceled
                to_return_step_x = step_x
                to_return_step_y = step_y

                # x direction, floor or ceil depending on the sign of the step
                step_x = self.special_round(step_x)

                # detect a collision and dont move in x direction if colliding
                if hero_rect.move(step_x, 0).collidelist(tile_rects) > -1:
                        to_return_step_x = 0 
                        self.mybeep()

                # y direction, floor or ceil depending on the sign of the step
                step_y = self.special_round(step_y)

                # detect a collision and dont move in y direction if colliding
                if hero_rect.move(0, step_y).collidelist(tile_rects) > -1:
                        to_return_step_y = 0
                        self.mybeep()

                #print to_return_step_x
                #print to_return_step_y
                # return the step the hero should do
                return to_return_step_x, to_return_step_y

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
        
        #---------------------------------------
        def metti_strega(self):
                animated_strega=self.strega.ritorna_fotogramma()
                strega_rect=animated_strega.get_rect()
                self.x_strega=self.x_strega+1
                if self.x_strega>1000:
                        self.x_strega=0
                strega_rect.midbottom=self.coord_strega(self.x_strega)
                
                self.sprite_layers[2].remove_sprite(self.stregasprite)
                self.stregasprite=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_strega,strega_rect)
                self.sprite_layers[2].add_sprite(self.stregasprite)
        
        #---------------------------------------
        
        def metti_fotogrammi_hero_animato(self):
                font = pygame.font.Font(None, 26)
                
                if self.cammina:
                        animated_image= self.giocatore_animato.ritorna_fotogramma()
                        rect = animated_image.get_rect()
                        rect.midbottom = (self.hero_pos_x, self.hero_pos_y)
                        
                        self.sprite_layers[self.layer_giocatore].remove_sprite(self.hero)
                        self.hero=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_image, rect)
                        self.sprite_layers[self.layer_giocatore].add_sprite(self.hero)
                        testog = font.render("Giocatore cammina", 1, (255, 255, 255))
                        if self.corsa:
                                testog = font.render("Giocatore corre", 1, (255, 255, 255))
                else:
                        testog = font.render("Giocatore fermo", 1, (255, 255, 255))
                        
                self.screen.blit(testog, (10,60))
        #--------------------------------------- ---------------------------------
        
        def gestione_eventi(self):
                #print pygame.event.get()
                self.coda_eventi=pygame.event.get()
                for event in self.coda_eventi:
                    if event.type == pygame.QUIT:
                        self.running_loop = False
                    elif event.type == pygame.USEREVENT:
                        continue
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running_loop = False
                        elif event.type == pygame.KEYDOWN:
                                self.cammina=True
                                self.fps=round(self.clock.get_fps(),2)
                                
                                if event.key == pygame.K_LEFT:
                                        self.giocatore_animato=self.animated_object['left_walk']
                                        self.direction_x =-1
                                elif event.key == pygame.K_RIGHT:
                                        self.giocatore_animato=self.animated_object['right_walk']
                                        self.direction_x =1
                                elif event.key == pygame.K_UP:
                                        self.giocatore_animato=self.animated_object['back_walk']
                                        self.direction_y =-1
                                elif event.key == pygame.K_DOWN:
                                        self.giocatore_animato=self.animated_object['front_walk']
                                        self.direction_y =1
                                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                                        self.corsa=True
                                if event.key == pygame.K_F1:
                                        self.mybeep()
                                        world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode('mappe/001-1.tmx')                                        
                                        self.carica_mattonelle_in_layers(world_map)
                                elif event.key == pygame.K_F2:
                                        self.collisioni=False
                                        
                                        
                    elif event.type == pygame.KEYUP:
                        self.cammina=False
                        self.corsa=False                
                        self.direction_x=0
                        self.direction_y=0
        
        #--------------------------------------- ---------------------------------
        def setta_x_y_hero_non_animato(self,idx_layer_collisioni):
                hero_width = self.hero.rect.width
                #attenzione questa non e' la vera altezza ma?
                hero_height = 5
                # make sure the hero moves with same speed in all directions (diagonal!)
                dir_len = math.hypot(self.direction_x, self.direction_y)
                dir_len = dir_len if dir_len else 1.0
             
                if self.corsa:
                        self.speed=16
                else:
                        self.speed=8
                
                self.step_x = self.speed*self.direction_x / dir_len
                self.step_y = self.speed*self.direction_y / dir_len
                
                #controlla se collisione:
                if self.collisioni:
                        #print "layer collisioni:"+str(layer_collisioni)
                        self.step_x, self.step_y = self.check_collision(self.hero_pos_x, self.hero_pos_y, self.step_x, self.step_y, hero_width, hero_height, self.sprite_layers[idx_layer_collisioni])
                #aumenta la posizione del personaggio di +1 o -1
                self.hero_pos_x += self.step_x
                self.hero_pos_y += self.step_y       
                self.hero.rect.midbottom = (self.hero_pos_x, self.hero_pos_y)

                # adjust camera according to the hero's position, follow him
                self.renderer.set_camera_position(self.hero.rect.centerx, self.hero.rect.centery)
        
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
        
        def scrivi_testo_di_controllo(self):
                font = pygame.font.Font(None, 26)
                # Display some text
                if hasattr(self, 'step_x'):
                        textfps=font.render("Fotogrammi per secondo:"+str(self.fps), 1, (255, 255, 255))
                        textx = font.render("Movimento x:"+str(self.step_x), 1, (255, 255, 255))
                        texty = font.render("Movimento y:"+str(self.step_y), 1, (255, 255, 255))
                        self.screen.blit(textx, (10,10))
                        self.screen.blit(texty, (10,30))
                        self.screen.blit(textfps, (10,90))
        #------------------------------------------------------------------        
        
        def inserisci_prima_img_hero(self):
                # add the hero the the right layer, it can be changed using 0-9 keys
                self.sprite_layers[self.layer_giocatore].add_sprite(self.hero)
        #------------------------------------------------------------------
        
        
        def cambia_pieno_schermo(self,fullscr,screen_width, screen_height):
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
        
        def carica_mattonelle_in_layers(self,world_map):
                # load the images of tiles using tiledtmxloader 
                resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()
                resources.load(world_map)
                self.sprite_layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)
                # filter layers
                #self.sprite_layers = [layer for layer in self.sprite_layers if not layer.is_object_group]
                if self.poligoni:
                    self.carica_poligoni()
        #------------------------------------------------------------------
                
        def setta_posizione_camera_iniz(self):
                # initial cam_offset is for scrolling
                cam_world_pos_x = self.hero.rect.centerx
                cam_world_pos_y = self.hero.rect.centery
                # set initial cam position and size
                self.renderer.set_camera_position_and_size(cam_world_pos_x, cam_world_pos_y, \
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
        
        #--------------
        def mostra_poligoni(self):
                for index in range (len(self.lista_poligoni)):
                        self.lista_poligoni[index].aggiungi_a_layers_mappa(self)
                        self.lista_poligoni[index].aggiungi_a_layers_mappa(self)
        
        #--------------------------------------- ---------------------------------
        def carica_mappa(self,file_name,fullscr='0'):
            # parser the map (it is done here to initialize the
            # window the same size as the map if it is small enough)
            world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(file_name)
            assert world_map.orientation == "orthogonal"
            
            surf_icon=pygame.image.load('immagini/icona2.gif')    
            pygame.display.set_icon(surf_icon)
            # init pygame and set up a screen
            pygame.init()
            pygame.display.set_caption("Mappa caricata: " + file_name + " - keys: arrows, 0-9")
            
            self.screen_width = min(900, world_map.pixel_width)
            
            self.screen_height = min(600, world_map.pixel_height)
           
            #-----------------------------------------------------------
            self.screen=self.cambia_pieno_schermo(fullscr,self.screen_width, self.screen_height)
            
            self.carica_mattonelle_in_layers(world_map)
            
            
            self.setta_posizione_camera_iniz()
            
            # layer add/remove hero keys
            num_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, \
                            pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

            # variables for the main loop
            self.clock = pygame.time.Clock()

            # set up timer for fps printing
            pygame.time.set_timer(pygame.USEREVENT, 1000)
            
            font = pygame.font.Font(None, 26)
            
            self.running_loop = True
            
            # add the hero the the right layer, it can be changed using 0-9 keys
            self.inserisci_prima_img_hero()
            
            
            #Inizio while loop
            while self.running_loop:
                dt = self.clock.tick(60)
                
                self.gestione_eventi()

                self.setta_x_y_hero_non_animato(self.idx_layer_collisioni)
                
                # clear screen, might be left out if every pixel is redrawn anyway
                self.screen.fill((0, 0, 0))
                
                self.render_the_map()
                
                self.scrivi_testo_di_controllo()

                self.metti_fotogrammi_hero_animato()
                self.metti_strega()
                ##self.mostra_poligoni()
                
                pygame.display.flip()
                #end while loop
        
        #EOFunc -----------------------------------------------------------------------------------------


if __name__ == '__main__':
      main()


