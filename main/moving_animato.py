# coding: utf-8
from moving_beast import calcola_passi,MovingBeast,Dialogosemplice
import datetime
from random import randint
import pygame
from pygame.locals import *
from miovar_dump import *

#Inizio Classe               
class AnimatoSemplice(MovingBeast):
    #---------------------------------------
    #Animazione di unità che non parla e non affronta il personaggio avatar
    #limitandosi a camminare avanti e indietro secondo il percorso della proprietà points
    #della retta con una pausa indicata in durata_pausa
    #----------------------------------------
    #----------------------------------------
    def __init__(self,animato):
        MovingBeast.__init__(self,animato,parlante=False)
        self.dialogosemp=type('obj', (object,), {'dialogo_btn' : False}) # qui la proprietà dialogo_btn viene settata a False
    #----------------------------------------
    @property
    def draw_fotogramma(self):
        return True
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        pass
        #hits=self.motore.avatar.rect.colliderect(self.talk_box)
        #print hits
    
    #----------------------------------------
    def muovi_animato(self):
        if self.auto: ##verifica se deve procedere a calcolare una nuova sequenza di passi
            if self.contatore_destinazioni>len(self.lista_destinazioni)-1: 
                    self.contatore_destinazioni=0 #resetta il contatore della lista delle destinazioni automatiche
                    self.segmento=0
            if (self.x,self.y)==self.lista_destinazioni[self.contatore_destinazioni]:
                    print "destinazione uguale a partenza"
                    self.x=self.x+3
                    self.y=self.y+3
                    #exit()
            self.listap=calcola_passi(or_pos=(self.x,self.y),target_pos=self.lista_destinazioni[self.contatore_destinazioni])  #qui viene compilata la lista dei passi da seguire per camminare nel percorso
            pos_da_raggiungere=self.listap[len(self.listap)-1] #legge la posizione finale di destinazione dalla lista delle destinazioni
            self.direzione=self.calcola_direzione((self.x,self.y),pos_da_raggiungere) #calcola la direzione della destinazione da raggiungere
            self.contatore_destinazioni=self.contatore_destinazioni+1 #incrementa il contatore delle destinazioni
            self.auto=False #arresta il cinghiale quando ha fatto una singola camminata
            self.lanciato=False #setta il timer su fermo mentre la camminata è in corso
        #sezione che effettivamente muove l'animazione, ma solo se non èin pausa o non è fermata
        if self.is_walking and not self.fermato and not self.is_persona_collide: 
            self.scegli_fotogramma_animazione(self.miocing,self.direzione)
        else:
            if (self.direzione=='right') or (self.direzione=='SE') or (self.direzione=='NE'): 
                self.fotogramma=self.miocing.animObjs['right_stand'].ritorna_fotogramma()
            elif (self.direzione=='left') or (self.direzione=='SW') or (self.direzione=='NW'): 
                self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()
        if (self.lanciato==False) and (self.is_walking==False) and (self.staifermo==False):
                self.mio_timer_pausa() #lancia il timer che conta i secondi della pausa passati come parametro a MovingBeast()
                fotog_sprite=self.sprite_fotogramma
        if self.miotimer: #controlla ad ogni ciclo se è attivo un timer e se la pausa di quel timer è scaduta
            self.miotimer.check_time()
        return self.fotogramma
#---------------------------------------------------
#fine della Classe


