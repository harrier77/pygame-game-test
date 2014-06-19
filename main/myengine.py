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

from moving_beast import calcola_passi,MovingBeast
from moving_animato import AnimatoSemplice,AnimatoParlanteAvvicina,AnimatoParlanteFermo
from moving_animato import AnimatoParlanteConEvento,MessaggioDaEvento,FaiParlare,AttivaAnimato,AnimatoFermo,AnimatoMorente
from miovar_dump import *
#from dialogosemp import Dialogosemplice
from librerie import xmltodict
import subprocess
import math
from math import atan2,pi
DEBUG=False
try:
    __builtin__.miavar
except:
    try:
        os.stat('animation')
    except:
        print 'cambio dir a '+os.getcwd()
        os.chdir('..\\') 
        
        
        
#-------------------------------------------------------------------------------
class Magazzino(model.Object):
    def __init__(self,motore):
        self.motore=motore
        square=pygame.image.load('.\\immagini\\square1.png').convert_alpha()
        self.background_magazzino =pygame.transform.scale(square,(State.screen.size[0]-1,100))
        self.backvuoto=self.background_magazzino.copy()
    def aggiungi_magazzino(self):
        x=10
        #if not self.motore.dialogo_btn:
        for obj in self.motore.raccolti:
            larg=obj.image.get_width()
            self.background_magazzino.blit(obj.image,(x,15))
            State.screen.blit(self.background_magazzino,(5,550))
            x=x+larg
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
class Proiettile(model.Object):
    
    #------------------------------------
    def __init__(self,motore,mouse_position):
        self.freccia=pygame.image.load('immagini/bulletnero.png')
        #freccia=pygame.transform.scale(freccia,(72,72))
        pygame.mixer.init()
        self.suono=pygame.mixer.Sound('immagini/message.wav')
        self.motore=motore
        self.rect=self.image.get_rect()
        #self.rect=self.motore.avatar.rect.copy()
        self.rect.x=self.motore.avatar.rect.x-self.freccia.get_width()/2
        self.rect.y=self.motore.avatar.rect.y-self.freccia.get_height()/2
        pos= self.motore.camera.screen_to_world(mouse_position)
        self.mouse_position=pos
        dify= (pos[1]-self.rect.y) 
        difx=  (pos[0]-self.rect.x)
        angolo_rads=math.atan2(dify,difx)
        #self.coefa=float(dify)/float(difx)

        self.dx=math.cos(angolo_rads)
        self.dy=math.sin(angolo_rads)
        self.freccia=pygame.transform.rotate(self.freccia, 360-angolo_rads*57.29)
        self.sprite=pygame.sprite.Sprite()
        self.sprite.image=self.freccia
        self.sprite.rect=self.rect
        self.colpito=False

    #------------------------------------
    def mostra(self):
        self.motore.avatar_group.add(self)
    #------------------------------------
    def muovi(self): 
        if not self.colpito:
            """if len(self.lista_pos)>0: 
                pos=self.lista_pos.pop(0)
                self.rect.x,self.rect.y=pos
            p=geometry.step_toward_point((self.rect.x,self.rect.y), self.mouse_position, 10)
            self.rect.x=p[0]
            self.rect.y=p[1]
            print p"""
            #con trigonometria
            self.rect.x=self.rect.x+self.dx*10
            self.rect.y=self.rect.y+self.dy*10
            hits= pygame.sprite.spritecollide(self.sprite,self.motore.beast_sprite_group, False)
            if hits:
                self.colpito=True
                self.motore.avatar_group.objects.remove(self)
                self.suono.play()
            #con coefficiente angolare
            #self.rect.x=self.rect.x+4
            #self.rect.y=self.rect.y+4*self.coefa
        
    #------------------------------------
    @property
    def image(self):
        #self.freccia=pygame.transform.rotate(self.freccia, 360-self.arcotangente*57.29)
        return self.freccia
#-------------------------------------------------------------------------------#end of class

