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
from pygame import sprite,time
import paths
import gummworld2
from gummworld2 import context, data, model, geometry, toolkit
from gummworld2 import Engine, State, TiledMap, BasicMapRenderer, Vec2d
from librerie import pyganim,gui
from varie import *
from miovardump import miovar_dump
from moving_beast import calcola_passi,MovingBeast,Dialogosemplice

from moving_animato import AnimatoSemplice,AnimatoParlanteAvvicina,AnimatoParlanteFermo

#from moving_animato import AnimatoParlanteConEvento,MessaggioDaEvento,FaiParlare,AttivaAnimato,AnimatoFermo
from moving_animato import AnimatoSegue,AnimatoAttacca,AnimatoCambiaTipo,AnimatoMandria
from eventi import AnimatoParlanteConEvento,MessaggioDaEvento,FaiParlare,AttivaAnimato,AnimatoFermo,EventoRecinto,EventoMessaggio
from armi_utensili import *
from salvataggi import *
#from miovar_dump import *
#from dialogosemp import Dialogosemplice
from librerie import xmltodict
#import subprocess
import math
from math import atan2,pi
import time
import pickle
import array

DEBUG=False
try:
    __builtin__.miavar
except:
    try:
        os.stat('animation')
    except:
        #print 'cambio dir a '+os.getcwd()
        #os.chdir('..\\') 
        os.chdir(os.pardir)


