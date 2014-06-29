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
from librerie import pyganim,gui
from miovardump import miovar_dump
from moving_beast import calcola_passi,MovingBeast,Dialogosemplice
from moving_animato import AnimatoSemplice,AnimatoParlanteAvvicina,AnimatoParlanteFermo
from moving_animato import AnimatoParlanteConEvento,MessaggioDaEvento,FaiParlare,AttivaAnimato,AnimatoFermo
from moving_animato import AnimatoSegue,AnimatoAttacca,AnimatoCambiaTipo
#from miovar_dump import *
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
        #print 'cambio dir a '+os.getcwd()
        os.chdir('..\\') 

#-------------------------------------------------------------------------------
class PguApp():
    def __init__(self,motore_genitore,inizio='menu'):
        self.motore=motore_genitore
        #mytheme = gui.Theme(dirs="gray")
        self.app = gui.Desktop(width=800,height=600)
        self.app.connect(gui.QUIT,self.app.quit,None)
        self.tabella = gui.Table(width=200,height=300,valign=-1,y=50)
        self.tabella.style.margin_top=150
        #print self.tabella.style.margin_top
        if inizio=="inventario":
            self.inventario()
        else:
            self.menu()
        
        self.app.init(self.tabella)
        self.mioloop=True
        clock = pygame.time.Clock()
        while self.mioloop:
                mousemotions = pygame.event.get(MOUSEMOTION)
                if mousemotions: #checks if the list is nonempty
                        mousemotion = mousemotions[-1]
                coda_eventi=pygame.event.get()
                for event in coda_eventi:
                        if event.type == pygame.QUIT:
                                self.mioloop = False
                        elif event.type == pygame.USEREVENT:
                                continue
                        elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_e:
                                        self.mioloop = False
                                if event.key == pygame.K_ESCAPE:
                                        self.mioloop = False
                                        
                        self.app.event(event)
                        self.app.paint()
                        pygame.display.flip()
                        clock.tick(60)
        pygame.key.set_repeat()
    #-------------------------------------------------------------------------------   
    def menu(self):
        self.tabella.tr()
        inventario=gui.Button(value='Inventario')
        inventario.connect(gui.CLICK,self.inventario)
        self.tabella.td(inventario)
        
        self.tabella.tr()
        inv_animali=gui.Button(value='Animali al seguito')
        inv_animali.connect(gui.CLICK,self.inventario_animali)
        self.tabella.td(inv_animali)

        self.tabella.tr()
        tornabtn=gui.Button(value='Torna al gioco')
        tornabtn.connect(gui.CLICK,self.quit)
        self.tabella.td(tornabtn)
        nrighe=self.tabella.getRows()
        self.tabella.style.height=nrighe*50
    #-------------------------------------------------------------------------------
    def scarica(self,id_cosa_raccolta,i,tab_riga,eti,immagine,idx_img):
        if id_cosa_raccolta in self.motore.lista_beast:
            self.motore.lista_beast[id_cosa_raccolta].segui=False
            try:del self.motore.mag.seguito[i]
            except:
                print "i="+str(i),self.motore.mag.seguito
                exit()
        else:
            obj=pygame.sprite.Sprite()
            obj.image=immagine.value
            obj.rect=obj.image.get_rect()
            obj.rect.x=self.motore.avatar.rect.x+16
            obj.rect.y=self.motore.avatar.rect.y+16
            obj.img_idx=idx_img
            self.motore.raccolto_spathash.add(obj)
            del self.motore.mag.raccolti[i]
        self.tabella.remove(tab_riga)
        self.tabella.remove(eti)
        self.tabella.remove(immagine)
    #-------------------------------------------------------------------------------
    def loop_inventario(self,lista_oggetti):
        for i,cosa in lista_oggetti.iteritems():
                eti=gui.Label(cosa[0]['nome'])
                immagine=gui.Image(cosa[1].image)
                self.tabella.tr()
                #ilab=gui.Label(str(i))
                #self.tabella.td(ilab)
                self.tabella.td(eti)
                self.tabella.td(immagine)
                font = pygame.font.SysFont("Tahoma", 12)
                L=gui.Link(value='Scarica',font=font)
                dic=cosa[0]
                if 'numero' in dic:idx_img=dic['numero'] 
                else:idx_img=0 
                L.connect(gui.CLICK,self.scarica,dic['nome'],i,L,eti,immagine,idx_img)
                self.tabella.td(L)
        nrighe=self.tabella.getRows()
        self.tabella.style.height=nrighe*10
    #-------------------------------------------------------------------------------       
    def inventario(self):
        self.tabella.clear()
        self.tabella.tr()
        etichetta=gui.Label("Inventario oggetti raccolti:")
        self.tabella.td(etichetta,colspan=2)
        self.loop_inventario(self.motore.mag.raccolti)
    #------------------------------------------------------------------------------- 
    def inventario_animali(self):
        self.tabella.clear()
        self.tabella.tr()
        etichetta=gui.Label("Animali al seguito:")
        self.tabella.td(etichetta,colspan=2)
        self.loop_inventario(self.motore.mag.seguito)
    #-------------------------------------------------------------------------------
    def quit(self):
        #print 'quit'
        self.mioloop=False
