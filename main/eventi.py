# coding: utf-8
from moving_animato import *
from moving_beast import Dialogosemplice  

#--------------------------------------------
# Derivato da AnimatoParlanteFermo, con la differenza
# che comincia a parlare quando il personaggio avatar entra in
# una zona della mappa senza bisogno di contatto diretto
#--------------------------------------------
#Inizio Classe               
class AnimatoParlanteConEvento(AnimatoParlanteFermo):

    def __init__(self,animato):
        MovingBeast.__init__(self,animato,parlante=False)
        self.dialogosemp=Dialogosemplice(self)
        self.direzione='front'
    #-------------------------------------------------------------------------
    @property
    def is_persona_collide(self):
        pass
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        #if self.dialogosemp.dialogo_btn:
            self.dialogosemp.is_near=True
            self.fermato=True
            self.dialogosemp.sequenza_messaggi_noth()
    #-------------------------------------------------------------------------        
    def effetto_collisione_con_evento(self,proprieta_oggetto_evento):
        if proprieta_oggetto_evento['azione']=='parla':
            #self.dialogosemp.dialogo_btn=True
            self.dialogosemp.dialogo_show=True
            #self.dialogosemp.finito_dialogo=False
            self.dialogosemp.idx_mess=0
            #print "parla!"
            self.fallo_parlare()
        else:
            print proprieta_oggetto_evento['azione']
            
#EofClass
#---------------------------------------------------


#--------------------------------------------
# Derivato da AnimatoParlanteFermo, quando il personaggio avatar entra in
# una zona della mappa scattano i messaggi, nessuna animazione, l'animato non esiste
#--------------------------------------------               
class MessaggioDaEvento(AnimatoParlanteFermo):
    def __init__(self,animato):
        #MovingBeast.__init__(self,animato,parlante=False)
        self.id=animato['id']
        self.points = ((0,0),(0,0))
        self.miosprite=pygame.sprite.Sprite()
        self.miosprite.rect=animato['og_rect']
        self.miosprite.image=pygame.Surface((self.miosprite.rect.width, self.miosprite.rect.height))
        self.miosprite.image.set_alpha(0)
        self.attendi_evento=False
        self.finito_evento=False
        self.dialogosemp=Dialogosemplice(self)
        self.x=animato['pos'][0]+self.image.get_width()/2
        self.y=animato['pos'][1]+self.image.get_height()

    @property
    def fotogramma(self):
        return self.miosprite.image
    @property
    def image(self):
        #image=self.fotogramma
        return self.miosprite.image
    @property
    def sprite_fotogrammanew(self):
        return self.miosprite
    @property
    def evento_hit_box(self):
        return self.miosprite.rect
    
    #-------------------------------------------------------------------------
    @property
    def is_persona_collide(self):
        #chiamato da self.muovi_animato
        hits=self.evento_hit_box.colliderect(self.motore.avatar.sprite.rect)
        #print hits
        if hits:
            self.dialogosemp.dialogo_show=True
        #il dialogo viene chiuso in scrivi_frase quando trova finito_dialogo messo a True da incrementa_idx_mess
        #quindi dialogo_show non serve torni a False

    #--------------------------------------------------------------------------------
    def muovi_animato(self):
        #print self.dialogosemp.dialogo_btn
        a=self.is_persona_collide
        pass
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        #chiamato dal motore draw-<is_talking2->fallo_parlare
        self.fermato=True
        self.dialogosemp.dialogo_btn=True
        self.dialogosemp.is_near=True
        if not self.dialogosemp.finito_dialogo:
            self.attendi_evento=False
            self.dialogosemp.sequenza_messaggi_noth() 
        pass
    #-------------------------------------------------------------------------        
    def effetto_collisione_con_evento(self,proprieta_oggetto_evento):
        """
        self.dialogosemp.dialogo_btn=True
        #self.dialogosemp.finito_dialogo=False
        self.dialogosemp.idx_mess=0
        self.fallo_parlare() """
        pass