#-------------------------------------------------------------------------------
class Miohero(model.Object):

        #------------------------------------
        def __init__(self,map_pos,screen_pos,parentob,dormi=True):
            model.Object.__init__(self)
            # load the "standing" sprites (these are single images, not animations)
            self.sit_standing=pygame.image.load('animazioni/gameimages/crono_sleep.000.gif')
            self.front_standing = pygame.image.load('animazioni/gameimages/crono_front.gif')
            self.back_standing = pygame.image.load('animazioni/gameimages/crono_back.gif')
            self.left_standing = pygame.image.load('animazioni/gameimages/crono_left.gif')
            self.right_standing = pygame.transform.flip(self.left_standing, True, False)

            self.standing_scelta=self.sit_standing
            self.div_scala=1.8
            self.miosprite=pygame.sprite.Sprite()
            self.parent=parentob
            self.dormi=dormi
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
            
            imagesAndDurations = [('animazioni/gameimages/crono_sleep.000.gif',1),('animazioni/gameimages/crono_sleep.001.gif',1)]
            animObjs['sleep']=pyganim.PygAnimation(imagesAndDurations)
            
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
                self.dormi=False
            elif self.dormi:
                self.giocatore_animato=self.animated_object['sleep']
                image=self.giocatore_animato.ritorna_fotogramma()
            else:
                image=self.standing_scelta
                dim_meta= (int(image.get_size()[0]/self.div_scala),int(image.get_size()[1]/self.div_scala))
                image=pygame.transform.scale(image,dim_meta)
            return image
        #------------------------------------ 
        @property
        def hitbox(self):
            hitbox=self.rect.copy()
            hitbox.height=12
            hitbox.width=10
            #y = self.rect.y+(hitbox.height/2)
            y = self.rect.y+hitbox.height/2
            x= self.rect.x-(hitbox.width/2)
            
            hitbox.y=y
            hitbox.x=x
            #print hitbox.midbottom
            return hitbox
        
        @property
        def sprite(self):
            miosprite=self.miosprite
            miosprite.image=self.image
            miosprite.rect=self.hitbox
            return miosprite
        
        
