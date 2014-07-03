import pygame
import math
#-------------------------------------------------------------------------------
class Proiettile(object):
    #------------------------------------
    def __init__(self,motore,mouse_position):
        self.freccia1=pygame.image.load('immagini/frnera.png')
        lasso=pygame.image.load('immagini/lasso.png')
        self.lasso=pygame.transform.scale(lasso,(64,15))
        pygame.mixer.init()
        self.motore=motore
        tipo=self.tipo_proiettile
        if tipo=='arco':  self.dalanciare=self.freccia1
        elif tipo=='lasso': self.dalanciare=self.lasso
        if hasattr(self,'dalanciare'):
            self.orienta_proiettile(mouse_position)
     #------------------------------------
    def orienta_proiettile(self,mouse_position):
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
    @property
    def tipo_proiettile(self):
        for arma,selettore in self.motore.mag.selezionabili.iteritems():
            if selettore:
                return arma
    #------------------------------------
    def mostra(self):
        if hasattr(self,'rect'):
            self.motore.avatar_group.add(self)
    #------------------------------------
    def muovi(self): 
        if not self.colpito:
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

class UtensileSpada(object):
    def __init__(self,motore,mouse_position):
        #Proiettile.__init__(self,motore,mouse_position)
        pygame.mixer.init()
        self.motore=motore
        self.check_corpo_a_corpo()
    #------------------------------------
    def check_corpo_a_corpo(self):
        hits= pygame.sprite.spritecollide(self.motore.avatar.sprite,self.motore.beast_sprite_group, False)
        if hits:
            ogg_colpito=self.motore.lista_beast[hits[0].id]
            if hasattr(ogg_colpito,'evento_colpito'):
                ogg_colpito.evento_colpito()
            self.colpito=True
    #------------------------------------
    def muovi(self): 
        pass
    #------------------------------------
    def mostra(self):
        pass
    #------------------------------------
    @property
    def image(self):
        pass
#-------------------------------------------------------------------------------#end of class

class UtensilePiccone(object):
    def __init__(self,motore,mouse_position):
        pygame.mixer.init()
        self.motore=motore
        self.check_collision()
    #------------------------------------
    def check_collision(self):
        hits= pygame.sprite.spritecollide(self.motore.avatar.sprite,self.motore.collision_group, False)
        if hits:
            print hits
    #------------------------------------
    def muovi(self): 
        pass
    #------------------------------------
    def mostra(self):
        pass
    #------------------------------------
    @property
    def image(self):
        pass
#-------------------------------------------------------------------------------#end of class