#---------------------------------------------------
#Inizio Classe               
class AnimatoParlanteAvvicina(MovingBeast):
    #---------------------------------------
    #Animazione di unità che affronta il personaggio avatar
    #iniziando a parlare
    #----------------------------------------
    in_uscita=False
    #----------------------------------------
    @property
    def draw_fotogramma(self):
        if self.attendi_evento or self.finito_evento:
            return False
        else:
            return True
    def effetto_collisione_con_evento(self,proprieta_oggetto_evento):
        #print proprieta_oggetto_evento
        if proprieta_oggetto_evento['azione']=='attiva_animato':
            self.attendi_evento=False
        else:
            print proprieta_oggetto_evento['azione']
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        hits=self.motore.avatar.rect.colliderect(self.talk_box)
        if self.dialogosemp.dialogo_btn:
            if hits:
                #beast.set_dialogo_btn(True)
                self.dialogosemp.is_near=True
                #beast.dialogosemp.sequenza_messaggi_new()
                #beast.staifermo=True
                self.fermato=True
                if hasattr(self.dialogosemp,'sequenza_messaggi_noth'):
                    self.dialogosemp.sequenza_messaggi_noth()
            else:
                self.dialogosemp.is_near=False
                #beast.set_dialogo_btn(False)
                self.dialogosemp.dialogo_btn=False
                self.dialogosemp.open=False
                self.dialogosemp.idx_mess=0
                self.fermato=False
    #----------------------------------------
    def muovi_animato(self):
        if self.dialogosemp.lista_messaggi==['...']:
                try:
                    if type(self.dic_storia['messaggio']) is not list: self.dic_storia['messaggio']=[self.dic_storia['messaggio']]
                except:
                    self.dic_storia['messaggio']=['nulla']
                self.dialogosemp.lista_messaggi=self.dic_storia['messaggio']

        if self.auto: ##verifica se deve procedere a calcolare una nuova sequenza di passi
            if self.contatore_destinazioni>len(self.lista_destinazioni)-1: 
                    self.contatore_destinazioni=0 #resetta il contatore della lista delle destinazioni automatiche
                    self.segmento=0
            if (self.x,self.y)==self.lista_destinazioni[self.contatore_destinazioni]:
                    #"destinazione uguale a partenza"
                    self.x=self.x+3
                    self.y=self.y+3

            self.listap=calcola_passi(or_pos=(self.x,self.y),target_pos=self.lista_destinazioni[self.contatore_destinazioni])  #qui viene compilata la lista dei passi da seguire per camminare nel percorso
            pos_da_raggiungere=self.listap[len(self.listap)-1] #legge la posizione finale di destinazione dalla lista delle destinazioni
            self.direzione=self.calcola_direzione((self.x,self.y),pos_da_raggiungere) #calcola la direzione della destinazione da raggiungere
            self.contatore_destinazioni=self.contatore_destinazioni+1 #incrementa il contatore delle destinazioni
            self.auto=False #arresta il cinghiale quando ha fatto una singola camminata
            self.lanciato=False #setta il timer su fermo mentre la camminata è in corso
        
        #sezione che effettivamente muove l'animazione, ma solo se non èin pausa o non è fermata
        if self.is_walking and not self.fermato and not self.is_persona_collide: 
            self.scegli_fotogramma_animazione(self.miocing,self.direzione)
        elif self.in_uscita:
            if not self.finito_evento:self.scegli_fotogramma_animazione(self.miocing,self.direzione)
        else:
            if (self.direzione=='right') or (self.direzione=='SE') or (self.direzione=='NE'): 
                self.fotogramma=self.miocing.animObjs['right_stand'].ritorna_fotogramma()
            elif (self.direzione=='left') or (self.direzione=='SW') or (self.direzione=='NW'): 
                self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()
        
        if (self.lanciato==False) and (self.is_walking==False) and (self.staifermo==False):
                self.mio_timer_pausa() #lancia il timer che conta i secondi della pausa passati come parametro a MovingBeast()
                fotog_sprite=self.sprite_fotogramma
        
        if self.miotimer: #controlla ad ogni ciclo se è attivo un timer e se la pausa di quel timer è scaduta
            self.miotimer.check_time()
        
        if self.dialogosemp.finito_dialogo:
            self.staifermo=False
            if not self.in_uscita:
                #points=[(11,82),(11,78)]
                #self.lista_destinazioni=self.calcola_points(points,self.posizione_iniziale_animato)
                self.listap=calcola_passi(or_pos=(self.x,self.y),target_pos=self.lista_destinazioni[0])
                pos_da_raggiungere=self.listap[len(self.listap)-1] #legge la posizione finale di destinazione dalla lista delle destinazioni
                self.direzione=self.calcola_direzione((self.x,self.y),pos_da_raggiungere) #calcola la direzione della destinazione da raggiungere
            self.in_uscita=True
            if len(self.listap)==0:
                self.attendi_evento=True
                self.finito_evento=True
            #print self.lista_destinazioni
            
        return self.fotogramma
        #---------------------------------------------------
#EofClass