#EofCLass-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class AutoDict(dict):
    def __init__(self):
        dict.__init__(self)
        self.id=0
    def append(self,item):
        self.id=self.id+1
        self[self.id]=item
#EofClass

#-------------------------------------------------------------------------------
class Magazzino(model.Object):
    def __init__(self,motore):
        self.motore=motore
        from collections import defaultdict
        self.raccolti=AutoDict()
        self.seguito=AutoDict()
        #square=pygame.image.load('.\\immagini\\square1.png').convert_alpha()
        #self.background_magazzino =pygame.transform.scale(square,(State.screen.size[0]-1,100))
        #self.backvuoto=self.background_magazzino.copy()
        self.suono=pygame.mixer.Sound('suoni/message.wav')
    #-------------------------------------------------------        
    def is_raccolto_collide(self):
        newsprite=self.motore.avatar.sprite
        hits=pygame.sprite.spritecollide(newsprite, self.motore.raccolto_spathash.objects,False)
        if hits:
            for obj in hits:
                prop_ogg= self.motore.dict_gid_to_properties[obj.img_idx]
                #self.raccolti[obj.img_idx].append
                self.raccolti.append((prop_ogg,obj))
                self.motore.raccolto_spathash.remove(obj)
                self.suono.play()
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
class Proiettile(model.Object):
    
    #------------------------------------
    def __init__(self,motore,mouse_position,tipo='f'):
        self.freccia1=pygame.image.load('immagini/frnera.png')
        lasso=pygame.image.load('immagini/lasso.png')
        self.lasso=pygame.transform.scale(lasso,(64,15))
        if tipo=='f':self.dalanciare=self.freccia1
        elif tipo=='l':self.dalanciare=self.lasso
        else: self.dalanciare=self.freccia1
        #freccia=pygame.transform.scale(freccia,(72,72))
        
        pygame.mixer.init()
        self.motore=motore
        self.rect=self.image.get_rect()

        self.rect.x=self.motore.avatar.rect.x-self.dalanciare.get_width()/2
        self.rect.y=self.motore.avatar.rect.y-self.dalanciare.get_height()/2
        pos= self.motore.camera.screen_to_world(mouse_position)
        self.mouse_position=pos
        dify= (pos[1]-self.rect.y) 
        difx=  (pos[0]-self.rect.x)
        angolo_rads=math.atan2(dify,difx)
        #self.coefa=float(dify)/float(difx)

        self.dx=math.cos(angolo_rads)
        self.dy=math.sin(angolo_rads)
        self.dalanciare=pygame.transform.rotate(self.dalanciare, 360-angolo_rads*57.29)
        self.sprite=pygame.sprite.Sprite()
        self.sprite.image=self.dalanciare
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
                ogg_colpito=self.motore.lista_beast[hits[0].id]
                
                if ogg_colpito.id<>'Wolf':
                    #if hasattr(ogg_colpito,'miocingdying'):
                    if hasattr(ogg_colpito,'evento_colpito'):
                        ogg_colpito.evento_colpito()
                    self.colpito=True
                    self.motore.avatar_group.objects.remove(self)
                if self.motore.lista_beast[hits[0].id].sottotipo=='attaccante':
                    self.motore.lista_beast[hits[0].id].vaiattacca=True
            hitsover=pygame.sprite.spritecollide(self.sprite,self.motore.over_group,False)
            if hitsover:
                if hitsover[0].img_idx in self.motore.dict_gid_to_properties:
                        #print self.motore.dict_gid_to_properties[hitsover[0].img_idx]['nome']
                        pass
                else:
                        #print hitsover[0].img_idx
                        pass
                self.motore.suono_colpito.play()
                self.motore.avatar_group.objects.remove(self)
            #con coefficiente angolare
            #self.rect.x=self.rect.x+4
            #self.rect.y=self.rect.y+4*self.coefa
        
    #------------------------------------
    @property
    def image(self):
        #self.freccia=pygame.transform.rotate(self.freccia, 360-self.arcotangente*57.29)
        return self.dalanciare
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
        
