# coding: utf-8                     
import sys
import os

import __builtin__
import pygame
from pygame.locals import *
import sys
import time
import paths
from librerie import miovar_dump
from librerie import pyganim
import gummworld2
from gummworld2 import geometry,model,data
from random import randint


import threading
import datetime
from pygame.sprite import Sprite
from miovar_dump import *
from beast1 import Beast
from beast2 import Beast2
from dialogosemp import Dialogosemplice

#evento_timer = USEREVENT


def calcola_passi(or_pos=(300,200),target_pos=(200,200)):
        
        distanza=int(geometry.distance(or_pos,target_pos))
        lista_posizioni=[]
        for progress_distance in range(1,distanza):  
                p= geometry.step_toward_point(or_pos, target_pos, progress_distance)
                lista_posizioni.append(p)
        return lista_posizioni


#-------------------------------------------------
class Pseudo_async_timer():
        scaduto=False
        id=None
        def __init__(self,pausa,func,id=None):
                pausa=pausa/1000
                self.set_future_time(pausa)
                self.pausa=pausa
                self.id=id
                self.func_da_chiamare=func
        def set_future_time(self,pausa):
                t = time.time()
                self.fut_t=t+pausa
        def check_time(self):
                tnow=time.time()
                if (tnow>self.fut_t):
                        if not self.scaduto:
                                self.scaduto=True
                                self.func_da_chiamare()
                                return True
#-------------------------------------------------




