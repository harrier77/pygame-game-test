# coding: utf-8
import pygame
from pygame.locals import *
from pygame import sprite
import sys
sys.path.append(".\\miogummworld") 
sys.path.append(".\\miogummworld\\gamelib") 
import paths
import cProfile, pstats
import gummworld2
from gummworld2 import context, data, model, geometry, toolkit
from gummworld2 import Engine, State, TiledMap, BasicMapRenderer, Vec2d
from miefunzioni import pyganim
from miefunzioni import miovar_dump
from dialogo_2 import Mio_dialogo

#-------------------------------------------------------------------------------
class Miohero():
        # load the "standing" sprites (these are single images, not animations)
        sit_standing=pygame.image.load('gameimages/crono_sleep.000.gif')
        front_standing = pygame.image.load('gameimages/crono_front.gif')
        back_standing = pygame.image.load('gameimages/crono_back.gif')
        left_standing = pygame.image.load('gameimages/crono_left.gif')
        right_standing = pygame.transform.flip(left_standing, True, False)
        def __init__(self,map_pos,screen_pos):
                self.animated_object=self.crea_giocatore_animato()
                self.giocatore_animato=self.animated_object['front_walk']
                self.image= self.giocatore_animato.ritorna_fotogramma()
                self.rect=self.image.get_rect()
                self.herosprite=pygame.sprite.Sprite()
                self.herosprite.image=self.image
                self.herosprite.rect=self.rect
                self.position = map_pos
                self.screen_position = screen_pos
        def crea_giocatore_animato(self):
                playerWidth, playerHeight = self.front_standing.get_size()
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
                self.moveConductor = pyganim.PygConductor(animObjs)
                self.moveConductor.play()
                return animObjs
#-------------------------------------------------------------------------------