#-------------------------------------------------------------------------------
class App_gum(Engine):
    def __init__(self,resolution=(400,200),dir=".\\mappe\\mappe_da_unire\\",mappa="casa_gioco.tmx",\
                            coll_invis=True,ign_coll=False,miodebug=False,hero_ini_pos=None,dormi=True):
        self.suono_colpito=pygame.mixer.Sound('suoni/colpito.wav')
        self.suono_noncolpito=pygame.mixer.Sound('suoni/non_colpito.wav')
        self.nuova_mappa_caricare=True
        self.fringe_i=1
        xml = open('animazioni\\prova.xml', 'r').read()
        self.dic_storia=xmltodict.parse(xml)['storia']
        self.lista_beast=[]
        self.lista_beast={}
        self.godebug=False
        
        #dialogo_btn=False
        self.beast_sprite_group=pygame.sprite.Group()
        #necessario per resettare la condizione messa dalla libreria PGU
        pygame.key.set_repeat()
        x = 20
        y = 80
        #import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)    
        
        resolution = Vec2d(resolution)
        #dir=".\\mappe\\"
        #mappa='mini.tmx'
        self.mappa_dirfile=dir+mappa
        
        self.tiled_map = TiledMap(dir+mappa)

        for mylayer in self.tiled_map.layers:
                if mylayer.name=="Collision":
                        self.collision_group_i= mylayer.layeri
                if mylayer.name=="Fringe":
                        self.fringe_i= mylayer.layeri
                if mylayer.name=="Over":
                        self.over_i= mylayer.layeri
                if mylayer.name=="raccolto": 
                        self.raccolto_layer=mylayer
                        self.raccolto_spathash=mylayer.objects

        self.dict_gid_to_properties={}
        for tileset in self.tiled_map.raw_map.tile_sets:
                for tile in tileset.tiles:
                        #print tile
                        tile.properties['parent_tileset_name']=tileset.name
                        gid=int(tileset.firstgid)+int(tile.id)
                        tile.properties['numero']=gid
                        self.dict_gid_to_properties[gid]=tile.properties
        #print self.dict_gid_to_properties
        #exit()
        
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
        self.over_group=self.tiled_map.layers[self.over_i]
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
        self.catturabili=pygame.sprite.Group()
        #self.lista_beast=[]
        self.avatar = Miohero((hero_ini_pos), resolution//2,parentob=self,dormi=dormi)
        self.direzione_avatar='front'
        #Engine.__init__(self, caption='Tiled Map with Renderer '+mappa, resolution=resolution, camera_target=self.avatar,map=self.tiled_map,frame_speed=0)
        Engine.__init__(self, caption='LandOfFire', resolution=resolution, camera_target=self.avatar,map=self.tiled_map,frame_speed=0)
        self.State=State
        for index,O in enumerate(self.prima_lista_ogg):
            if O.name==None:
                gid=int(O.gid)
                O.name=self.dict_gid_to_properties[gid]['Name']
                O.type='animato'
                O.properties['id']=O.name+str(index)
                O.properties['sottotipo']='parlantefermo'
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
                        #if beast.id in self.dic_storia:
                            #beast.dialogosemp.lista_messaggi=self.dic_storia[beast.id]['messaggio']
                    beast.motore=self
            #if O.type==None:
                #print O.name, O.properties
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
                    beast=AnimatoSemplice(animato)
                elif O.properties['sottotipo']=='animatosegue':
                    beast=AnimatoSegue(animato)
                elif O.properties['sottotipo']=='attaccante':
                    beast=AnimatoAttacca(animato)
                elif O.properties['sottotipo']=='catturabile':
                    beast=AnimatoCambiaTipo(animato)

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
        self.tipofreccia='f'

        #exit()
        #discorso_iniziale=None
        #if discorso_iniziale:
            #self.dialogogioco=Dialogo_gioco(self,lista_messaggi=discorso_iniziale)
            #self.dialogogioco.dialogo_show=True
    #EofInit------------------------------------------------------------------ 
    
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
    def warp_del_seguito(self):
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
                try:dir=warp.properties['dir']
                except:dir=".\\mappe\\mappe_da_unire\\"
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
                        self.warp_del_seguito() #verifica se nel passaggio di mappa deve portarsi dietro il cane o altro seguito
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
                pygame.draw.rect(self.camera.surface, Color('red'), beast.sprite_fotogramma.rect.move(-cx,-cy))
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
            #print 'f7'
            pgu=PguApp(self)
        elif key == pygame.K_e:
            pgu=PguApp(self,inizio="inventario")
        elif key == pygame.K_F9:
            print 'f9'
            self.lista_beast['jag1'].vaiattacca=True
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
            tipo=self.tipofreccia
            self.freccia=Proiettile(self,pos,tipo=tipo)
            self.freccia.mostra()

    #------------------------------------------------------------------ 
    def on_mouse_button_up(self, pos, button):
            self.mouse_down = False

    def on_key_up(self,key,mod):
        if not self.blockedkeys:
            self.on_key_up_incondizionato(key, mod)
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
    oggetto=App_gum(resolution=(800,600),miodebug=debug,hero_ini_pos=hero_ini_pos1)
    icon=pygame.image.load(".\immagini\\icona2.gif")
    pygame.display.set_icon(icon)
    gummworld2.run(oggetto)
    return oggetto
        

if __name__ == '__main__':


    
    miomain(debug=DEBUG,hero_ini_pos1=(0,0))
        
     