import pygame
from pygame.sprite import Sprite
from pygame.locals import *
import sys
sys.path.append("./miogummworld") 
import paths
import gummworld2
from gummworld2 import context, data, model, geometry, toolkit
from gummworld2 import Engine, State, TiledMap, Vec2d,BasicMapRenderer
from miefunzioni import miovar_dump

class Mia_image():
        front_standing = pygame.image.load('gameimages/crono_front.gif')
        def __init__(self,map_pos=(100,100),screen_pos=(100,100)):
                self.herosprite=pygame.sprite.Sprite()
                self.herosprite.image=self.front_standing
                self.herosprite.rect=self.herosprite.image.get_rect()
                self.herosprite.rect.x=1
                self.herosprite.rect.y=1
                self.position = map_pos
                self.screen_position = screen_pos
                
class App_gum(Engine):
        lista_objects_groups=list()
        def __init__(self,resolution=(800,600)):
                self.resolution = Vec2d(resolution)
                tiled_map=self.carica_mappa()
                #miovar_dump(self.lista_objects_groups[0].objects)
                miohero=Mia_image()
                self.mioherosprite=miohero.herosprite
                tiled_map.layers[2].add(self.mioherosprite)
                self.inizializza_engine(tiled_map)
                self.cammina=False
                self.movex=0
                self.movey=0
                #State.camera.target.position=self.mioherosprite.rect.x,self.mioherosprite.rect.y
                #State.camera.position=(10,10)
                State.camera.position=(150,100)
                
        def carica_mappa(self,mappa=".\\mappe\\001-1.tmx"):
                tiled_map = TiledMap(mappa)
                ##rimuovi i lvelli degli oggetti per evitare l'errore in BasicMapRendererTile
                for L in tiled_map.layers: 
                       if L.is_object_group : 
                               tiled_map.layers.pop(L.layeri)
                               self.lista_objects_groups.append(L)
                ##fine rimuovi object layer
                return tiled_map
                
        def inizializza_engine(self,tiled_map):
                Engine.__init__(self,
                    caption='Tiled Map with Renderer',
                    resolution=self.resolution,
                    camera_target=Mia_image((1,1), self.resolution//2),
                    map=tiled_map,
                    frame_speed=0)
                State.speed = 1
                ## Create the renderer.
                self.renderer = BasicMapRenderer(tiled_map, max_scroll_speed=State.speed)
                self.visible_objects = toolkit.get_object_array()

        def update(self, dt):
                State.camera.update()
                ## Set render's rect.
                self.renderer.set_rect(center=State.camera.rect.center)
        
        def draw(self, interp):
                State.screen.clear()
                self.renderer.draw_tiles()
                if self.cammina:
                        self.mioherosprite.rect.x=self.mioherosprite.rect.x+self.movex
                        self.mioherosprite.rect.y=self.mioherosprite.rect.y+self.movey
                State.camera.target.position=(self.mioherosprite.rect.x+100,self.mioherosprite.rect.y+100)
                toolkit.draw_object_array(self.visible_objects)
                self.controlla_collisione_object()
                State.screen.flip()
        
        def controlla_collisione_object(self):
                if self.lista_objects_groups[0].objects.collide(self.mioherosprite):
                        for O in self.lista_objects_groups[0].objects.collide(self.mioherosprite):
                                #self.mioherosprite.image=None
                                oggetto_toccato=O
                                self.esegui_eventi_mappa(oggetto_toccato)
                                
        def esegui_eventi_mappa(self,oggetto_toccato):
                if oggetto_toccato.name=='Pozzo':
                        self.cammina=False
                        self.lista_objects_groups=list()
                        tiled_map=self.carica_mappa(".\\mappe\\mappa_x25.tmx")
                        self.mioherosprite.rect.x=10
                        self.mioherosprite.rect.y=10
                        tiled_map.layers[2].add(self.mioherosprite)
                        State.camera.target.position=(self.mioherosprite.rect.x,self.mioherosprite.rect.y)
                        self.inizializza_engine(tiled_map)

        def on_key_down(self, unicode, key, mod):
                self.cammina=True
                if key == K_DOWN:               
                        self.movey += State.speed
                elif key == K_UP: 
                        self.movey += -State.speed
                elif key == K_RIGHT: 
                        self.movex += State.speed
                elif key == K_LEFT: 
                        self.movex += -State.speed
                elif key == K_ESCAPE: context.pop()

        def on_key_up(self, key, mod):
                self.cammina=False
                if key == K_DOWN: 
                    self.movey -= State.speed
                elif key == K_UP: 
                    self.movey -= -State.speed
                elif key == K_RIGHT: 
                    self.movex -= State.speed
                elif key == K_LEFT: 
                    self.movex -= -State.speed
                    
        
        def on_quit(self):
                context.pop()

#-----------------------------------------------------------------------------------			

if __name__ == '__main__':
        oggetto=App_gum()
        gummworld2.run(oggetto)