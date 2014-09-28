import pickle
import pygame
import array
import copy
from pygame.locals import *
from pygame import sprite,time
from miovardump import miovar_dump
from moving_beast import MovingBeast
from weakref import WeakKeyDictionary

class Salvataggio():
    def __init__(self):
        self.matr_layer_raccolto=[]
        self.avatar_pos=(100,100)
        
    #-----------------------------
    def ricostruisci_animati(self,animati_caricati,motore):
        class MyO(pygame.sprite.Sprite):
            def __init__(self):
                pygame.sprite.Sprite.__init__(self)
                self.rect = pygame.rect.Rect(0,0,32,32)

        for a in animati_caricati:
            #print a['posizione']
            O=MyO()
            O.rect.x=a['posizione'][0]
            O.rect.y=a['posizione'][1]
            O.name=a['name']
            O.type=a['type']
            O.gid=a['gid']
            O.properties=a['properties']
            O.image=a['image']
            O.image_source=a['image_source']
            animato={'is_segui':a['is_segui'],'id':O.properties['id'],'pos':(O.rect.x,O.rect.y),'dir':str(O.name),'staifermo':False,'orientamento':"vuoto",\
                            'og_rect':O.rect,'sottotipo':O.properties['sottotipo'],'points':O.properties['points']}
            #print animato
            dict_animati={}
            motore.popola_lista_beast(O,dict_animati,animato)

        
    
    #-------------------------------------------------------        
    def azzera_layer_raccolto(self,motore):
        rect = pygame.Rect(0,0, motore.tiled_map.pixel_width+1, motore.tiled_map.pixel_height+1)
        cell_size = max(motore.tiled_map.tile_width, motore.tiled_map.tile_height)
        motore.raccolto_spathash.__init__(rect,cell_size) #azzera tutto il layer delle celle raccoglibili
        colonne=len(motore.matr_layer_raccolto[0])
        righe=len(motore.matr_layer_raccolto)
        newcontent2D = []
        #myarr=[]
        myarr=[0 for i in range(colonne)]
        #myarr.extend(myarr1)
        newcontent2D=[copy.copy(myarr) for i in range(righe)]
        motore.matr_layer_raccolto=newcontent2D
        #print motore.matr_layer_raccolto
        """
        j=0
        for r in motore.matr_layer_raccolto:
            i=0
            for c in r:
                if c<>0:
                    motore.matr_layer_raccolto[j][i]=0
                i=i+1
            j=j+1
        print motore.matr_layer_raccolto
        """
    
    #-------------------------------------------------------            
    def ricostruisci_layer_raccolto(self,content2D,motore):
        self.azzera_layer_raccolto(motore)
        #print "inizio ricostruzione: " +str(content2D)
        larg_tile=int(motore.tiled_map.tile_width)
        alt_tile=int(motore.tiled_map.tile_height)
        for r,row in enumerate(content2D):
            for c,cell in enumerate(row):
                myobj=pygame.sprite.Sprite()
                myobj.name=(r,c)
                myobj.img_idx=long(cell)
                pixposx=int(r)*larg_tile
                pixposy=int(c)*alt_tile
                rect=pygame.Rect(pixposx,pixposy,larg_tile,alt_tile)
                myobj.rect=rect
                if myobj.img_idx<>0:
                    #print type(myobj.img_idx)
                    offx,offy,tile_img = motore.tiled_map.mio_resource.indexed_tiles[myobj.img_idx]
                    myobj.image=tile_img
                    motore.raccolto_spathash.add(myobj)
                    #non funziona da una mappa all'altra se le 2 mappe non hanno esattamente gli stessi tilesets
                    motore.matr_layer_raccolto[r][c]=myobj.img_idx
        #print "fine ricostruzione: " +str(self.motore.matr_layer_raccolto[22])
    
        
    #-----------------------------
    def salva(self,motore=None,manuale=False):
        filename="saved\\salvataggio.txt"
        try:
            root_dati=pickle.load(open( filename, "rb" ))
        except:
            root_dati=dict()
        dati=dict()
        dati['matr_layer_raccolto']=motore.matr_layer_raccolto
        
        #print "sto salvando in "+str(motore.mappa_dirfile)+" "+str(motore.matr_layer_raccolto[22][17])
        
        if manuale: dati['avatar_pos']=motore.avatar.position
        dati['dormi']=motore.avatar.dormi
        dati['cammina']=motore.cammina
        
        dati['animati']=list()
        root_dati['lista_seguito']=list()
        #print motore.mag.raccolti
        for id,beast in motore.lista_beast.iteritems():
            if beast.id in motore.mag.seguito.lista_nomi_seguito:
                properties1=beast.properties
                dic_da_agg_seg={'id':id,'classe':beast.classe,'is_segui':beast.segui,'posizione':(int(beast.x),int(beast.y)),'name':beast.name,\
                    'properties':properties1,'type':beast.type,'gid':beast.gid,'image':None,'image_source':beast.image_source}
                root_dati['lista_seguito'].append(dic_da_agg_seg)
            else:
                properties=beast.properties
                dic_da_agg={'id':id,'classe':beast.classe,'is_segui':beast.segui,'posizione':(int(beast.x),int(beast.y)),'name':beast.name,\
                    'properties':properties,'type':beast.type,'gid':beast.gid,'image':None,'image_source':beast.image_source}
                dati['animati'].append(dic_da_agg)

        root_dati['quale_mappa']=motore.mappa_dirfile
        root_dati[motore.mappa_dirfile]=dati
        pickle.dump(root_dati, open(filename,"wb" ) )
    
    def carica_mappa(self):
        exit()
    
    def reset_avatar(self,motore,dati):
        motore.cammina=dati['cammina']
        if 'avatar_pos' in dati: 
            motore.avatar.position=dati['avatar_pos']
            motore.avatar.rect.x=dati['avatar_pos'][0]
            motore.avatar.rect.y=dati['avatar_pos'][1]
        motore.avatar.dormi=dati['dormi']
        motore.avatar_group.add(motore.avatar)
        
    def reset_animati_old(self,motore,dati):
        del motore.lista_beast
        motore.lista_beast=dict()
        for layer in motore.overlays:
            sprites = layer.objects.intersect_objects(motore.State.camera.rect)
            for s in sprites:
                if isinstance(s,MovingBeast):
                    motore.avatar_group.objects.remove(s)
        animati_caricati=dati['animati']
        self.ricostruisci_animati(animati_caricati,motore)
    
    def reset_animati(self,motore,dati):
        del motore.lista_beast
        motore.lista_beast=dict()
        rect = pygame.Rect(0,0, motore.tiled_map.pixel_width+1, motore.tiled_map.pixel_height+1)
        #cell_size = max(motore.tiled_map.tile_width, motore.tiled_map.tile_height)
        #motore.avatar_group.objects.__init__(rect,cell_size) #azzera tutto il layer
        for layer in motore.overlays:
            sprites = layer.objects.intersect_objects(rect)
            motore.beast_sprite_group.empty()
            for s in sprites:
                if isinstance(s,MovingBeast):
                    motore.avatar_group.objects.remove(s)
        animati_caricati=dati['animati']
        self.ricostruisci_animati(animati_caricati,motore)
        
    def reset_utensili(self,motore,dati):
        nuovamatrice=dati['matr_layer_raccolto']

        #print "sto resettando"+str(nuovamatrice[22])
        self.ricostruisci_layer_raccolto(nuovamatrice,motore)
        #print "matrice resettata "+str(motore.matr_layer_raccolto[22])
        
    
    #-----------------------------
    def ricarica(self,motore=None,qualemappa=None):
        filename="saved\\salvataggio.txt"
        root_dati=pickle.load(open( filename, "rb" ))

        if qualemappa is None : qualemappa=root_dati['quale_mappa']
        if qualemappa<>motore.mappa_dirfile:
            #print qualemappa
            #self.carica_mappa()
            pass
        if qualemappa in root_dati:
            dati=root_dati[qualemappa]
            
            #ressetta la situazione degli oggetti raccolti allo stato precedente
            self.reset_utensili(motore,dati)
            #resetta la situazione dell'avatar
            self.reset_avatar(motore,dati)
            #resetta la situazione degli animati allo stato precedente
            self.reset_animati(motore,dati)
        
        lista_seguito=root_dati['lista_seguito']

        #print "listas"+str(lista_seguito)
        self.ricostruisci_animati(lista_seguito,motore)

#Eofclass#-------------------------------------------------