#EofClass
#---------------------------------------------------




#---------------------------------------------------
# E' uguale a MessaggioDaEvento, tranne che
# i messaggi sono quelli associati ad una animazione
# che parla quando l'avatar entra nell'area dell'evento
class FaiParlare(MessaggioDaEvento):
    def __init__(self,animato):
        MessaggioDaEvento.__init__(self,animato)
        self.id=animato['id_animato']
        #print self.id
#EofClass        



#---------------------------------------------------
# E' uguale a FaiParlare, tranne che
# avvia una animazione
# che prima  appare quando l'avatar entra nell'area dell'evento
# e poi si avvicina all'avatae e parla quando raggiunge l'avatar a 
#--------------------------------------------------              
class AttivaAnimato(MessaggioDaEvento):
    def __init__(self,animato):
        MessaggioDaEvento.__init__(self,animato)
        #self.id=animato['id_animato']
        self.id_animato=animato['id_animato']
        #print "attiva animato"
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        hits=self.motore.avatar.rect.colliderect(self.talk_box)
        if hits:
            self.motore.lista_beast[self.id_animato].attendi_evento=False
            if self.motore.lista_beast[self.id_animato].dialogosemp.finito_dialogo:
                self.motore.lista_beast[self.id_animato].dialogosemp.dialogo_show=False
                self.dialogosemp.dialogo_show=False
                self.motore.blockedkeys=False
                #print "collisione con area attiva animato!"+str(self.motore.blockedkeys)

#EofClass

#-------------------------
#Evento che si attiva se nel recinto ci sono almeno x animali
class EventoRecinto():
    def __init__(self,oggetto_sulla_mappa,motore):
        self.motore=motore
        self.rect=oggetto_sulla_mappa.rect
        self.mesprite=oggetto_sulla_mappa
        self.id=oggetto_sulla_mappa.properties['id']
        self.attendi_evento=False
        self.finito_evento=False
        self.dialogosemp=Dialogosemplice(self)
        self.dialogosemp.lista_messaggi=['Hai radunato tutto il bestiame!','liberalo nel recinto usando il selettore..']
    #-------------------------------------------------------------------------
    def controlla_se_attivo(self):
        #hits=self.motore.avatar.rect.colliderect(self.rect)
        hits=pygame.sprite.spritecollide(self.mesprite,self.motore.beast_sprite_group,False)
        if hits:
            if len(hits)>=3:
                self.attendi_evento=False
                self.dialogosemp.is_near=True
                self.dialogosemp.dialogo_show=True
                #print self.dialogosemp.lista_messaggi
                self.dialogosemp.sequenza_messaggi_noth() 
                self.dialogosemp.scrivi_frase()
    #-------------------------------------------------------------------------
#EofClass

class EventoMessaggio():
    def __init__(self,oggetto_sulla_mappa,motore):
        self.motore=motore
        self.mesprite=oggetto_sulla_mappa
        self.id=oggetto_sulla_mappa.properties['id']
        self.attendi_evento=False
        self.finito_evento=False
        self.dialogosemp=Dialogosemplice(self)
        if 'messaggi' in oggetto_sulla_mappa.properties:
            lista_messaggi=oggetto_sulla_mappa.properties['messaggi'].split(';')
            self.dialogosemp.lista_messaggi=lista_messaggi
        else:
            self.dialogosemp.lista_messaggi=self.motore.dic_storia[self.id]['messaggio']
    #-------------------------------------------------------------------------        
    def controlla_se_attivo(self):
        hits=self.mesprite.rect.colliderect(self.motore.avatar.hitbox)
        if hits:
            self.attendi_evento=False
            self.dialogosemp.is_near=True
            self.dialogosemp.dialogo_show=True
            #print self.dialogosemp.lista_messaggi
            self.dialogosemp.sequenza_messaggi_noth() 
            self.dialogosemp.scrivi_frase()
    #-------------------------------------------------------------------------
#EofClass       