#-------------------------------------------------------------------------------
class Motore(Engine):
    def __init__(self,resolution=(400,200),dir=".\\mappe\\mappe_da_unire\\",mappa="001-1.tmx",\
                            coll_invis=True,ign_coll=False,miodebug=False,hero_ini_pos=None,dormi=True,inizia_con_menu=False):
        try:
            #filename="saved\\salvataggio.txt"
            filename=os.path.join("saved","salvataggio.txt")
            os.remove(filename)
        except:
            pass
        x = 20
        y = 80
        
        #inizia_con_menu=True
        if inizia_con_menu:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
            menuscreen = pygame.display.set_mode((800, 600))
            State.mioevento=None
            pgu=PguApp(self,inizio="salvataggi")
        self.suono_colpito=pygame.mixer.Sound('suoni/colpito.wav')
        self.suono_noncolpito=pygame.mixer.Sound('suoni/non_colpito2.wav')
        self.suono_cilecca=pygame.mixer.Sound('suoni/cilecca.wav')
        self.fringe_i=1
        #xml = open('animazioni\\prova.xml', 'r').read()
        sep=os.sep

        #xml = open('animazioni'+sep+'beta.xml', 'r').read()
        xml = open('animazioni'+sep+'prova.xml', 'r').read()
        self.dic_storia=xmltodict.parse(xml)['storia']
        #self.lista_beast=[]

        self.godebug=False
        
        #necessario per resettare la condizione messa dalla libreria PGU
        pygame.key.set_repeat()
        
        self.cammina=False   
        self.corsa=False
        #import os
        #print os.environ
       #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)    
        resolution = Vec2d(resolution)
        self.mag=Magazzino(self)
        self.app_salvata=None
        self.blockedkeys=False
        self.tipofreccia='f'
        #con questa proprietà le collisioni vengono ignorate
        self.ignora_collisioni=ign_coll
        State.speed = 10
        self.movex=0
        self.movey=0
        # Mouse and movement state. move_to is in world coordinates.
        self.move_to = None
        self.speed = None
        self.target_moved = (0,0)
        self.mouse_down = False
        self.grid_cache = {}
        self.label_cache = {}
        self.dict_gid_to_properties={0:''}
        self.arma=Arma(self)
        self.avatar = Miohero((hero_ini_pos), resolution//2,parentob=self,dormi=dormi)
        self.direzione_avatar='front'
        self.imm_fermo=self.avatar.sit_standing
        #miovar_dump(State)
        #exit()
        if sys.platform=='linux2':
            dir=dir.replace('\\', '/');
            
        dir_mappa=dir+mappa    
            
        self.init_mappa(dir_mappa=dir_mappa,coll_invis=coll_invis,hero_ini_pos=hero_ini_pos,resolution=resolution,dormi=dormi,miodebug=miodebug)

    #EofInit------------------------------------------------------------------ 
    
    def init_mappa(self,dir_mappa='',coll_invis=True,hero_ini_pos=(0,0),resolution=(800,600),dormi=True,miodebug=True):
        self.lista_beast={}
        self.lista_eventi={}
        self.warps=[]
        self.eventi=pygame.sprite.Group()
        self.beast_sprite_group=pygame.sprite.Group()
        
        self.mappa_dirfile=dir_mappa
    
        self.tiled_map = TiledMap(dir_mappa)
        
        #lista_matrice_gids(self.tiled_map.raw_map.layers[5].content2D)
        
        for mylayer in self.tiled_map.layers:
                if mylayer.name=="Ground1" or mylayer.name=="Ground":
                        self.ground_group_i= mylayer.layeri
                        self.ground_spathash=mylayer.objects
                if mylayer.name=="Collision":
                        self.collision_group_i= mylayer.layeri
                if mylayer.name=="Fringe":
                        self.fringe_i= mylayer.layeri
                if mylayer.name=="Over":
                        self.over_i= mylayer.layeri
                if mylayer.name=="raccolto": 
                        self.raccolto_layer=mylayer
                        self.raccolto_spathash=mylayer.objects
                        self.matr_layer_raccolto=self.tiled_map.raw_map.layers[mylayer.layeri].content2D
        for tileset in self.tiled_map.raw_map.tile_sets:
                for tile in tileset.tiles:
                        tile.properties['parent_tileset_name']=tileset.name
                        gid=int(tileset.firstgid)+int(tile.id)
                        tile.properties['numero']=gid
                        self.dict_gid_to_properties[gid]=tile.properties

        #carica in una lista i lvelli degli oggetti 
        self.lista_oggetti=list()
        myappend=self.lista_oggetti.append
        for L in self.tiled_map.layers: 
                if L.is_object_group :
                        myappend(L)
        #l'attr lista_oggetti in realtà è una lista dei layer con oggetti, che spesso è uno solo
        self.prima_lista_ogg=self.lista_oggetti[0].objects.objects

        ## Save special layers.
        self.all_groups = self.tiled_map.layers[:]
        self.avatar_group = self.tiled_map.layers[self.fringe_i]
        self.ground_group= self.tiled_map.layers[self.ground_group_i]
        self.over_group=self.tiled_map.layers[self.over_i]
        self.collision_group = self.tiled_map.layers[self.collision_group_i]
        num_layers=len(self.all_groups)-1
        self.overlays = self.tiled_map.layers[1:num_layers]
        ## Hide the busy Collision layer. Player can show it by hitting K_3.
        self.collision_group.visible = not coll_invis
        ## Remove above-ground layers so we can give map to the renderer.
        del self.tiled_map.layers[1:]
        dict_animati={}
        self.catturabili=pygame.sprite.Group()
        #self.avatar = Miohero((hero_ini_pos), resolution//2,parentob=self,dormi=dormi)
        Engine.__init__(self, caption='LandOfFire', resolution=resolution, camera_target=self.avatar,map=self.tiled_map,frame_speed=0)
        self.State=State
        self.avatar.position=hero_ini_pos
        for index,O in enumerate(self.prima_lista_ogg):
            
            if O.name==None:
                if hasattr(O,'gid'):
                    gid=int(O.gid)
                else:
                    gid=0
                    
                
                if 'Name' in self.dict_gid_to_properties[gid]:
                    O.name=self.dict_gid_to_properties[gid]['Name']
                elif 'name' in self.dict_gid_to_properties[gid]: 
                    O.name=self.dict_gid_to_properties[gid]['name']
                else:O.name='boar'
                O.type='animato'
                if not 'id' in O.properties:O.properties['id']=O.name+str(index)
                if not 'sottotipo' in O.properties:O.properties['sottotipo']='parlantefermo'
            animato={'pos':(O.rect.x,O.rect.y),'dir':str(O.name),'staifermo':False,'orientamento':"vuoto",'og_rect':O.rect}
            for p in O.properties:
                animato[p]=O.properties[p]
            if hero_ini_pos==(0,0):
                if O.name=="Inizio" or O.name=="inizio":
                    hero_ini_pos= O.rect.x,O.rect.y
                    self.avatar.position=hero_ini_pos
            if O.type=="warp":
                self.warps.append(O)
            if O.type=="evento":
                self.eventi.add(O)
                if 'sottotipo' in O.properties:
                    if O.properties['sottotipo']=='MessaggioDaEvento':
                        beast=MessaggioDaEvento(animato)
                        self.lista_beast[beast.id]=beast
                        beast.dialogosemp.lista_messaggi=self.dic_storia[beast.id]['messaggio']
                    if O.properties['sottotipo']=='FaiParlare':
                        beast=FaiParlare(animato)
                        self.lista_beast[beast.id]=beast
                        beast.dialogosemp.lista_messaggi=self.dic_storia[beast.id]['messaggio']
                    if O.properties['sottotipo']=='AttivaAnimato':
                        beast=AttivaAnimato(animato)
                        self.lista_beast[beast.id]=beast
                    beast.motore=self
            if O.type=='eventonew':
                #self.eventi.add(O)
                if O.name=='recinto':
                    enew=EventoRecinto(O,self)
                    self.lista_eventi[enew.id]=enew
                    #exit()
                if O.name=='messaggio':
                    enew=EventoMessaggio(O,self)
                    self.lista_eventi[enew.id]=enew
                    
            if O.type=="animato" :
                #miovar_dump(O)
                #exit()
                self.popola_lista_beast(O,dict_animati,animato,miodebug)
                
        ## Insert avatar into the Fringe layer.
        self.avatar.rect.x=hero_ini_pos[0]
        self.avatar.rect.y=hero_ini_pos[1]
        self.avatar_group.add(self.avatar)
        State.camera.position=Vec2d(State.camera.position)

        self.animato=self.camera.target.animated_object
        # Create a speed box for converting mouse position to destination
        # and scroll speed.
        self.speed_box = geometry.Diamond(0,0,4,2)
        self.speed_box.center = Vec2d(State.camera.rect.size) // 2
        self.max_speed_box = float(self.speed_box.width) / 2.0
        ## Create the renderer.
        self.mioclock=pygame.time.Clock()
        #self.mioframelimit=30
        #State.clock.max_ups=10
        #State.clock.max_fps=10
        toolkit.make_hud()
        self.renderer = BasicMapRenderer(self.tiled_map, max_scroll_speed=State.speed)
    #------------------------------------------------------------------ 
    def popola_lista_beast(self,O,dict_animati,animato,miodebug=False):
        dict_animati[animato.get('id')]=animato
        dict_animati[animato.get('id')]['dic_storia'] = self.dic_storia.get(animato.get('id'),{})

        if O.properties['sottotipo']=='semplice':
            beast=AnimatoSemplice(animato)
        elif O.properties['sottotipo']=='parlante':
            beast=AnimatoParlanteAvvicina(animato)
        elif O.properties['sottotipo']=='parlanteconevento':
            beast=AnimatoParlanteConEvento(animato)
        elif O.properties['sottotipo']=='parlantefermo':
            beast=AnimatoParlanteFermo(animato)
        elif O.properties['sottotipo']=='semplicefermo':
            beast=AnimatoFermo(animato)
        elif O.properties['sottotipo']=='morente':
            beast=AnimatoSemplice(animato)
        elif O.properties['sottotipo']=='animatosegue':
            beast=AnimatoSegue(animato,motore=self)
            if 'is_segui' in animato: beast.segui=animato['is_segui']
        elif O.properties['sottotipo']=='attaccante':
            beast=AnimatoAttacca(animato)
        elif O.properties['sottotipo']=='catturabile':
            beast=AnimatoCambiaTipo(animato)
        elif O.properties['sottotipo']=='mandria':
            beast=AnimatoMandria(animato,motore=self)

        self.beast_sprite_group.add(beast.sprite_fotogrammanew)
        beast.debug=miodebug
        beast.dic_storia=animato['dic_storia']
        beast.staifermo=animato['staifermo']
        beast.orientamento=animato['orientamento']
        beast.classe=O.properties['sottotipo']
        beast.properties=O.properties
        
        if hasattr(O,'gid'):
            beast.gid=O.gid
        beast.type=O.type
        beast.name=O.name
        #beast.image=O.image
        beast.image_source=O.image_source
        beast.motore=self
        self.lista_beast[beast.id]=beast
        self.avatar_group.add(beast)
    
    #------------------------------------------------------------------ 
    def update(self, dt):
        if self.blockedkeys:
            self.movex=self.movey=0
            self.cammina=False
            e=State.mioevento
            if e:
                typ = e.type
                if typ == KEYDOWN or typ == KEYUP:
                    self.on_key_up(e.key,e.mod)
        if self.movex or self.movey:
                if self.is_walkable2():
                    wx=State.camera.target.position[0]+self.movex
                    wy=State.camera.target.position[1]+self.movey
                    State.camera.target.position=(wx,wy)
                    self.camera.target.herosprite.rect.x=wx
                    self.camera.target.herosprite.rect.y=wy
                    self.move_to = State.camera.screen_to_world((wx,wy))
                self.is_warp()
                #self.is_event_collide()
                self.mag.is_raccolto_collide()
        self.update_camera_position()
        State.camera.update()
        ## Set render's rect.
        self.renderer.set_rect(center=State.camera.rect.center)
        State.hud.update(dt)
        #self.mioclock.tick(self.mioframelimit)
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
            #re-add the moving avatar 
            self.avatar_group.add(avatar)
            #re-add all others moving things
            for k,beast in self.lista_beast.iteritems():
                self.avatar_group.add(beast)
    #----------------------------------------------------------------------
    def draw_debug(self):
        # draw the hitbox and speed box
        camera = State.camera
        cx,cy = camera.rect.topleft
        rect = self.avatar.hitbox
        pygame.draw.rect(camera.surface, Color('red'), rect.move(-cx,-cy))
        pygame.draw.polygon(camera.surface, Color('white'), self.speed_box.corners, 1)
        State.hud.draw()
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
        self.draw_detail()
        for k,beast in self.lista_beast.iteritems():
            if not beast.attendi_evento and not beast.finito_evento:
                beast.muovi_animato()
                self.is_talking2(beast)
                if hasattr(beast.dialogosemp,'scrivi_frase'):
                    beast.dialogosemp.scrivi_frase()
        for k,evento in self.lista_eventi.iteritems():
            evento.controlla_se_attivo()
        
        State.screen.flip()
    #---------------------------------------------------
    def draw_detail(self):
        camera = State.camera
        camera_rect = camera.rect
        cx,cy = camera_rect.topleft
        blit = camera.surface.blit
        avatar = self.avatar
        # Draw static overlay tiles.
        for layer in self.overlays:
            sprites = layer.objects.intersect_objects(camera_rect)
            if layer.visible:
                if layer is self.avatar_group:
                    sprites.sort(key=lambda o:o.rect.bottom)
                for s in sprites:
                    if isinstance(s,Proiettile):
                        #s.muovi()
                        #blit(s.image, s.rect.move(-cx,-cy))
                        pass
                    if s is avatar:
                        blit(s.image, s.rect.move(camera.anti_interp(s)))
                        pass
                    else:
                        #if self.godebug:
                        #    print(camera.rect)
                        #    print(s.rect)
                        #    print(camera.rect.colliderect(s.rect))
                        if isinstance(s,MovingBeast):
                            #if not s.attendi_evento and not s.finito_evento:
                            if s.draw_fotogramma:
                                blit(s.image, s.rect.move(-cx,-cy))
                        elif isinstance(s,Proiettile):
                            s.muovi()
                            blit(s.image, s.rect.move(-cx,-cy))
                        elif isinstance(s,UtensilePiccone):
                            s.muovi()
                            blit(s.image, s.rect.move(-cx,-cy))
                        else:
                            blit(s.image, s.rect.move(-cx,-cy))
                            pass
    #---------------------------------------------------
    def warp_del_seguito(self):
        incremento=0
        for k,i in self.mag.seguito.iteritems():
            id_raccolto=i[0]['nome']
            if id_raccolto in self.lista_beast: 
                if self.direzione_avatar=='front':
                     incx=incy=-20
                elif self.direzione_avatar=='back':
                    incx=+16
                    incy=+42
                elif self.direzione_avatar=='left':
                    incx=+16
                    incy=+42
                elif self.direzione_avatar=='right':
                    incx=-32
                    incy=+42
                self.lista_beast[id_raccolto].x=self.avatar.hitbox.bottomleft[0]+incx
                self.lista_beast[id_raccolto].y=self.avatar.hitbox.bottomleft[1]+incy
                self.lista_beast[id_raccolto].sfasamento=incremento
            incremento=incremento+16
    #------------------------------------------------------
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
                try:
                    dir=warp.properties['dir']
                    if sys.platform=='linux2':
                        dir=dir.replace('\\', '/');
                except:
                    dir=".\\mappe\\mappe_da_unire\\"
                    if sys.platform=='linux2':
                        dir=dir.replace('\\', '/');
                mappa=warp.properties['dest_map']+".tmx"
                destx=int(warp.properties['dest_tile_x'])*32
                desty=int(warp.properties['dest_tile_y'])*32
                #print self.mappa_dirfile
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
                        self.warp_del_seguito() #posizione sulla nuova mappa il cane o altro seguito
                else:
                        self.nuova_mappa_caricare=True
                        if self.mag.seguito: #verifica se c'è seguito, in quel caso lo salva in lista_beast_seguito
                            lista_beast_seguito=dict()
                            for k,v in self.mag.seguito.iteritems():
                                if v[0]['nome'] in self.lista_beast:
                                    lista_beast_seguito[v[0]['nome']]=self.lista_beast[v[0]['nome']]
                        #else:
                            #lista_beast_seguito=dict()
                        salvataggio=Salvataggio() #salva lo stato della mappa lasciata
                        salvataggio.salva(motore=self)
                        
                        self.init_mappa(dir_mappa=dir+mappa,hero_ini_pos=(destx,desty),resolution=(800,600),dormi=False,miodebug=False)
                        #if 'lista_beast_seguito' in locals():
                            #self.lista_beast=dict(self.lista_beast.items()+lista_beast_seguito.items()) #aggiunge alla lista_beast della nuova mappa il seguito raccolto nella mappa lasciata
                        
                        salvataggio.ricarica(motore=self,qualemappa=self.mappa_dirfile)
                        self.warp_del_seguito() #posizione sulla nuova mappa il cane o altro seguito
            #print "tutte le bestie dopo l'aggiunat del seguito"+str(self.lista_beast)
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
    def toggle_layer(self, i):
        """toggle visibility of layer i"""
        try:
            layer = self.all_groups[i]
            layer.visible = not layer.visible
            self.renderer.clear()
        except:
            pass
    #-------------------------------------------------------
    @property
    def dialogo_btn(self):
        return self._dialogo_btn
    #------------------------------------------------------
    @dialogo_btn.setter
    def dialogo_btn(self,val):
        self._dialogo_btn=val
    #-------------------------------------------------------    
    
    #------------------------------------------------------
    def is_talking2(self,beast):
            #hits=self.avatar.rect.colliderect(beast.talk_box)
            beast.fallo_parlare()
            if self.godebug:
                cx,cy = self.camera.rect.topleft
                #pygame.draw.rect(self.camera.surface, Color('red'), beast.talk_box.move(-cx,-cy))
                #pygame.draw.rect(self.camera.surface, Color('red'), beast.beast_hit_box.move(-cx,-cy))
                pygame.draw.rect(self.camera.surface, Color('red'), beast.sprite_fotogrammanew.rect.move(-cx,-cy))
    #------------------------------------------------------------------
    def verifica_residuale_tasti_premuti(self,mio_keydown):
        if not self.blockedkeys:
            keys = pygame.key.get_pressed()
            #print keys[K_LEFT]
            #self.camera_target.moveConductor.play()
            if (keys[K_LEFT] or keys[K_a]):
                    self.camera.target.giocatore_animato=self.animato['left_walk']
                    self.cammina=True
                    self.movex += -State.speed
            if (keys[K_RIGHT] or keys[K_d]):
                    self.camera.target.giocatore_animato=self.animato['right_walk']
                    self.cammina=True
                    self.movex += State.speed
            if (keys[K_DOWN] or keys[K_s]):
                    self.camera.target.giocatore_animato=self.animato['front_walk']
                    self.cammina=True
                    self.movey += State.speed
            if (keys[K_UP] or keys[K_w]):
                self.camera.target.giocatore_animato=self.animato['back_walk']
                self.cammina=True
                self.movey += -State.speed
    #------------------------------------------------------------------ 
    def on_key_down(self, unicode, key, mod):
        if not self.blockedkeys:
            self.on_key_down_incondizionato(unicode, key, mod)

    #------------------------------------------------------------------ 
    def on_key_down_incondizionato(self, unicode, key, mod):
        if key == K_DOWN or key == K_s:               
            self.cammina=True
            self.camera.target.giocatore_animato=self.animato['front_walk']
            self.movey += State.speed
            if self.corsa: 
                    self.movey += State.speed
                    self.camera.target.giocatore_animato=self.animato['front_run']
            self.direzione_avatar='front'
        elif key == K_UP or key == K_w: 
            self.cammina=True
            self.camera.target.giocatore_animato=self.animato['back_walk']
            self.movey += -State.speed
            if self.corsa:
                    self.movey += -State.speed
                    self.camera.target.giocatore_animato=self.animato['back_run']
            self.direzione_avatar='back'
        elif key == K_RIGHT or key == K_d: 
            self.cammina=True
            self.camera.target.giocatore_animato=self.animato['right_walk']
            self.movex += State.speed
            if self.corsa: 
                    self.camera.target.giocatore_animato=self.animato['right_run']
                    self.movex += State.speed
            self.direzione_avatar='right'
        elif key == K_LEFT or key == K_a: 
            self.cammina=True
            self.camera.target.giocatore_animato=self.animato['left_walk']
            self.movex += -State.speed
            if self.corsa:
                    self.movex += -State.speed
                    self.camera.target.giocatore_animato=self.animato['left_run']
            self.direzione_avatar='left'
        elif key==pygame.K_l:
            if self.tipofreccia=='l':
                self.tipofreccia='f'
            else:
                self.tipofreccia='l'
        elif key==pygame.K_h:
            #print "h"
            selettore=Selettore(motore=self)
        elif key == pygame.K_F2:  #salva la situazione del gioco 
            print 'salvato'
            salvataggio=Salvataggio()
            salvataggio.salva(motore=self,target_file='prova_salvato.txt')
            del salvataggio
        elif key == pygame.K_F3: #ricarica la situazione del gioco dal file 
            print "ricarica"
            salvato=Salvataggio()
            salvato.ricarica_manuale(motore=self,target_file='prova_salvato.txt')
            print salvato.root['mappa_attuale']
            del salvato
        elif key == pygame.K_F4:
            print 'f4'
            dialog = DialogoAvvisi(testo='pippo F4')
        elif key == pygame.K_F5:
            if not self.godebug:
                self.godebug=True
            else:
                self.godebug=False
        elif key == pygame.K_F6:
            #self.wx.testo.SetLabel(label=str(self.avatar.hitbox))
            self.wx.Show(True) #mostra la finestra wxpython 
            #print pygame.display.get_wm_info()
        elif key == pygame.K_F7:
            #print 'f7'
            pgu=PguApp(self)
        elif key == pygame.K_e:
            pgu=PguApp(self,inizio="animali")
        elif key == pygame.K_t:
            pgu=PguApp(self,inizio="inventario")
        elif key == pygame.K_m:
            pgu=PguApp(self,inizio="mappa")
        elif key == pygame.K_F9:
            print 'f9'
            self.beast_sprite_group.empty()
            
        elif key == K_g:
            State.show_grid = not State.show_grid
        elif key == K_l:
            State.show_labels = not State.show_labels
        elif key >= K_0 and key <= K_9:
                    self.toggle_layer(key - K_0)                    
        elif key == K_ESCAPE: 
                context.pop()
    #------------------------------------------------------------------ 
    @property
    def intervallo_mouse(self):
        if not hasattr(self,'mousenow'): return True
        tnow=time.time()
        if tnow>self.mousenow+2:
            self.suono_noncolpito.play()
            return True
        else: 
            self.suono_cilecca.play()
            return False
    #------------------------------------------------------------------ 
    def on_mouse_button_down(self, pos, button): 
        if button==3:
            self.blockedkeys=False
        if button==1:
            if self.intervallo_mouse:
                self.mousenow=time.time()
                if 'arco' in self.mag.selezionabili:
                    if self.mag.selezionabili['arco']:
                        utensile=Proiettile(self,pos)
                if 'lasso' in self.mag.selezionabili:
                    if self.mag.selezionabili['lasso']:
                        utensile=Proiettile(self,pos)
                if 'spada' in self.mag.selezionabili:
                    if self.mag.selezionabili['spada']:
                        utensile=UtensileSpada(self,pos)
                if 'piccone' in self.mag.selezionabili:
                    if self.mag.selezionabili['piccone']:
                        utensile=UtensilePiccone(self,pos)
                if 'mappa' in self.mag.selezionabili:
                    if self.mag.selezionabili['mappa']:
                        pgu=PguApp(self,inizio="mappa")
                if 'utensile' in locals():
                    utensile.mostra()
                else:
                    if not 'pgu' in locals():
                        dialog = DialogoAvvisi(testo="Seleziona un'arma o uno strumento da usare! (tasto T) (tasto H)")

    #------------------------------------------------------------------ 
    def on_mouse_button_up(self, pos, button):
            self.mouse_down = False

    def on_key_up(self,key,mod):
        if not self.blockedkeys:
            self.on_key_up_incondizionato(key, mod)
        else:
            self.avatar.standing_scelta=self.avatar.front_standing
    #------------------------------------------------------------------ 
    def on_key_up_incondizionato(self, key, mod):
        self.cammina=False
        self.movey =0
        self.movex =0
        if key == K_DOWN or key == K_s: 
            self.avatar.standing_scelta=self.avatar.front_standing
        elif key == K_UP or key == K_w: 
            self.avatar.standing_scelta=self.avatar.back_standing
        elif key == K_RIGHT or key == K_d: 
            self.avatar.standing_scelta=self.avatar.right_standing
        elif key == K_LEFT or key == K_a: 
            self.avatar.standing_scelta=self.avatar.left_standing
        self.verifica_residuale_tasti_premuti(key)
                

    
    #------------------------------------------------------------------ 
    def on_quit(self):
        self.app_salvata=context.top()
        context.pop()
    
    def mio_riprendi(self):

        context.push(self.app_salvata)
        while context.top():
            State.clock.tick()

    #----------------------------------------------------------------------
#Eofclass#-----------------------------------------------------------------------------------			

def miomain(debug=True,hero_ini_pos1=(0,0)):
    oggetto=Motore(resolution=(800,600),miodebug=debug,hero_ini_pos=hero_ini_pos1,mappa='casa_gioco.tmx')
    iconimg=".\immagini\\icona2.gif"
    if sys.platform=='linux2':
        iconimg=iconimg.replace('\\', '/');
    icon=pygame.image.load(iconimg)
    #icon=pygame.image.load(".\immagini\\icona2.gif")
    pygame.display.set_icon(icon)
    gummworld2.run(oggetto)
    return oggetto

def newmain(debug=True,hero_ini_pos1=(0,0),mappa='betatest.tmx',inizia_con_menu=True):
    oggetto=Motore(resolution=(800,600),miodebug=debug,hero_ini_pos=hero_ini_pos1,mappa=mappa,inizia_con_menu=True)
    iconimg=".\immagini\\icona2.gif"
    if sys.platform=='linux2':
        iconimg=iconimg.replace('\\', '/');
    icon=pygame.image.load(iconimg)
    pygame.display.set_icon(icon)
    gummworld2.run(oggetto)
    return oggetto

if __name__ == '__main__':


    
    newmain(debug=DEBUG,hero_ini_pos1=(0,0))
        
     