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
#import cProfile, pstats
from gummworld2 import context, data, model, geometry, toolkit
from gummworld2 import Engine, State, TiledMap, BasicMapRenderer, Vec2d
from librerie import pyganim,gui

from miovardump import miovar_dump
from moving_beast import calcola_passi,MovingBeast,Dialogosemplice
from moving_animato import AnimatoSemplice,AnimatoParlanteAvvicina,AnimatoParlanteFermo
from moving_animato import AnimatoParlanteConEvento,MessaggioDaEvento,FaiParlare,AttivaAnimato,AnimatoFermo
from moving_animato import AnimatoSegue,AnimatoAttacca,AnimatoCambiaTipo
from armi_utensili import *
#from miovar_dump import *
#from dialogosemp import Dialogosemplice
from librerie import xmltodict
#import subprocess
import math
from math import atan2,pi
import time
DEBUG=False
try:
    __builtin__.miavar
except:
    try:
        os.stat('animation')
    except:
        #print 'cambio dir a '+os.getcwd()
        os.chdir('..\\') 

class DialogoAvvisi(gui.Dialog):
    def __init__(self,**params):
        testo=params['testo']
        self.scrivi_testo(testo)
        self.init_app()
    def scrivi_testo(self,testo):
        title = gui.Label("Avviso")
        doc = gui.Document(width=200,height=200)
        gui.Dialog.__init__(self,title,doc)
        space = title.style.font.size(" ")
        for word in testo.split(" "): 
            doc.add(gui.Label(word))
            doc.space(space)
        doc.br(space[1])
    def init_app(self):
        area=pygame.Rect(300,200,400,400)
        app = gui.App()
        self.open()
        app.init(screen=State.screen.surface,widget=self,area=area)
        app.paint()
        pygame.display.flip()
        while 1:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                break
        pygame.key.set_repeat()
        
#EofClass----------------

class Selettore(gui.Container):
    def __init__(self,**params):
        motore=params['motore']
        if motore.mag.selezionabili:
            if not True in motore.mag.selezionabili.values():
                firstkey=motore.mag.selezionabili.iterkeys().next()
                motore.mag.selezionabili[firstkey]=True
            sprite_selez=self.individua_selezionato(motore.mag.selezionabili,motore.mag.raccolti)
        else:
            return
        
        if sprite_selez==None:
            dialog = DialogoAvvisi(testo="Seleziona un'arma o uno strumento da usare! (tasto E)")
            return
        self.immagine=gui.Image(sprite_selez.image)
        self.dic_selezionabili=motore.mag.selezionabili
        self.dic_raccolti=motore.mag.raccolti
        w=40
        h=40
        posx=(800-w)/2
        posy=600-h
        self.doc = gui.Document(width=w,height=h,valign=-1,align=0)
        self.doc.add(self.immagine,align=-1)
        titlewidg = gui.Label("Sel")
        #gui.Dialog.__init__(self,titlewidg,self.doc,valign=-1,align=-1)
        self.my_dialog_init(titlewidg,self.doc)
        area=pygame.Rect(posx,posy,w,h)
        self.app = gui.App()
        
        self.open()
        self.app.init(screen=State.screen.surface,widget=self,area=area)
        self.app.paint()
        pygame.display.flip()
        #miovar_dump(self.app.theme)
        self.ciclo()
    #-----------------------------
    def my_dialog_init(self,title,main,**params):
        params.setdefault('cls','selettore')
        #gui.Table.__init__(self,**params)
        #self.tr()
        #self.td(main,colspan=2,cls=self.cls+".main")
        gui.Container.__init__(self,**params)
        self.add(main,0,0)
        
    #-----------------------------
    def individua_selezionato(self,lista,dic_raccolti):
        selezionato=None
        sprite_selez=None
        for nome,condizione in lista.iteritems():
            if condizione:
                selezionato=nome
                self.selez=nome
        if selezionato is not None:
            for key,record in dic_raccolti.iteritems():
                if record[0]['nome']==selezionato:
                    sprite_selez=record[1]          
        return sprite_selez
    #------------------------------
    def cambia_selez(self,verso='next'):
        for k,condizione in self.dic_selezionabili.iteritems():
            if condizione:
                self.dic_selezionabili[k]=False
                if verso=='next':
                    scelto=self.dic_next[1][k]
                elif verso=='prev':
                    scelto=self.dic_next[0][k]
                if scelto is None:
                    scelto=self.dic_selezionabili.keys()[0]
                self.dic_selezionabili[scelto]=True
                break
        sprite_selez=self.individua_selezionato(self.dic_selezionabili,self.dic_raccolti)
        self.doc.remove(self.immagine)
        self.immagine=gui.Image(sprite_selez.image)
        self.doc.add(self.immagine,align=-1)
        self.app.paint()
        pygame.display.flip()
    #--------------------------------------------------
    def neighborhood(self,iterable):
        iterator = iter(iterable)
        prev = None
        item = iterator.next()  # throws StopIteration if empty.
        for next in iterator:
            yield (prev,item,next)
            prev = item
            item = next
        yield (prev,item,None)
    #----------------------------------
    @property
    def dic_next(self):
        mydic_next=dict()
        mydic_prev=dict()
        for lista_vicini in self.neighborhood(self.dic_selezionabili):
            previous=lista_vicini[0]
            next=lista_vicini[2]
            item=lista_vicini[1]
            mydic_prev[item]=previous
            mydic_next[item]=next
        return (mydic_prev,mydic_next)
    #----------------------------
    def ciclo(self):
        while 1:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                if event.button==4 or event.button==5:
                    self.cambia_selez()
                else:
                    break
            if event.type == KEYDOWN:
                if event.key == K_h or event.key ==K_ESCAPE:
                    break
                if event.key==K_RIGHT:
                    self.cambia_selez(verso='next')
                if event.key==K_LEFT:
                    self.cambia_selez(verso='prev')
                    
        pygame.key.set_repeat()
