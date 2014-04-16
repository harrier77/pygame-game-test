# coding: utf-8
import os
from os.path import relpath
import sys
import __builtin__
import xml
from xml import dom
from xml.dom import minidom
import pygame
from pygame.locals import *
from pygame import sprite
import paths
import gummworld2
import cProfile, pstats
from gummworld2 import context, data, model, geometry, toolkit
from gummworld2 import Engine, State, TiledMap, BasicMapRenderer, Vec2d
from librerie import pyganim

from beast import calcola_passi,Beast,MovingBeast
from miovar_dump import *
from dialogosemp import Dialogosemplice
from librerie import xmltodict
DEBUG=False

#-------------------------------------------------------------------------------
class Miohero(model.Object):
        # load the "standing" sprites (these are single images, not animations)
        try:
                __builtin__.miavar
        except:
                try:
                        os.stat('animation')
                except:
                        print 'cambio dir a '+os.getcwd()
                        os.chdir('..\\') 
        sit_standing=pygame.image.load('animazioni/gameimages/crono_sleep.000.gif')
        front_standing = pygame.image.load('animazioni/gameimages/crono_front.gif')
        back_standing = pygame.image.load('animazioni/gameimages/crono_back.gif')
        left_standing = pygame.image.load('animazioni/gameimages/crono_left.gif')
        right_standing = pygame.transform.flip(left_standing, True, False)
        standing_scelta=sit_standing
        div_scala=1.4
        

        #------------------------------------
        def __init__(self,map_pos,screen_pos,parentob):
                model.Object.__init__(self)
                self.parent=parentob
                self.animated_object=self.crea_giocatore_animato()
                self.giocatore_animato=self.animated_object['front_walk']
                #self.image= self.giocatore_animato.ritorna_fotogramma()
                self.rect=self.image.get_rect()
                #self.hitbox = self.rect
                self.herosprite=pygame.sprite.Sprite()
                self.herosprite.image=self.image
                self.herosprite.rect=self.rect
                self.position = map_pos
                self.screen_position = screen_pos
                
        #------------------------------------       
        def crea_giocatore_animato(self):
                #playerWidth, playerHeight = self.front_standing.get_size()
                # creating the PygAnimation objects for walking/running in all directions
                animTypes = 'back_run back_walk front_run front_walk left_run left_walk'.split()
                animObjs = {}
                for animType in animTypes:
                    imagesAndDurations = [('animazioni/gameimages/crono_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
                    animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)
 
                for id in animObjs:
                        dim_meta=(int(animObjs[id].getRect().width/self.div_scala),int(animObjs[id].getRect().height/self.div_scala))
                        animObjs[id].scale(dim_meta)
                        
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
        #------------------------------------
        @property
        def image(self):
            if self.parent.cammina:
                image= self.giocatore_animato.ritorna_fotogramma()
            else:
                #image=self.front_standing
                image=self.standing_scelta
                dim_meta= (int(image.get_size()[0]/self.div_scala),int(image.get_size()[1]/self.div_scala))
                image=pygame.transform.scale(image,dim_meta)
            return image
        #------------------------------------ 
        @property
        def hitbox(self):
            hitbox=self.rect.copy()
            hitbox.height=18
            hitbox.width=10
            y = self.rect.y+(hitbox.height/2)
            x= self.rect.x-(hitbox.width/2)
            hitbox.y=y
            hitbox.x=x
            return hitbox
        
        
#FineClasse -------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class App_gum(Engine):
        nuova_mappa_caricare=True
        fringe_i=1
        #dic_storia={'interlocutore':{'segmento':'2','messaggio':'Esci muoviti! Il califfo sta parlando e manchi solo tu!'}}
        xml = open('animazioni\\prova.xml', 'r').read()
        dic_storia1=xmltodict.parse(xml)['storia']

        
        def __init__(self,resolution=(400,200),dir=".\\mappe\\mappe_da_unire\\",mappa="casa_gioco.tmx",\
                                coll_invis=True,ign_coll=False,miodebug=True,hero_ini_pos=(21*32,28*32)):
                #necessario per resettare la condizione messa dalla libreria PGU
                pygame.key.set_repeat()
                #---------------
                #self.warping=False
                resolution = Vec2d(resolution)
                self.mappa_dirfile=dir+mappa
                #if self.nuova_mappa_caricare: 
                self.tiled_map = TiledMap(dir+mappa)
                for mylayer in self.tiled_map.layers:
                        if mylayer.name=="Collision":
                                self.collision_group_i= mylayer.layeri
                        if mylayer.name=="Fringe":
                                self.fringe_i= mylayer.layeri
                                
                ##carica in una lista i lvelli degli oggetti 
                self.lista_oggetti=list()
                
                for L in self.tiled_map.layers: 
                        if L.is_object_group :
                                self.lista_oggetti.append(L)
                ##fine
                ##l'attr lista_oggetti in realtà è una lista dei layer con oggetti, che spesso è uno solo
                self.prima_lista_ogg=self.lista_oggetti[0].objects.objects

                ## Save special layers.
                self.all_groups = self.tiled_map.layers[:]
                self.avatar_group = self.tiled_map.layers[self.fringe_i]
                self.collision_group = self.tiled_map.layers[self.collision_group_i]
                num_layers=len(self.all_groups)-1
                self.overlays = self.tiled_map.layers[1:num_layers]
                ## Hide the busy Collision layer. Player can show it by hitting K_3.
                self.collision_group.visible = not coll_invis
                ## Remove above-ground layers so we can give map to the renderer.
                del self.tiled_map.layers[1:]
                

                cinghiale_ini_pos=(251,483)
                dict_animati={}
                self.warps=[]
                for O in self.prima_lista_ogg:
                        if O.type=="warp":
                                self.warps.append(O)
                        if O.name=="Inizio" or O.name=="inizio":
                                hero_ini_pos= O.rect.x,O.rect.y
                        if O.type=="animato":
                                if O.name=="cinghiale":
                                        cinghiale_ini_pos=O.rect.x,O.rect.y
                                        cinghiale = {'pos': cinghiale_ini_pos, 'id': O.properties['id'],'durata_pausa':int(O.properties['durata_pausa'])}
                                        cinghiale['points']=O.properties['points']
                                        cinghiale['dir']='boar'
                                        id= int(cinghiale.get('id'))
                                        pos=cinghiale['pos']
                                        dict_animati[id]=cinghiale
                                        dict_animati[id]['dic_storia'] ={}
                                if O.name=="antagonista":
                                        antagonista_ini_pos=O.rect.x,O.rect.y
                                        antagonista = {'pos': antagonista_ini_pos, 'id': O.properties['id'],'durata_pausa':int(O.properties['durata_pausa'])}
                                        antagonista['points']=O.properties['points']
                                        antagonista['dir']='priest'
                                        id= antagonista.get('id')
                                        pos=antagonista['pos']
                                        dict_animati[id]=antagonista
                                        #dict_animati[id]['dic_storia'] = self.dic_storia['interlocutore']
                                        dict_animati[id]['dic_storia'] = self.dic_storia1['interlocutore'][0]
                                        
                self.cammina=False        
                ## The avatar is also the camera target.
                self.avatar = Miohero((hero_ini_pos), resolution//2,parentob=self)
                
                self.lista_beast=[]
                for i in dict_animati:
                       pos_beast= dict_animati[i]['pos']
                       durata_pausa=dict_animati[i]['durata_pausa']
                       id=dict_animati[i]['id']
                       points=dict_animati[i]['points']
                       dir_from_dict=dict_animati[i]['dir']
                       beast=MovingBeast(pos_beast,durata_pausa,id,points,dir_name=dir_from_dict)
                       beast.debug=miodebug
                       beast.dic_storia=dict_animati[i]['dic_storia']
                       beast.motore=self
                       self.lista_beast.append(beast)
                
      
                Engine.__init__(self,
                    caption='Tiled Map with Renderer '+mappa,
                    resolution=resolution,
                    camera_target=self.avatar,
                    map=self.tiled_map,
                    frame_speed=0)
                
                ## Insert avatar into the Fringe layer.
                self.avatar.rect.x=hero_ini_pos[0]
                self.avatar.rect.y=hero_ini_pos[1]
                self.avatar_group.add(self.avatar)
                for beast in self.lista_beast:
                        self.avatar_group.add(beast)
                
                State.camera.position=Vec2d(State.camera.position)
         
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
                
                State.speed = 10
                self.movex=0
                self.movey=0
                self.cammina=False
                self.imm_fermo=Miohero.sit_standing
                self.animato=self.camera.target.animated_object
                
                #con questa proprietà le collisioni vengono ignorate
                self.ignora_collisioni=ign_coll
                self.corsa=False
                #self.collision_dummy = Miohero((0,0),resolution//2,parentob=self)
                ## Create the renderer.
                self.renderer = BasicMapRenderer(self.tiled_map, max_scroll_speed=State.speed)
                self.dialogo=Dialogosemplice()
                

                
        #------------------------------------------------------------------ 
        def update(self, dt):
                if self.movex or self.movey:
                        if self.is_walkable2():
                            wx=State.camera.target.position[0]+self.movex
                            wy=State.camera.target.position[1]+self.movey
                            State.camera.target.position=(wx,wy)
                            self.camera.target.herosprite.rect.x=wx
                            self.camera.target.herosprite.rect.y=wy
                            self.move_to = State.camera.screen_to_world((wx,wy))
                        self.is_warp()


                self.update_camera_position()
                State.camera.update()
                ## Set render's rect.
                self.renderer.set_rect(center=State.camera.rect.center)
                
        #------------------------------------------------------------------                      
        @property
        def mio_move_to(self):
            if self.cammina:
                return self.move_to
            else:
                return None
        #------------------------------------------------------------------    
        def update_camera_position(self):
            """update the camera's position if any movement keys are held down
            """
            if self.mio_move_to is not None:
                camera = State.camera
                wx,wy = camera.position
                avatar = self.avatar
                # Keep avatar inside map bounds.
                rect = State.world.rect
                wx = max(min(wx,rect.right), rect.left)
                wy = max(min(wy,rect.bottom), rect.top)
                camera.position = wx,wy
                self.avatar_group.add(avatar)
        #----------------------------------------------------------------------
        def draw_debug(self):
                # draw the hitbox and speed box
                camera = State.camera
                cx,cy = camera.rect.topleft
                rect = self.avatar.hitbox
                pygame.draw.rect(camera.surface, Color('red'), rect.move(-cx,-cy))
                pygame.draw.polygon(camera.surface, Color('white'), self.speed_box.corners, 1)
        
        
        
        #------------------------------------------------------------------ 
        def draw(self, interp):
                State.screen.clear()
                #if self.warping:return "warping"
                self.renderer.draw_tiles()
                if State.show_grid:
                    toolkit.draw_grid(self.grid_cache)
                if State.show_labels:
                    toolkit.draw_labels(self.label_cache)
                if self.all_groups[self.collision_group_i].visible: self.draw_debug()
                for beast in self.lista_beast:
                    beast.muovi_animato()
                self.draw_detail()
                self.dialogo.scrivi_frase()
                State.screen.flip()
        #---------------------------------------------------
        def draw_detail(self):
            camera = State.camera
            camera_rect = camera.rect
            cx,cy = camera_rect.topleft
            blit = camera.surface.blit
            avatar = self.avatar
            #beast=self.beast
            # Draw static overlay tiles.
            for layer in self.overlays:
                sprites = layer.objects.intersect_objects(camera_rect)
                if layer.visible:
                    if layer is self.avatar_group:
                        sprites.sort(key=lambda o:o.rect.bottom)
                    for s in sprites:
                        if s is avatar:
                            blit(s.image, s.rect.move(camera.anti_interp(s)))
                        #if s is beast:
                            #blit(s.image, s.rect.move(-cx,-cy))
                        else:
                            blit(s.image, s.rect.move(-cx,-cy))
  
        
        def is_warp(self):
                dummy = self.avatar
                newhitbox=dummy.hitbox.copy()
                newhitbox.x=dummy.hitbox.x+self.movex
                for warp in self.warps:
                        if warp.rect.colliderect(newhitbox):
                                scrittaor=pygame.image.load('immagini/loading4.gif').convert()
                                scritta=pygame.transform.scale(scrittaor,(100,100))
                                self.warping=True
                                State.screen.clear()
                                centerpos=State.screen.center[0]-scritta.get_width()/2,State.screen.center[1]-scritta.get_height()/2
                                State.screen.blit(scritta,centerpos)
                                State.screen.flip()
                                try:dir=warp.properties['dir']
                                except:dir=".\\mappe\\mappe_da_unire\\"
                                mappa=warp.properties['dest_map']+".tmx"
                                destx=int(warp.properties['dest_tile_x'])*32
                                desty=int(warp.properties['dest_tile_y'])*32
                                print self.mappa_dirfile
                                if self.mappa_dirfile==dir+mappa:
                                        self.nuova_mappa_caricare=False
                                        self.avatar.rect.x=destx
                                        self.avatar.rect.y=desty
                                        camera = State.camera
                                        wx,wy = destx,desty
                                        # Keep avatar inside map bounds.
                                        rect = State.world.rect
                                        wx = max(min(wx,rect.right), rect.left)
                                        wy = max(min(wy,rect.bottom), rect.top)
                                        camera.position = wx,wy
                                else:
                                        self.nuova_mappa_caricare=True
                                        self.__init__(resolution=(800,600),dir=dir,mappa=mappa,hero_ini_pos=(destx,desty))


                
        #------------------------------------------------------
        def is_walkable2(self):
                if self.ignora_collisioni:
                        return True
                dummy = self.avatar
                is_walkable=True
                newhitbox=dummy.hitbox.copy()
                newhitbox.x=dummy.hitbox.x+self.movex
                hits=self.collision_group.objects.intersect_objects(newhitbox)
                if not hits:
                        dummy.hitbox.x=newhitbox.x
                        is_walkable=True
                else:
                        is_walkable=False
                newhitbox.y=dummy.hitbox.y+self.movey
                hits=self.collision_group.objects.intersect_objects(newhitbox)
                if not hits:
                        dummy.hitbox.y=newhitbox.y
                        is_walkable=True
                else:
                        is_walkable=False
                return is_walkable       
        
        #------------------------------------------------------------------
        def verifica_residuale_tasti_premuti(self,mio_keydown):
                keys = pygame.key.get_pressed()
                #print keys[K_LEFT]
                #self.camera_target.moveConductor.play()
                if (keys[K_LEFT]):
                        self.camera.target.giocatore_animato=self.animato['left_walk']
                        self.cammina=True
                        self.movex += -State.speed
                if (keys[K_RIGHT]):
                        self.camera.target.giocatore_animato=self.animato['right_walk']
                        self.cammina=True
                        self.movex += State.speed
                if (keys[K_DOWN]):
                        self.camera.target.giocatore_animato=self.animato['front_walk']
                        self.cammina=True
                        self.movey += State.speed
                if (keys[K_UP]):
                    self.camera.target.giocatore_animato=self.animato['back_walk']
                    self.cammina=True
                    self.movey += -State.speed

        #------------------------------------------------------------------ 
        def on_key_down(self, unicode, key, mod):
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
                        #self.dialogo.testo="Pippo"
                        self.dialogo.open=True
                elif key == K_g:
                    State.show_grid = not State.show_grid
                elif key == K_l:
                    State.show_labels = not State.show_labels
                elif key >= K_0 and key <= K_9:
                            self.toggle_layer(key - K_0)                    
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
                        self.avatar.standing_scelta=self.avatar.front_standing
                    elif key == K_UP: 
                        self.avatar.standing_scelta=self.avatar.back_standing
                    elif key == K_RIGHT: 
                        self.avatar.standing_scelta=self.avatar.right_standing
                    elif key == K_LEFT: 
                        self.avatar.standing_scelta=self.avatar.left_standing
                    self.verifica_residuale_tasti_premuti(key)
                    
        #------------------------------------------------------------------ 
        def toggle_layer(self, i):
            """toggle visibility of layer i"""
            try:
                layer = self.all_groups[i]
                layer.visible = not layer.visible
                self.renderer.clear()
            except:
                pass
        
        #------------------------------------------------------------------ 
        def on_quit(self):
                context.pop()
        #----------------------------------------------------------------------
#Eofclass#-----------------------------------------------------------------------------------			

def miomain(debug=True):
        oggetto=App_gum(resolution=(800,600),miodebug=debug)
        icon=pygame.image.load(".\immagini\\icona2.gif")
        pygame.display.set_icon(icon)
        gummworld2.run(oggetto)
        

if __name__ == '__main__':
        miomain(debug=DEBUG)
        
     