class App_gum(Engine):
        def __init__(self,resolution=(400,200),dir=".\\mappe\\",mappa="Villaggio_gioco_new.tmx",coll_invis=True,ign_coll=False):
                #necessario per resettare la condizione messa dalla libreria PGU
                pygame.key.set_repeat()
                #---------------
                
                resolution = Vec2d(resolution)
                tiled_map = TiledMap(dir+mappa)
                self.lista_oggetti=list()
                
                ##rimuovi i lvelli degli oggetti per evitare l'errore in BasicMapRendererTile
                for L in tiled_map.layers: 
                        if L.is_object_group : 
                                tiled_map.layers.pop(L.layeri)
                                self.lista_oggetti.append(L)
                ##fine rimuovi object layer
                
                hero_ini_pos=200,200
                for O in self.lista_oggetti[0].objects.objects:
                        if O.name=="Inizio":
                                hero_ini_pos= O.rect.x,O.rect.y
                        
                
                Engine.__init__(self,
                    caption='Tiled Map with Renderer',
                    resolution=resolution,
                    camera_target=Miohero((hero_ini_pos), resolution//2),
                    map=tiled_map,
                    frame_speed=0)
                
                #State.map.layers[4].visible=False
                # I like huds.
                State.camera.position=Vec2d(State.camera.position)
                toolkit.make_hud()
                
                # Create a speed box for converting mouse position to destination
                # and scroll speed.
                self.speed_box = geometry.Diamond(0,0,4,2)
                self.speed_box.center = Vec2d(State.camera.rect.size) // 2
                self.max_speed_box = float(self.speed_box.width) / 2.0

                # Mouse and movement state. move_to is in world coordinates.
                self.move_to = None
                self.speed = None
                self.target_moved = (0,0)
                self.mouse_down = False
                self.grid_cache = {}
                self.label_cache = {}
                
                State.speed = 4.33
                self.movex=0
                self.movey=0
                self.cammina=False
                self.imm_fermo=Miohero.sit_standing
                self.animato=self.camera.target.animated_object
                
                if coll_invis:self.rendi_invisibili_collisioni()
                #con questa proprietà le collisioni vengono ignorate
                self.ignora_collisioni=ign_coll
                self.corsa=False
                
                ## Create the renderer.
                self.renderer = BasicMapRenderer(tiled_map, max_scroll_speed=State.speed)

        
        #-----------------------------------------------------------------
        def rendi_invisibili_collisioni(self):
                #per rendere invisibili le collisioni all'inizio, non funziona con il renderer avviato
                for L in State.map.layers:
                                if L.name=='Collision': 
                                        self.idx_c= L.layeri
                                        State.map.layers[self.idx_c].visible=False
                #print State.map.layers[4].visible
                
                
        #------------------------------------------------------------------ 
        def update(self, dt):
                if self.movex or self.movey:
                        
                        if self.is_walkable():
                                wx=State.camera.target.position[0]+self.movex
                                wy=State.camera.target.position[1]+self.movey
                                State.camera.target.position=(wx,wy)
                                self.camera.target.herosprite.rect.x=wx
                                self.camera.target.herosprite.rect.y=wy
                State.camera.update()
                ## Set render's rect.
                self.renderer.set_rect(center=State.camera.rect.center)
                State.camera.position=Vec2d(State.camera.position)
                State.hud.update(dt)

        #------------------------------------------------------------------        
        def update_mouse_movement(self, pos):
                # Angle of movement.
                angle = geometry.angle_of(self.speed_box.center, pos)
                # Final destination.
                self.move_to = None
                for edge in self.speed_box.edges:
                    # line_intersects_line() returns False or (True,(x,y)).
                    cross = geometry.line_intersects_line(edge, (self.speed_box.center, pos))
                    if cross:
                        x,y = cross[0]
                        self.move_to = State.camera.screen_to_world(pos)
                        self.speed = geometry.distance(
                            self.speed_box.center, (x,y)) / self.max_speed_box
                        break                
        #------------------------------------------------------------------ 
        def draw(self, interp):
                State.screen.clear()
                self.renderer.draw_tiles()
                if State.show_grid:
                    toolkit.draw_grid(self.grid_cache)
                if State.show_labels:
                    toolkit.draw_labels(self.label_cache)
                State.hud.draw()
                self.draw_avatar()
                #self.miodialogo.app.paint()
                State.screen.flip()
                
        #------------------------------------------------------------------ 
        def draw_avatar(self):
                self.verifica_residuale_tasti_premuti()
                if self.cammina:
                        State.camera.target.image=self.camera.target.giocatore_animato.ritorna_fotogramma()
                #elif (self.cammina==False):
                else:
                        State.camera.target.image=self.imm_fermo
                State.camera.surface.blit(State.camera.target.image, State.camera.target.screen_position)
        #------------------------------------------------------------------ 
        def is_walkable(self):
                if self.ignora_collisioni:
                        return True
                is_walkable=True
                pos_x=self.camera.target.position[0]+self.movex
                pos_y=self.camera.target.position[1]+self.movey
                coll_layer=self.renderer.basic_map.named_layers['Collision']
                tile_x=int(pos_x // coll_layer.tilewidth)
                tile_y = int(pos_y // coll_layer.tileheight)
                if coll_layer.content2D[tile_x][tile_y]:
                        #print "x y"
                        is_walkable=True
                if (coll_layer.content2D[tile_x][tile_y+1]) :
                        #print "x y+1"
                        is_walkable=True
                if (coll_layer.content2D[tile_x+1][tile_y]) :
                        #print "x+1 y"
                        is_walkable=True
                if (coll_layer.content2D[tile_x+1][tile_y+1]) :
                        #print "x+1 y+1"
                        is_walkable=True
                if (coll_layer.content2D[tile_x+1][tile_y+2]) : 
                        #print "x+1 y+2"
                        is_walkable=False
                if (coll_layer.content2D[tile_x][tile_y+2]) : 
                        #print "x y+2"
                        is_walkable=False

                return is_walkable
                
        #------------------------------------------------------------------
        def verifica_residuale_tasti_premuti(self):
                keys = pygame.key.get_pressed()
                #print keys[K_LEFT]
                #self.camera_target.moveConductor.play()
                if (keys[K_LEFT]):
                        self.camera.target.giocatore_animato=self.animato['left_walk']
                        self.cammina=True
                if (keys[K_RIGHT]):
                        self.camera.target.giocatore_animato=self.animato['right_walk']
                        self.cammina=True
                if (keys[K_DOWN]):
                        self.camera.target.giocatore_animato=self.animato['front_walk']
                        self.cammina=True
                if (keys[K_UP]):
                        self.camera.target.giocatore_animato=self.animato['back_walk']
                        self.cammina=True
                
                self.corsa=False
                if (keys[K_LSHIFT]):
                        self.corsa=True
                        
                        


                #self.cammina=False        
        #------------------------------------------------------------------ 
        
        
        def on_key_down(self, unicode, key, mod):
                #print self.corsa
                
                #self.camera_target.moveConductor.play()

                if key == K_DOWN:               
                        self.cammina=True
                        self.camera.target.giocatore_animato=self.animato['front_walk']
                        self.movey += State.speed
                        if self.corsa: 
                                self.movey += State.speed
                                self.camera.target.giocatore_animato=self.animato['front_run']
                elif key == K_UP: 
                        self.cammina=True
                        self.camera.target.giocatore_animato=self.animato['back_walk']
                        self.movey += -State.speed
                        if self.corsa:
                                self.movey += -State.speed
                                self.camera.target.giocatore_animato=self.animato['back_run']
                elif key == K_RIGHT: 
                        self.cammina=True
                        self.camera.target.giocatore_animato=self.animato['right_walk']
                        self.movex += State.speed
                        if self.corsa: 
                                self.camera.target.giocatore_animato=self.animato['right_run']
                                self.movex += State.speed
                elif key == K_LEFT: 
                        self.cammina=True
                        self.camera.target.giocatore_animato=self.animato['left_walk']
                        self.movex += -State.speed
                        if self.corsa:
                                self.movex += -State.speed
                                self.camera.target.giocatore_animato=self.animato['left_run']
                                
                
                        
                
                
                elif key == pygame.K_F4:
                        self.rendi_invisibili_collisioni()
                        #context.pop()
                        #self.__init__()
                        #miodialogo=Mio_dialogo(screen=State.screen,oggetto_chiamante=self)
                        #miodialogo.main(open=True)
                        #pygame.key.set_repeat()
                        
                        
                elif key == K_g:
                    State.show_grid = not State.show_grid
                elif key == K_l:
                    State.show_labels = not State.show_labels        
                elif key == K_ESCAPE: 
                        context.pop()
                
        #------------------------------------------------------------------ 
        def on_mouse_button_down(self, pos, button):
                self.mouse_down = True
        #------------------------------------------------------------------ 
        def on_mouse_button_up(self, pos, button):
                self.mouse_down = False
                
        #------------------------------------------------------------------ 
        def on_key_up(self, key, mod):
                self.cammina=False
                self.movey =0
                self.movex =0
                if key == K_DOWN: 
                    self.imm_fermo=Miohero.front_standing
                elif key == K_UP: 
                    self.imm_fermo=Miohero.back_standing
                elif key == K_RIGHT: 
                    self.imm_fermo=Miohero.right_standing
                elif key == K_LEFT: 
                    self.imm_fermo=Miohero.left_standing

        #------------------------------------------------------------------ 
        def on_quit(self):
                context.pop()
        #----------------------------------------------------------------------

        ##Eofclass#-----------------------------------------------------------------------------------			

if __name__ == '__main__':
        oggetto=App_gum(resolution=(800,600))
        gummworld2.run(oggetto)
     