#EofClass----------------    

#-------------------------------------------------------------------------------
class PguApp():
    def __init__(self,motore_genitore,inizio='menu'):
        self.motore=motore_genitore
        #mytheme = gui.Theme(dirs="gray")
        self.app = gui.Desktop(width=800,height=600)
        self.app.connect(gui.QUIT,self.app.quit,None)
        self.tabella = gui.Table(width=200,height=300,valign=-1,y=50)
        self.tabella.style.margin_top=150
        selezionatoimg=pygame.image.load('.\\immagini\\selezionato.png').convert_alpha()
        self.selezionatoimg=pygame.transform.scale(selezionatoimg,(28,28))
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
                            self.quit()
                        elif event.type == pygame.USEREVENT:
                            continue
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button==4:
                                print 'prossimo'
                            if event.button==5:
                                print "precedente"
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_e:
                                self.quit()
                            if event.key == pygame.K_ESCAPE:
                                self.quit()
                                    
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
    def scarica(self,id_cosa_raccolta,i,tab_riga,eti,immagine,idx_img,sel):
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
            
            nomestrumento=self.motore.mag.raccolti[i][0]['nome']
            self.motore.mag.raccolti.pop(i)
            self.motore.mag.selezionabili.pop(nomestrumento)
        self.tabella.remove(tab_riga)
        self.tabella.remove(eti)
        self.tabella.remove(immagine)
        self.tabella.remove(sel)
    #-------------------------------------------------------------------------------
    def loop_inventario(self,lista_oggetti):
        sel_val=''
        for s in self.motore.mag.selezionabili:
            if self.motore.mag.selezionabili[s] ==True:sel_val=s
        
        self.g = gui.Group(name='armi',value=sel_val)
        unchainimg=pygame.image.load('.\\immagini\\unchain.png').convert_alpha()
        unchainimg=pygame.transform.scale(unchainimg,(20,20))
        iconunchain=gui.Image(unchainimg)
        for i,cosa in lista_oggetti.iteritems():
                eti=gui.Label(cosa[0]['nome'])
                immagine=gui.Image(cosa[1].image)
                self.tabella.tr()
                self.tabella.td(eti)
                self.tabella.td(immagine)
                L=gui.Button(iconunchain)
                dic=cosa[0]
                if 'numero' in dic:idx_img=dic['numero'] 
                else:idx_img=0 
                sel=gui.Radio(self.g,value=dic['nome'])
                L.connect(gui.CLICK,self.scarica,dic['nome'],i,L,eti,immagine,idx_img,sel)
                self.tabella.td(L)
                self.tabella.td(sel)
        nrighe=self.tabella.getRows()
        self.tabella.style.height=nrighe*10
    #-------------------------------------------------------------------------------       
    def inventario(self):
        self.tabella.clear()
        self.tabella.tr()
        if len(self.motore.mag.raccolti)==0:
            etichetta=gui.Label("Avvicinati a qualcosa per raccoglierlo")
        else:
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
        for s in self.motore.mag.selezionabili:
            self.motore.mag.selezionabili[s]=False
        if self.g.value in self.motore.mag.selezionabili:
            self.motore.mag.selezionabili[self.g.value]=True
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
        self.selezionabili=dict()
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
                nomestrumento=prop_ogg['nome']
                self.selezionabili[nomestrumento]=False
                self.motore.raccolto_spathash.remove(obj)
                self.suono.play()
        #self.selezionabili['arco']=True
    def delete_selezionabile(self,key):
        self.selezionabili.pop(key)