#Inizio Classe               
class MovingBeast(model.Object):
        debug=False
        miotimer=None
        segmento=0
        dic_storia={'messaggio':'...'}
        messaggio_dato=False
        motore=None
        fermato=False
        staifermo=False
        def __init__(self,position=(100,100),durata_pausa=1000,id=1,points=(()),dir_name='boar'):
            model.Object.__init__(self)
            if dir_name=='boar' or dir_name=='priest':
                    self.miocing=Beast(dir_name=dir_name)
            else:
                    self.miocing=Beast2(dir_name=dir_name)
            self.id=id
            self.x=position[0]
            self.y=position[1]
            
            
            #points = [(3,3), (200,200)]
            if points:
                self.lista_destinazioni=self.calcola_points(points,position)
                self.x=self.lista_destinazioni[0][0]
                self.y=self.lista_destinazioni[0][1]
            else:
                self.lista_destinazioni=self.comp_lista_destinazioni(self.x,self.y)
            self.contatore_destinazioni=0
            self.listap=[]
            self.auto=True
            self.lanciato=False
            self.inpausa=False
            self.fotogramma=self.miocing.left_standing
            self.miocing.moveConductor.play()
            self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()
            self.durata_pausa=durata_pausa
            self.dialogosemp=Dialogosemplice()
            print "dic_storia"+str(self.dic_storia)
            #self.dialogosemp.lista_messaggi=self.dic_storia['messaggio']

        
        def calcola_points(self,points,position):
            real_points=[]
            for singlepos in points:
                newx=position[0]+singlepos[0]
                newy=position[1]+singlepos[1]
                couple=(newx,newy)
                real_points.append(couple)
            return real_points

 
        def comp_lista_destinazioni(self,x,y):
            lista_destinazioni=[]
            x=x-50
            y=y
            lista_destinazioni.append((x,y))
            y=y+50
            lista_destinazioni.append((x,y))
            x=x+150
            lista_destinazioni.append((x,y))
            x=x-100
            y=y-100
            lista_destinazioni.append((x,y))
            return lista_destinazioni
   
        def calcola_direzione(self,pos,mousepos):
            angolo= geometry.angle_of(pos,mousepos)
            ore=(angolo*100/360)*12
            if ore>100 and ore<200:
                    direzione='NE'
            elif ore>400 and ore<500:
                    direzione='SE'
            elif ore>700 and ore<800:
                    direzione='SW'
            elif ore>1000 and ore<1100:
                    direzione='NW'
            elif ore>1100 or ore<100:
                    direzione='back'
            elif ore>500 and ore<700:
                    direzione='front'
            elif ore>200 and ore<400:
                    direzione='right'
            elif ore>800 and ore<1000:
                    direzione='left'
            return direzione
        
        #-------------------------------------------------------------------------
        def scegli_fotogramma_animazione(self,miocing,direzione):
            self.direzione=direzione
            if len(self.listap)>0:  ##inizia la camminata
                if not self.staifermo:
                    #qui vengono impostati x e y del fotogramma da proiettare prendendoli dalla lista della camminata self.listap
                    pos= self.listap.pop(0)
                    self.x,self.y=pos ##qui vengono impostati x e y del fotogramma da proiettare sullo schermo prendendoli dalla lista della camminata self.listap
                    #fine impostazione
                
                miocing.moveConductor.play()
                #di seguito viene selezionata l'iimmagine a seconda della direzione della camminata; x e y sono già stati impostati
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
        
        @property
        def is_walking(self):
            if len(self.listap)>0:
                return True
            else:
                return False
        
        @property
        def sprite_fotogramma(self):
            fotog_sprite=pygame.sprite.Sprite()
            fotog_sprite.image=self.fotogramma
            fotog_sprite.rect=self.fotogramma.get_rect()
            fotog_sprite.rect.x=self.x
            fotog_sprite.rect.y=self.y-fotog_sprite.rect.height
            return fotog_sprite
        
        @property
        def rect(self):
            rect=self.sprite_fotogramma.rect
            return rect
        
        @property
        def image(self):
            image=self.fotogramma
            return image
        
        
        @property
        def talk_box(self):
            talk_box=self.rect
            if self.rect.height<100: talk_box.height=self.rect.height+120
            else:talk_box.height=self.rect.height
            if talk_box.width<100:talk_box.width=self.rect.width+120
            else: talk_box.width=self.rect.width
            y = self.rect.y
            x= self.rect.x
            talk_box.y=y
            talk_box.x=x
            return talk_box
        
        #--------------------------------------------------------------------------------
        def mio_timer_pausa(self):
            adesso= datetime.datetime.time(datetime.datetime.now())
            if self.debug:print "timer per la pausa del oggetto partito "+str(adesso)
            self.lanciato=True
            self.inpausa=True
            self.auto=False  ##con auto=false il ciclo di muovi_cinghiale() non gira
            fun_callback=self.fine_pausa
            self.miotimer=Pseudo_async_timer(self.durata_pausa,fun_callback,1) #crea l'ggetto timer con la pausa presa dai par di MovingBeast()
            #print "segmento completato n. "+str(self.segmento)
            self.segmento=self.segmento+1
         #--------------------------------------------------------------------------------        
        def fine_pausa(self): ##questa procedura si avvia ogni n secondi e fa muovere il cinghiale e poi fermarsi
            self.auto=True  ##con auto=True può girare il ciclo in muovi_cinghiale() quindi è finita la pausa
            self.lanciato=False
            self.inpausa=False
            adesso= datetime.datetime.time(datetime.datetime.now())
            if self.debug:print "finita pausa del oggetto "+str(adesso)
            self.miotimer=None
        #--------------------------------------------------------------------------------
        
        def check_storia(self):
            try:
                #if self.segmento==int(self.dic_storia['segmento']) and self.messaggio_dato==False:
                if self.messaggio_dato==False:
                    #self.motore.dialogo.testo=self.dic_storia['messaggio']
                    self.motore.dialogo.open=True
                    #self.messaggio_dato=True
                    #self.fermato=True
            except:
                pass
            
            #if self.motore:
            #    if self.motore.dialogo.close_clicked:
            #        self.fermato=False
                            
                
        #----------------------------------------
        def muovi_animato(self):
            if self.dialogosemp.lista_messaggi==['...']:
                if type(self.dic_storia['messaggio']) is not list : self.dic_storia['messaggio']=[self.dic_storia['messaggio']]
                self.dialogosemp.lista_messaggi=self.dic_storia['messaggio']
            
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
            else:
                if self.staifermo:
                    direzioni=['left_walk','right-walk','front_walk','back_walk','SW','NW','SW','NE','SE']
                    adesso= datetime.datetime.time(datetime.datetime.now()).microsecond/1000
                    adesso1= int(adesso/4)
                    if adesso1>230:
                        self.direzione=direzioni[randint(0,8)]
                        #print self.direzione
            
            #sezione che effettivamente muove l'animazione, ma solo se non è in pausa o non è fermata
            if self.is_walking and not self.fermato: 
            #if self.is_walking:
                self.scegli_fotogramma_animazione(self.miocing,self.direzione)
            else:
                if (self.direzione=='right') or (self.direzione=='SE') or (self.direzione=='NE'): 
                        self.fotogramma=self.miocing.animObjs['right_stand'].ritorna_fotogramma()
                elif (self.direzione=='left') or (self.direzione=='SW') or (self.direzione=='NW'): 
                        self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()

            if (self.lanciato==False) and (self.is_walking==False): 
                    self.mio_timer_pausa() #lancia il timer che conta i secondi della pausa passati come parametro a MovingBeast()
                    fotog_sprite=self.sprite_fotogramma
            
            if self.miotimer: #controlla ad ogni ciclo se è attivo un timer e se la pausa di quel timer è scaduta
                self.miotimer.check_time()
            
            #self.check_storia() #controlla ad ogni ciclo se deve mandare un messaggio

            return self.fotogramma
        #---------------------------------------------------
#fine della Classe




                    
def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 300))
    dir_name="aio"
    pygame.display.set_caption('Animato in movimento: '+dir_name)
    BGCOLOR = (180, 180, 180)
    mainClock = pygame.time.Clock()
    
    
    bestia=MovingBeast(dir_name=dir_name)
    bestia.staifermo=True
    

    #print ogg.sprite_fotogramma.rect
    while True:
        #print bestia.dialogosemp.lista_messaggi
        screen.fill(BGCOLOR)
        bestia.muovi_animato()

        screen.blit(bestia.sprite_fotogramma.image, (bestia.rect.x, bestia.rect.y))

        for event in pygame.event.get(): # event handling loop
            # handle ending the program
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_F4:
                    print 'f4'
                    bestia.dialogosemp.open=True
                    """
                    if not bestia.fermato:
                        bestia.fermato=True
                    else:
                        bestia.fermato=False
                    """
        bestia.dialogosemp.scrivi_frase()
        pygame.display.flip()
        mainClock.tick(40) # Feel free to experiment with any FPS setting.
              
                    
if __name__ == '__main__':
    #ciclo=MovingBeast()
    main()