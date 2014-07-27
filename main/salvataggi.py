import pickle
import pygame
from pygame.locals import *
from pygame import sprite,time
from miovardump import miovar_dump
from moving_beast import MovingBeast

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
            O=MyO()
            O.rect.x=a['posizione'][0]
            O.rect.y=a['posizione'][1]
            O.name=a['name']
            O.type=a['type']
            O.gid=a['gid']
            O.properties=a['properties']
            O.image=a['image']
            O.image_source=a['image_source']
            animato={'id':O.properties['id'],'pos':(O.rect.x,O.rect.y),'dir':str(O.name),'staifermo':False,'orientamento':"vuoto",\
                            'og_rect':O.rect,'sottotipo':O.properties['sottotipo'],'points':O.properties['points']}
            dict_animati={}
            motore.popola_lista_beast(O,dict_animati,animato)

        
    #-----------------------------
    def salva(self,motore=None):
        dati=dict()
        dati['matr_layer_raccolto']=motore.matr_layer_raccolto
        dati['avatar_pos']=motore.avatar.position
        dati['animati']=list()
        for id,beast in motore.lista_beast.iteritems():
            properties=beast.properties
            dic_da_agg={'id':id,'classe':beast.classe,'is_segui':beast.segui,'posizione':(int(beast.x),int(beast.y)),'name':beast.name,'properties':properties,'type':beast.type,'gid':beast.gid,'image':None,'image_source':beast.image_source}
            dati['animati'].append(dic_da_agg)
        filename="saved\\salvataggio.txt"
        pickle.dump(dati, open(filename,"wb" ) )

    #-----------------------------
    def ricarica(self,motore=None):
        filename="saved\\salvataggio.txt"
        dati=pickle.load(open( filename, "rb" ))
        nuovamatrice=dati['matr_layer_raccolto']
        motore.mag.ricostruisci_layer_raccolto(nuovamatrice)
        motore.avatar.position=dati['avatar_pos']
        motore.avatar.rect.x=dati['avatar_pos'][0]
        motore.avatar.rect.y=dati['avatar_pos'][1]
        motore.avatar_group.add(motore.avatar)
        del motore.lista_beast
        motore.lista_beast=dict()
        for layer in motore.overlays:
            sprites = layer.objects.intersect_objects(motore.State.camera.rect)
            for s in sprites:
                if isinstance(s,MovingBeast):
                    motore.avatar_group.objects.remove(s)
        animati_caricati=dati['animati']
        self.ricostruisci_animati(animati_caricati,motore)
#Eofclass#-------------------------------------------------