#-------------------------------------------------------------------------------


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
        if hasattr(self.parent,'arma') and not self.parent.cammina:
            self.parent.arma.draw_arma()
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
class Arma(object):
    def __init__(self,parent,nomeutensile='spada'):
        self.parent=parent
        #self.load(nomeutensile)

    #def load(self,nomeutensile):
    #    arma=pygame.image.load('immagini/'+nomeutensile+'.png').convert()
    #    self.arma=pygame.transform.scale(arma,(16,16))
        
    @property
    def arma_img(self):
        colorkey = self.arma.get_at((0,0))
        self.arma.set_colorkey(colorkey, RLEACCEL)
        return self.arma
    
    def draw(self):
        cx,cy=self.parent.State.camera.rect.topleft
        img=self.arma_img
        avatar=self.parent.avatar
        direzione=self.parent.direzione_avatar
        if not avatar.dormi:
            x=avatar.rect.x-cx
            y=avatar.rect.y-cy
            if direzione=='right':
                x=avatar.rect.x-cx-3
                y=avatar.rect.y-cy-9
            elif direzione=='left':
                img=pygame.transform.flip(self.arma_img,True,False)
                y=avatar.rect.y-cy-9
                x=avatar.rect.x-cx-25
            elif direzione=='front':
                y=avatar.rect.y-cy-4
                x=avatar.rect.x-cx-12
            elif direzione=='back':
                img=pygame.transform.rotate(self.arma_img,200)
                img=pygame.transform.scale(img,(10,10))
                y=avatar.rect.y-cy+5
                x=avatar.rect.x-cx
            #print direzione+str(x)+ str(y)
            self.parent.screen.blit(img,(x,y))
    
    def draw_arma(self):
        if 'spada' in self.parent.mag.selezionabili:
            if self.parent.mag.selezionabili['spada']:
                arma=pygame.image.load('immagini/spada.png').convert()
                self.arma=pygame.transform.scale(arma,(16,16))
                self.draw()
        if 'piccone' in self.parent.mag.selezionabili:
            if self.parent.mag.selezionabili['piccone']:
                arma=pygame.image.load('immagini/piccone.png').convert()
                self.arma=pygame.transform.scale(arma,(24,24))
                self.draw()
            
#--EofClass---------------------------------------------------------                

        
#-------------------------------------------------------------------------------
class Motore(Engine):
    def __init__(self,resolution=(400,200),dir=".\\mappe\\mappe_da_unire\\",mappa="casa_gioco.tmx",\
                            coll_invis=True,ign_coll=False,miodebug=False,hero_ini_pos=None,dormi=True):
        self.suono_colpito=pygame.mixer.Sound('suoni/colpito.wav')
        self.suono_noncolpito=pygame.mixer.Sound('suoni/non_colpito2.wav')
        self.suono_cilecca=pygame.mixer.Sound('suoni/cilecca.wav')
        self.fringe_i=1
        xml = open('animazioni\\prova.xml', 'r').read()
        self.dic_storia=xmltodict.parse(xml)['storia']
        self.lista_beast=[]
        self.lista_beast={}
        self.godebug=False
        
        #necessario per resettare la condizione messa dalla libreria PGU
        pygame.key.set_repeat()
        x = 20
        y = 80
        self.cammina=False   
        self.corsa=False
        #import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)    
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
        self.dict_gid_to_properties={}
        self.arma=Arma(self)
        self.avatar = Miohero((hero_ini_pos), resolution//2,parentob=self,dormi=dormi)
        self.direzione_avatar='front'
        self.imm_fermo=self.avatar.sit_standing
        dir_mappa=dir+mappa
        self.init_mappa(dir_mappa=dir_mappa,coll_invis=coll_invis,hero_ini_pos=hero_ini_pos,resolution=resolution,dormi=dormi,miodebug=miodebug)

    #EofInit------------------------------------------------------------------ 
    
    def init_mappa(self,dir_mappa='',coll_invis=True,hero_ini_pos=(0,0),resolution=(800,600),dormi=True,miodebug=True):
        self.warps=[]
        self.eventi=pygame.sprite.Group()
        self.beast_sprite_group=pygame.sprite.Group()
        self.mappa_dirfile=dir_mappa
        self.tiled_map = TiledMap(dir_mappa)
        for mylayer in self.tiled_map.layers:
                if mylayer.name=="Ground1":
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
        print hero_ini_pos
        self.avatar.position=hero_ini_pos
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
                    beast.motore=self

            if O.type=="animato":
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
        self.renderer = BasicMapRenderer(self.tiled_map, max_scroll_speed=State.speed)
        
    
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
                        elif isinstance(s,UtensilePiccone):
                            s.muovi()
                            blit(s.image, s.rect.move(-cx,-cy))
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
                        #self.__init__(resolution=(800,600),dir=dir,mappa=mappa,hero_ini_pos=(destx,desty),dormi=False)
                        self.init_mappa(dir_mappa=dir+mappa,hero_ini_pos=(destx,desty),resolution=(800,600),dormi=False,miodebug=False)
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
        elif key==pygame.K_h:
            print "h"
            selettore=Selettore(motore=self)
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
                if 'utensile' in locals():
                    utensile.mostra()
                else:
                    dialog = DialogoAvvisi(testo="Seleziona un'arma o uno strumento da usare! (tasto E)")

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
    oggetto=Motore(resolution=(800,600),miodebug=debug,hero_ini_pos=hero_ini_pos1)
    icon=pygame.image.load(".\immagini\\icona2.gif")
    pygame.display.set_icon(icon)
    gummworld2.run(oggetto)
    return oggetto
        

if __name__ == '__main__':


    
    miomain(debug=DEBUG,hero_ini_pos1=(0,0))
        
     