#---------------------------------------------------
#Inizio Classe               
class AnimatoParlanteFermo(MovingBeast):
    direzione='front'
    is_walking=False
    #----------------------------------------
    @property
    def draw_fotogramma(self):
        return True
    #-------------------------------------------------------------------------
    @property
    def is_persona_collide(self):
        self.dialogosemp.dialogo_btn=True
        self.dialogosemp.finito_dialogo=False
        newsprite=self.motore.avatar.sprite
        hits=self.beast_hit_box.colliderect(newsprite.rect)
        #hits=pygame.sprite.collide_rect(newsprite, self.sprite_fotogramma)
        if hits:
            #self.mostra_esclamazione()
            self.dialogosemp.dialogo_btn=True
            self.dialogosemp.idx_mess=0
            return True
        else:
            return False
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        hits=self.motore.avatar.rect.colliderect(self.talk_box)
        if self.dialogosemp.dialogo_btn:
            if hits:
                #beast.set_dialogo_btn(True)
                self.dialogosemp.is_near=True
                #beast.dialogosemp.sequenza_messaggi_new()
                #beast.staifermo=True
                self.fermato=True
                if hasattr(self.dialogosemp,'sequenza_messaggi_noth'):
                    self.dialogosemp.sequenza_messaggi_noth()
            else:
                self.dialogosemp.is_near=False
                #beast.set_dialogo_btn(False)
                self.dialogosemp.dialogo_btn=False
                self.dialogosemp.open=False
                self.dialogosemp.idx_mess=0
                self.fermato=False
    #-------------------------------------------------------------------------
    def scegli_fotogramma_animazione(self,miocing,direzione):
        self.direzione=direzione
        if direzione=='left':
            self.fotogramma=miocing.animObjs['left_walk'].ritorna_fotogramma()
        elif direzione=='front':
            self.fotogramma=miocing.animObjs['front_walk'].ritorna_fotogramma()
        elif direzione=='right':
            self.fotogramma=miocing.animObjs['right_walk'].ritorna_fotogramma()
        elif direzione=='back':
            self.fotogramma=miocing.animObjs['back_walk'].ritorna_fotogramma()
        elif direzione=='SW':
            self.fotogramma=miocing.animObjs['SW'].ritorna_fotogramma()
        elif direzione=='NW':
            self.fotogramma=miocing.animObjs['NW'].ritorna_fotogramma()
        elif direzione=='SE':
            self.fotogramma=miocing.animObjs['SE'].ritorna_fotogramma()
        elif direzione=='NE':
            self.fotogramma=miocing.animObjs['NE'].ritorna_fotogramma()
        return self.fotogramma
    #--------------------------------------------------------------------------------
    def muovi_animato(self):
        if self.dialogosemp.lista_messaggi==['...']:
                try:
                    if type(self.dic_storia['messaggio']) is not list: self.dic_storia['messaggio']=[self.dic_storia['messaggio']]
                except:
                    self.dic_storia['messaggio']=['nulla']
                self.dialogosemp.lista_messaggi=self.dic_storia['messaggio']
        direzioni=['left','right','front','back','SW','NW','NE','SE']
        adesso= datetime.datetime.time(datetime.datetime.now()).second
        adesso1= int(adesso%5)
        if adesso1==0:
            if not self.giacambiato:
                numdirez=len(direzioni)
                self.direzione=direzioni[randint(0,numdirez-1)]
                self.giacambiato=True
        else:
            self.giacambiato=False
        #sezione che effettivamente muove l'animazione, ma solo se non èin pausa o non è fermata
        self.scegli_fotogramma_animazione(self.miocing,self.direzione)
        if self.is_persona_collide:
            pass
        return True
#EofClass



#---------------------------------------------------
#Inizio Classe               
class AnimatoParlanteConEvento(AnimatoParlanteFermo):
    #--------------------------------------------
    # Derivato da AnimatoParlanteFermo, con la differenza
    # che comincia a parlare quando il personaggio avatar entra in
    # una zona della mappa senza bisogno di contatto diretto
    #--------------------------------------------
    def __init__(self,animato):
        MovingBeast.__init__(self,animato,parlante=False)
        self.dialogosemp=Dialogosemplice(self)
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
            self.dialogosemp.dialogo_btn=True
            #self.dialogosemp.finito_dialogo=False
            self.dialogosemp.idx_mess=0
            #print "parla!"
            self.fallo_parlare()
        else:
            print proprieta_oggetto_evento['azione']
            
#EofClass
#---------------------------------------------------

#---------------------------------------------------
#Inizio Classe               
class AnimatoMessaggioDaEvento(AnimatoParlanteFermo):
    #--------------------------------------------
    # Derivato da AnimatoParlanteFermo, quando il personaggio avatar entra in
    # una zona della mappa scattano i messaggi, nessuna animazione, l'animato non esiste
    #--------------------------------------------
    def __init__(self,animato):
        #MovingBeast.__init__(self,animato,parlante=False)
        self.id=animato['id']
        self.points = ((0,0),(0,0))
        self.miosprite=pygame.sprite.Sprite()
        self.miosprite.image=pygame.Surface((50, 50))
        self.miosprite.image.set_alpha(0)
        self.attendi_evento=True
        self.finito_evento=False
        self.dialogosemp=Dialogosemplice(self)
        self.x=animato['pos'][0]++self.image.get_width()/2
        self.y=animato['pos'][1]+self.image.get_height()
        #print animato['pos']
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
    #-------------------------------------------------------------------------
    @property
    def is_persona_collide(self):
        pass
    #--------------------------------------------------------------------------------
    def muovi_animato(self):
        pass
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        self.fermato=True
        self.dialogosemp.dialogo_btn=True
        self.dialogosemp.is_near=True
        #print "parla!"+str(self.dialogosemp.lista_messaggi)
        if not self.dialogosemp.finito_dialogo:
            self.attendi_evento=False
            self.dialogosemp.sequenza_messaggi_noth()
    #-------------------------------------------------------------------------        
    def effetto_collisione_con_evento(self,proprieta_oggetto_evento):
        self.dialogosemp.dialogo_btn=True
        #self.dialogosemp.finito_dialogo=False
        self.dialogosemp.idx_mess=0
        self.fallo_parlare()

            
#EofClass
#---------------------------------------------------