#FineClasse -------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class App_gum(Engine):

    def __init__(self,resolution=(400,200),dir=".\\mappe\\mappe_da_unire\\",mappa="casa_gioco.tmx",\
                            coll_invis=True,ign_coll=False,miodebug=False,hero_ini_pos=(21*32,28*32),dormi=True):

        self.nuova_mappa_caricare=True
        self.fringe_i=1
        xml = open('animazioni\\prova.xml', 'r').read()
        self.dic_storia=xmltodict.parse(xml)['storia']
        self.lista_beast=[]
        self.lista_beast={}
        self.godebug=False
        self.raccolti=[]
        #dialogo_btn=False
        self.beast_sprite_group=pygame.sprite.Group()
        
        
        #necessario per resettare la condizione messa dalla libreria PGU
        pygame.key.set_repeat()
        
        x = 20
        y = 80
        #import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)    
        
        
        resolution = Vec2d(resolution)
        self.mappa_dirfile=dir+mappa
        
        self.tiled_map = TiledMap(dir+mappa)

        for mylayer in self.tiled_map.layers:
                if mylayer.name=="Collision":
                        self.collision_group_i= mylayer.layeri
                if mylayer.name=="Fringe":
                        self.fringe_i= mylayer.layeri
                if mylayer.name=="raccolto": 
                        self.raccolto_layer=mylayer
                        self.raccolto_spathash=mylayer.objects
                        tileset_raccoglibili=self.tiled_map.raw_map.tile_sets[mylayer.layeri]
                        self.raccoglibili_dict={}
                        for r in tileset_raccoglibili.tiles:
                            indice=str(int(r.id)+int(tileset_raccoglibili.firstgid))
                            self.raccoglibili_dict[indice]=r.properties['nome']
       
        #carica in una lista i lvelli degli oggetti 
        self.lista_oggetti=list()
        myappend=self.lista_oggetti.append
        for L in self.tiled_map.layers: 
                if L.is_object_group :
                        myappend(L)
        #fine
        #l'attr lista_oggetti in realtà è una lista dei layer con oggetti, che spesso è uno solo
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
        self.cammina=False   
        dict_animati={}
        self.warps=[]
        self.eventi=pygame.sprite.Group()
        #self.lista_beast=[]
        self.avatar = Miohero((hero_ini_pos), resolution//2,parentob=self,dormi=dormi)
        Engine.__init__(self, caption='Tiled Map with Renderer '+mappa, resolution=resolution, camera_target=self.avatar,map=self.tiled_map,frame_speed=0)
        self.State=State
        for O in self.prima_lista_ogg:
            animato={'pos':(O.rect.x,O.rect.y),'dir':str(O.name),'staifermo':False,'orientamento':"vuoto",'og_rect':O.rect}
            for p in O.properties:
                animato[p]=O.properties[p]
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
                        beast.motore=self
                    if O.properties['sottotipo']=='FaiParlare':
                        beast=FaiParlare(animato)
                        self.lista_beast[beast.id]=beast
                        beast.dialogosemp.lista_messaggi=self.dic_storia[beast.id]['messaggio']
                        beast.motore=self
                    if O.properties['sottotipo']=='AttivaAnimato':
                        beast=AttivaAnimato(animato)
                        self.lista_beast[beast.id]=beast
                        #if beast.id in self.dic_storia:
                            #beast.dialogosemp.lista_messaggi=self.dic_storia[beast.id]['messaggio']
                        beast.motore=self
                        
            
            if O.type=="animato":
                #animato={'pos':(O.rect.x,O.rect.y),'dir':str(O.name),'staifermo':False,'orientamento':"vuoto"}
                #for p in O.properties:
                    #animato[p]=O.properties[p]
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
                    beast=AnimatoMorente(animato)

                self.beast_sprite_group.add(beast.sprite_fotogrammanew)
                beast.debug=miodebug
                beast.dic_storia=animato['dic_storia']
                beast.staifermo=animato['staifermo']
                beast.orientamento=animato['orientamento']
                beast.motore=self
                self.lista_beast[beast.id]=beast
                self.avatar_group.add(beast)


        
        #miovar_dump(self.eventi.sprites()[0].rect)
        #exit()
        ## Insert avatar into the Fringe layer.
        self.avatar.rect.x=hero_ini_pos[0]
        self.avatar.rect.y=hero_ini_pos[1]
        self.avatar_group.add(self.avatar)

        #self.freccia=Proiettile(self)
 
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
        self.imm_fermo=self.avatar.sit_standing
        self.animato=self.camera.target.animated_object
        
        #con questa proprietà le collisioni vengono ignorate
        self.ignora_collisioni=ign_coll
        self.corsa=False

        ## Create the renderer.
        self.renderer = BasicMapRenderer(self.tiled_map, max_scroll_speed=State.speed)
        #self.dialogo_btn=False
        #self.crea_magazzino()
        self.mag=Magazzino(self)
        self.app_salvata=None
        self.blockedkeys=False
    #------------------------------------------------------------------ 
    
  
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
                self.is_raccolto_collide()
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
                #if callable(beast.dialogosemp.scrivi_frase):
                    beast.dialogosemp.scrivi_frase()
        #self.mag.aggiungi_magazzino()
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
                            pass
                        else:
                            blit(s.image, s.rect.move(-cx,-cy))
                            pass

    #---------------------------------------------------
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
                                self.__init__(resolution=(800,600),dir=dir,mappa=mappa,hero_ini_pos=(destx,desty),dormi=False)

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
   
    #------------------------------------------------------- 
    """
    def is_event_collide(self):
        newsprite=self.avatar.sprite
        hits=pygame.sprite.spritecollide(newsprite, self.eventi,False)
        if hits: 
            id_animato=hits[0].properties['id_animato']
            if hasattr(self.lista_beast[id_animato],'effetto_collisione_con_evento'):
                self.lista_beast[id_animato].effetto_collisione_con_evento(hits[0].properties)
                self.lista_beast['interlocutore'].prova()
            #if hits[0].properties['azione']=='attiva_animato':
            #    self.lista_beast[id_animato].attendi_evento=False #mette in moto l'animato che era in attesa dell'evento
            #else:
            #    print hits[0].properties['azione']
    """
    
    #-------------------------------------------------------        
    def is_raccolto_collide(self):
        newsprite=self.avatar.sprite
        hits=pygame.sprite.spritecollide(newsprite, self.raccolto_spathash.objects,False)
        if hits:
            for obj in hits:
                print "indice che punta alla posizione dell'immagine nel tileset png "+str(obj.img_idx)
                print self.raccoglibili_dict[str(obj.img_idx)]
                self.raccolti.append(obj)
                self.raccolto_spathash.remove(obj)
    
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
            hits=self.avatar.rect.colliderect(beast.talk_box)
            beast.fallo_parlare()
            if self.godebug:
                cx,cy = self.camera.rect.topleft
                #pygame.draw.rect(self.camera.surface, Color('red'), beast.talk_box.move(-cx,-cy))
                #pygame.draw.rect(self.camera.surface, Color('red'), beast.beast_hit_box.move(-cx,-cy))
                pygame.draw.rect(self.camera.surface, Color('red'), beast.sprite_fotogramma.rect.move(-cx,-cy))
            """if beast.dialogosemp.dialogo_btn:
                if hits:
                    #beast.set_dialogo_btn(True)
                    beast.dialogosemp.is_near=True
                    #beast.dialogosemp.sequenza_messaggi_new()
                    #beast.staifermo=True
                    beast.fermato=True
                    if hasattr(beast.dialogosemp,'sequenza_messaggi_noth'):
                        beast.dialogosemp.sequenza_messaggi_noth()
                else:
                    beast.dialogosemp.is_near=False
                    #beast.set_dialogo_btn(False)
                    beast.dialogosemp.dialogo_btn=False
                    beast.dialogosemp.open=False
                    beast.dialogosemp.idx_mess=0
                    beast.fermato=False"""

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
        elif key == K_UP or key == K_w: 
            self.cammina=True
            self.camera.target.giocatore_animato=self.animato['back_walk']
            self.movey += -State.speed
            if self.corsa:
                    self.movey += -State.speed
                    self.camera.target.giocatore_animato=self.animato['back_run']
        elif key == K_RIGHT or key == K_d: 
            self.cammina=True
            self.camera.target.giocatore_animato=self.animato['right_walk']
            self.movex += State.speed
            if self.corsa: 
                    self.camera.target.giocatore_animato=self.animato['right_run']
                    self.movex += State.speed
        elif key == K_LEFT or key == K_a: 
            self.cammina=True
            self.camera.target.giocatore_animato=self.animato['left_walk']
            self.movex += -State.speed
            if self.corsa:
                    self.movex += -State.speed
                    self.camera.target.giocatore_animato=self.animato['left_run']
        elif key==pygame.K_z:
            print "z"
            for k,beast in self.lista_beast.iteritems():
                beast.dialogosemp.incrementa_idx_mess()
        
        elif key == pygame.K_F4:
            #if not self.dialogo_btn:
                #self.dialogo_btn=True
            #else:
                #self.dialogo_btn=False
                
            pass
                
            #for k,beast in self.lista_beast.iteritems():
                #beast.dialogosemp.dialogo_btn=self.dialogo_btn
                #beast.dialogosemp.incrementa_idx_mess()
            #beast.dialogosemp.suono.play()
        
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
            print 'f7'
            print self.lista_beast['interlocutore'].id
            self.lista_beast['interlocutore'].attendi_evento=False
        elif key == pygame.K_F9:
            for k,beast in self.lista_beast.iteritems():
                print str(beast.id)+str(beast.dialogosemp.dialogo_btn)
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
        """ if button==3:
            self.mouse_down = True
            self.dialogo_btn=True
            for k,beast in self.lista_beast.iteritems():
                beast.dialogosemp.dialogo_btn=self.dialogo_btn"""
        if button==1:
            self.freccia=Proiettile(self,pos)
            self.freccia.mostra()

    #------------------------------------------------------------------ 
    def on_mouse_button_up(self, pos, button):
            self.mouse_down = False

    #------------------------------------------------------------------ 
    def on_key_up(self, key, mod):
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
        self.app_salvata=context.top()
        context.pop()
    
    def mio_riprendi(self):
        context.push(self.app_salvata)
        while context.top():
            State.clock.tick()

    #----------------------------------------------------------------------
#Eofclass#-----------------------------------------------------------------------------------			

def miomain(debug=True):
    oggetto=App_gum(resolution=(800,600),miodebug=debug)
    icon=pygame.image.load(".\immagini\\icona2.gif")
    pygame.display.set_icon(icon)
    gummworld2.run(oggetto)
    return oggetto
        

if __name__ == '__main__':
    #import profile
    miomain(debug=DEBUG)
        
     