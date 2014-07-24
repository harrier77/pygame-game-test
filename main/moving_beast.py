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


#import threading
import datetime
from pygame.sprite import Sprite

#from beast1 import Beast
#from beast2 import Beast2
import glob
#from dialogosemp import Dialogosemplice

#evento_timer = USEREVENT

#-----------------------------------------
# converts a state 
# (for example "collission detected")
# into an event 
#----------------------------------------
class StateToEvent():
    def __init__(self,id):
        self.id=id
        self.stack=['False']
    def check_state(self,state):
        if state<>self.stack[0]:
            self.stack.insert(0,state)
            ultimo=len(self.stack)-1
            self.stack.pop(ultimo)
            return self.toggle_ev(self.stack[0])
    def toggle_ev(self,stato):
        if stato:
            mioev=True
        else:
            mioev=False
        return mioev
#----------------------------------------


#ClassDialogoSemplice
class Dialogosemplice():
    
    #-----------------------------------------------------
    def __init__(self,moving_beast_genitore):
        self.is_near=False
        self.testo="Hello!"
        self.close_clicked=False
        self.beeped=False
        self.scritto=False
        self.sequenza_partita=False
        self.sequenza_finita=True
        self.lista_messaggi=['...']
        self.text_altezza=50
        self.crossrect=None
        #self.dialogo_btn=False
        self.dialogo_show=False
        self.finito_dialogo=False
        self.idx_mess=0
        self.conta_click=0
        self.is_triang=False
  
        self.moving_beast_genitore=moving_beast_genitore
        self.screen=pygame.display.get_surface()
        #self.background_txt = pygame.Surface((self.screen.get_size()[0]-1,self.text_altezza))
        square=pygame.image.load('.\\immagini\\square.png').convert_alpha()
        triangle=pygame.image.load('.\\immagini\\triangle.png').convert_alpha()
        self.triangle=pygame.transform.scale(triangle,(15,10))
        self.background_txt =pygame.transform.scale(square,(self.screen.get_size()[0]-1,self.text_altezza))
        self.backvuoto=self.background_txt.copy()
        #self.background_txt.fill((250, 250, 250))
        self.bgrect=self.background_txt.get_rect()
        self.bgrect.top=self.screen.get_size()[1]-self.text_altezza
        self.font=pygame.font.Font(data.filepath('font', 'Vera.ttf'), 18)
        #self.disegna_crocetta()
        pygame.mixer.init()
        self.suono=pygame.mixer.Sound('immagini/message.wav')
        #self.seq=MessageTimerClass(self.lista_messaggi,self)
        self.st_to_e1=StateToEvent(moving_beast_genitore.id)
        self.st_to_e2=StateToEvent(moving_beast_genitore.id)
        
    
    """
    def disegna_crocetta(self):
        self.cross=pygame.image.load('.\\immagini\\cross.gif')
        self.crossrect=self.cross.get_rect()
        self.crossrect.x=self.bgrect.topright[0]-15
        self.crossrect.y=self.bgrect.y
        self.crossrect.width=self.crossrect.width
        self.crossrect.height=self.crossrect.height
    """
    def disegna_messaggio(self):
        #self.disegna_triangolo()
        self.screen.blit(self.background_txt,(self.bgrect.x,self.bgrect.y))
        
    
    #-----------------------------------------------------
    def mywrite(self):
        #self.background_txt.fill((250, 250, 250))
        #font = pygame.font.Font(None, 32)
        text = self.font.render(self.testo, True, (10, 10, 10),(255,255,255))
        self.background_txt=self.backvuoto.copy() #qui ogni volta viene sbiancato il contenuto del riquadro dialogo
        
        self.background_txt.blit(text,(10,10))
        self.disegna_triangolo()
        
        #self.screen.blit(self.background_txt,(self.bgrect.x,self.bgrect.y))
        self.disegna_messaggio()
        self.scritto=True
        type_filter=pygame.MOUSEBUTTONDOWN
        e=self.moving_beast_genitore.motore.State.mioevento
        self.gestione_eventi(e)

    #-----------------------------------------------------
    def scrivi_frase(self):	
        
        #if self.dialogo_show:
        if self.st_to_e1.check_state(self.dialogo_show):
            self.moving_beast_genitore.motore.blockedkeys=True #qui viene bloccata la tastiera fino alla fine della sequenza messaggi
        elif self.st_to_e2.check_state(self.finito_dialogo):
            self.moving_beast_genitore.motore.blockedkeys=False #serve a riabilitare  la tastiera
        #il problema è che la tastiere è unica e sta sul motore e le variabili di tutti i dialoghi vengono controllate ogni volta e ce nè sempre un'altra che sblocca la tastiera
        #serve verificare se è entrato o uscito dalla collisione,  Ma anche se si fa, non esce più perché è bloccato, serve comunque una seconda variabile self.finito_dialogo che metta fine al blocco
        
        if self.is_near:
            if self.dialogo_show==True:
                if not self.finito_dialogo:
                    self.mywrite()
        else:
            self.scritto=False
        
    
    #-----------------------------------------------------
    def sequenza_messaggi_noth(self):
        if self.lista_messaggi[0]=='nulla':
            self.is_near=False
            return
        else:
            #if not self.sequenza_partita:
            self.testo=self.lista_messaggi[self.idx_mess]
            #if self.sequenza_finita:
            #    self.sequenza_partita=False
     #-----------------------------------------------------
    def disegna_triangolo(self):
        x=self.background_txt.get_width()-self.triangle.get_width()-10
        y=self.background_txt.get_height()-self.triangle.get_height()-10
        
        if self.conta_click<=len(self.lista_messaggi)-2:
            self.background_txt.blit(self.triangle,(x,y))
    
    
    #-----------------------------------------------------
    def incrementa_idx_mess(self):
        max_idx=len(self.lista_messaggi)-1
        if self.conta_click>=max_idx or self.idx_mess>=max_idx:
            self.conta_click=self.idx_mess=0
            self.moving_beast_genitore.staifermo=False
            self.moving_beast_genitore.fermato=False
            self.finito_dialogo=True
            self.dialogo_show=False
        else:
            self.conta_click=self.conta_click+1
            self.idx_mess=self.conta_click
        self.sequenza_messaggi_noth()
            
    #---------------------------------------------------------
    
    def gestione_eventi(self,event):
        if event:
            #if event.type == pygame.QUIT:
                #context.pop()      
            if event.type==pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.incrementa_idx_mess()
                self.moving_beast_genitore.motore.State.mioevento=None

#FineCLasse

#inizio classe
class Beast2():
    
    def __init__(self,dir_name="missionario",duration=0.1):
        
        self.motore=None
        #anim_file_name=dir_name
        variable_path_name=dir_name
        self.animatlabel=variable_path_name
        self.front_standing = pygame.image.load('animazioni/animation/'+variable_path_name+'front_walk.001.png')
        self.back_standing = pygame.image.load('animazioni/animation/'+variable_path_name+'back_walk.001.png')
        self.left_standing = pygame.image.load('animazioni/animation/'+variable_path_name+'left_walk.001.png')
        
        
        
        self.right_standing = pygame.transform.flip(self.left_standing, True, False)
        self.playerWidth, self.playerHeight = self.front_standing.get_size()
        self.rect=self.front_standing.get_rect()
        
        
        # creating the PygAnimation objects for walking/running in all directions
        animTypes = 'left_walk back_walk front_walk NW SW'.split()
        #animTypes = 'back_walk front_walk left_walk'.split()
        #conteggio_fotog=6
        self.animObjs = {}
        for animType in animTypes:
            conteggio_fotog= len(glob.glob('animazioni/animation/'+variable_path_name+"/"+animType+"*.png"))
            
            imagesAndDurations = [('animazioni/animation/'+variable_path_name+'%s.%s.png' % (animType, str(num).rjust(3, '0')), duration) for num in range(conteggio_fotog)]
            self.animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)
        #my_aniType=['left_stand']
        #for animType in my_aniType:
        #    imagesAndDurations1 = [('animazioni/animation/'+variable_path_name+'%s.%s.png' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
        #    self.animObjs[animType] = pyganim.PygAnimation(imagesAndDurations1)
        #my_aniType='left_stand'
        
        file_img='animazioni/animation/'+variable_path_name+'left_walk.000.png'
        imagesAndDurations1 = [(file_img,0.1)]
        self.animObjs['left_stand'] = pyganim.PygAnimation(imagesAndDurations1)
        
        file_img='animazioni/animation/'+variable_path_name+'front_walk.000.png'
        imagesAndDurations1 = [(file_img,0.1)]
        self.animObjs['front_stand'] = pyganim.PygAnimation(imagesAndDurations1)
        
        file_img='animazioni/animation/'+variable_path_name+'back_walk.000.png'
        imagesAndDurations1 = [(file_img,0.1)]
        self.animObjs['back_stand'] = pyganim.PygAnimation(imagesAndDurations1)
        
        #create the right-facing sprites by copying and flipping the left-facing sprites
        self.animObjs['right_walk'] = self.animObjs['left_walk'].getCopy()
        self.animObjs['right_walk'].flip(True, False)
        self.animObjs['right_walk'].makeTransformsPermanent()
        
        self.animObjs['SE'] = self.animObjs['SW'].getCopy()
        self.animObjs['SE'].flip(True, False)
        self.animObjs['SE'].makeTransformsPermanent()
        
        self.animObjs['NE'] = self.animObjs['NW'].getCopy()
        self.animObjs['NE'].flip(True, False)
        self.animObjs['NE'].makeTransformsPermanent()
        
        self.animObjs['right_stand'] = self.animObjs['left_stand'].getCopy()
        self.animObjs['right_stand'].flip(True, False)
        self.animObjs['right_stand'].makeTransformsPermanent()
   
        self.moveConductor = pyganim.PygConductor(self.animObjs)
        

        
#fine classe -------------------------------------

def calcola_passi(or_pos=(300,200),target_pos=(200,200)):
        
        distanza=int(geometry.distance(or_pos,target_pos))
        lista_posizioni=[]
        for progress_distance in range(1,distanza):  
                p= geometry.step_toward_point(or_pos, target_pos, progress_distance)
                lista_posizioni.append(p)
        return lista_posizioni


#-------------------------------------------------
class Pseudo_async_timer():

    def __init__(self,pausa,func,id=None):
            self.scaduto=False
            self.id=None
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
    #--------------------------------------------------------------------------------
    def __init__(self,animato=None,parlante=True):
        self.debug=False
        self.miotimer=None
        self.segmento=0
        self.dic_storia={'messaggio':'...'}
        self.messaggio_dato=False
        self.fermato=False
        self.staifermo=False
        self.giacambiato=False
        self.orientamento="vuoto"
        self.motore=None
        self.attendi_evento=False
        self.vai_incontro=False
        self.rendez_vous_punto=(200,200)
        self.in_uscita=False
        self.finito_evento=False
        self.contatore_destinazioni=0
        self.listap=[]
        self.auto=True
        self.lanciato=False
        self.inpausa=False
        model.Object.__init__(self)
        self.miosprite=pygame.sprite.Sprite()
        dir_name=animato['dir']
        self.sottotipo=animato['sottotipo']
        
        self.miocing=Beast2(dir_name=dir_name+"/cammina/",duration=0.1)
        
        dir_name_fermo='animazioni/animation/'+dir_name+'/fermo/'
        if os.path.exists(dir_name_fermo):
            self.miocingfermo=Beast2(dir_name=dir_name+"/fermo/",duration=0.1)
            self.miocingfermo.moveConductor.play()
        
        dir_name_dying='animazioni/animation/'+dir_name+'/muore/'
        if os.path.exists(dir_name_dying):
            self.miocingdying=Beast2(dir_name=dir_name+"/muore/",duration=0.3)
            self.miocingdying.moveConductor.play()
        dir_name_attacca='animazioni/animation/'+dir_name+'/attacca/'
        if os.path.exists(dir_name_attacca):
            self.miocingattacca=Beast2(dir_name=dir_name+"/attacca/",duration=0.1)
            self.miocingattacca.moveConductor.play()
        
        
        self.id=animato['id']
        #exclpng=pygame.image.load('immagini/exclam1.png').convert_alpha()
        #self.exclamation=pygame.transform.scale(exclpng,(50,38))
        #self.exclamation=exclpng
        self.x=animato['pos'][0]+16
        self.y=animato['pos'][1]
        position=animato['pos']
        self.posizione_iniziale_animato=position
        points = animato['points']
        if points:
            self.lista_destinazioni=self.calcola_points(points,position)
            self.x=self.lista_destinazioni[0][0]
            self.y=self.lista_destinazioni[0][1]
        elif 'punto_arrivo' in animato:
            cellxy=eval("("+animato['punto_arrivo']+")")
            self.lista_destinazioni=self.calcola_points_cella(cellxy,position)
        else:
            self.lista_destinazioni=self.comp_lista_destinazioni(self.x,self.y)
            
        #self.fotogramma=self.miocing.left_standing
        self.miocing.moveConductor.play()
        self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()
        self.morto=False
        if 'durata_pausa' in animato:
            self.durata_pausa=int(animato['durata_pausa'])
        else:
            self.durata_pausa=1
        if 'attendi_evento' in animato:
            self.attendi_evento=animato['attendi_evento']
        if 'vai_incontro' in animato:
            self.vai_incontro=animato['vai_incontro']
        if parlante:self.dialogosemp=Dialogosemplice(self)
        
        
    #--------------------------------------------------------------------------------
    def calcola_points(self,points,position):
        real_points=[]
        for singlepos in points:
            newx=position[0]+singlepos[0]
            newy=position[1]+singlepos[1]
            couple=(newx,newy)
            real_points.append(couple)
        return real_points
        
    def calcola_points_cella(self,cellxy,position):
        x0=position[0]+22
        y0=position[1]+22
        real_points=[(x0,y0)]
        x=int(cellxy[0])
        y=int(cellxy[1])
        newx=x*32
        newy=y*32
        couple=(newx,newy)
        
        real_points.append(couple)
        #print self.id
        #print position
        #print couple
        #print real_points
        return real_points
    
    
    #-------------------------------------------------------------------------
    def passi(self,or_pos=(300,200),target_pos=(200,200)):
        distanza=int(geometry.distance(or_pos,target_pos))
        lista_posizioni=[]
        for progress_distance in range(1,distanza):  
                p= geometry.step_toward_point(or_pos, target_pos, progress_distance)
                lista_posizioni.append(p)
        return lista_posizioni
    
    
    #--------------------------------------------------------------------------------
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
    
    #--------------------------------------------------------------------------------
    def calcola_direzione(self,pos,mousepos):
        angolo= geometry.angle_of(pos,mousepos)
        ore=(angolo*100/360)*12
        if ore>100 and ore<200:
                direzione='NE'
        elif ore>400 and ore<500:
                direzione='SE'
        elif ore>700 and ore<800:
                direzione='SW'
        elif ore>1000 and ore<1150:
                direzione='NW'
        elif ore>1150 or ore<100:
                direzione='back'
        elif ore>500 and ore<700:
                direzione='front'
        elif ore>200 and ore<400:
                direzione='right'
        elif ore>800 and ore<1000:
                direzione='left'
        distanza=geometry.distance(pos,mousepos)
        #if  distanza>55:
            #print distanza
        return direzione
    
    #--------------------------------------------------------------------------------
    @property
    def is_walking(self):
        if len(self.listap)>0:
            return True
        else:
            return False
    
    @property
    def is_p_in_listap(self):
        return self.is_walking
        
    #--------------------------------------------------------------------------------
    @property
    def sprite_fotogramma(self):
        fotog_sprite=self.miosprite
        #if self.fotogramma is not None:
        fotog_sprite.image=self.fotogramma
        fotog_sprite.rect=self.fotogramma.get_rect()
        fotog_sprite.rect.x=self.x-fotog_sprite.rect.width/2
        fotog_sprite.rect.y=self.y-fotog_sprite.rect.height
        return fotog_sprite
    
    @property
    def sprite_fotogrammanew(self):
        #fotog_sprite=pygame.sprite.Sprite()
        #fotog_sprite=self.miosprite
        self.miosprite.image=self.fotogramma
        self.miosprite.rect=self.fotogramma.get_rect()
        self.miosprite.rect.x=self.x-self.miosprite.rect.width/2
        self.miosprite.rect.y=self.y-self.miosprite.rect.height
        self.miosprite.id=self.id
        return self.miosprite

    #--------------------------------------------------------------------------------
    @property
    def rect(self):
        rect=self.sprite_fotogramma.rect
        return rect
    #--------------------------------------------------------------------------------
    @property
    def image(self):
        image=self.fotogramma
        return image
    #--------------------------------------------------------------------------------
    @property
    def talk_box(self):
        talk_box=self.rect
        if self.rect.height<100: talk_box.height=self.rect.height+10
        else:talk_box.height=self.rect.height
        if talk_box.width<100:talk_box.width=self.rect.width+10
        else: talk_box.width=self.rect.width
        y = self.rect.y
        x= self.rect.x
        talk_box.y=y
        talk_box.x=x
        return talk_box
    #--------------------------------------------------------------------------------
    @property
    def beast_hit_box(self):
        beast_hit_box=self.rect.copy()
        beast_hit_box.height=20
        beast_hit_box.width=30
        beast_hit_box.x=beast_hit_box.x+beast_hit_box.width/2
        beast_hit_box.y=beast_hit_box.y+beast_hit_box.height
        return beast_hit_box
    
    #--------------------------------------------------------------------------------
    def mostra_esclamazione(self):
        cx,cy=self.motore.State.camera.rect.topleft
        self.motore.State.screen.blit(self.exclamation,(self.rect.x-cx+3,self.rect.y-cy-25))
    #--------------------------------------------------------------------------------
    @property
    def is_persona_collide(self):
        newsprite=self.motore.avatar.sprite
        hits=self.beast_hit_box.colliderect(newsprite.rect)
        #hits=pygame.sprite.collide_rect(newsprite, self.sprite_fotogramma)
        if hits:
            #self.mostra_esclamazione()
            #self.dialogosemp.dialogo_btn=True
            self.dialogosemp.dialogo_show=True
            self.dialogosemp.idx_mess=0
            return True
        else:
            return False

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
    def scegli_fotogramma_animazione(self,miocing,direzione):
        self.direzione=direzione
        if len(self.listap)>0:  ##inizia la camminata
            if not self.staifermo:
                #qui vengono impostati x e y del fotogramma da proiettare prendendoli dalla lista della camminata self.listap
                pos= self.listap.pop(0)
                self.x,self.y=pos #qui vengono impostati x e y del fotogramma da proiettare sullo schermo prendendoli dalla lista della camminata self.listap
                #fine impostazione ---------------------------------------------------------------------------------------------------
                """if self.vai_incontro:
                        if self.motore:
                                self.lista_destinazioni=[self.lista_destinazioni[0],(self.motore.avatar.hitbox.bottomleft[0],self.motore.avatar.hitbox.bottomleft[1])]"""
                        #endifclause
                #endifclause
            #end_if_clause
            
            #miocing.moveConductor.play()
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
        #endifclause
    
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        return True
    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------
    #EndofClass
        
        
        
        #----------------------------------------
        # metodo unico poi sostituito nelle singole sottoclassi
        #----------------------------------------
        """def muovi_animato(self):
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
                    if self.orientamento=='front':
                        direzioni=['front','SW','SE']
                    elif self.orientamento=='back':
                        direzioni=['back','NW','NE']
                    elif self.orientamento=='left':
                        direzioni=['left','NW','SW']
                    elif self.orientamento=='right':
                        direzioni=['right','NE','SE']
                        
                    else:
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

            
            #sezione che effettivamente muove l'animazione, ma solo se non è in pausa o non è fermata
            if self.is_walking and not self.fermato and not self.is_persona_collide: 
            #if self.is_walking and not self.fermato: 
                self.scegli_fotogramma_animazione(self.miocing,self.direzione)
         
            else:
                #print self.direzione
                if (self.direzione=='right') or (self.direzione=='SE') or (self.direzione=='NE'): 
                    self.fotogramma=self.miocing.animObjs['right_stand'].ritorna_fotogramma()
                elif (self.direzione=='left') or (self.direzione=='SW') or (self.direzione=='NW'): 
                    self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()
           

            if (self.lanciato==False) and (self.is_walking==False) and (self.staifermo==False):
                    self.mio_timer_pausa() #lancia il timer che conta i secondi della pausa passati come parametro a MovingBeast()
                    fotog_sprite=self.sprite_fotogramma
            
            if self.miotimer: #controlla ad ogni ciclo se è attivo un timer e se la pausa di quel timer è scaduta
                self.miotimer.check_time()
            
            #self.check_storia() #controlla ad ogni ciclo se deve mandare un messaggio
            if self.dialogosemp.finito_dialogo:
                #print self.dialogosemp.finito_dialogo
                #self.auto=False
                if not self.in_uscita:
                    print self.x,self.y
                    points=[(11,82),(11,78)]
                    self.lista_destinazioni=self.calcola_points(points,(self.x,self.y))
                    self.in_uscita=True
                    print self.lista_destinazioni
                
            return self.fotogramma"""
        #---------------------------------------------------
#fine della Classe




"""                    
def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 300))
    dir_name="aio"
    pygame.display.set_caption('Animato in movimento: '+dir_name)
    BGCOLOR = (180, 180, 180)
    mainClock = pygame.time.Clock()
    
    animato={'dir':'aio','id':'1','pos':(100,100),'points':None,'durata_pausa':'10'}
    bestia=MovingBeast(animato)
    bestia.staifermo=False
    bestia.dialogosemp.lista_messaggi=['pippo','TOPOLINO','PLUTO']
    

    #print ogg.sprite_fotogramma.rect
    while True:
        #print bestia.dialogosemp.lista_messaggi
        screen.fill(BGCOLOR)
        bestia.muovi_animato()

        screen.blit(bestia.sprite_fotogramma.image, (bestia.rect.x, bestia.rect.y))
        
        if bestia.dialogosemp.dialogo_btn: 
            type_filter=[pygame.KEYDOWN,pygame.QUIT]
        else:
            type_filter=[pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN,pygame.QUIT]
            
        for event in pygame.event.get(type_filter): # event handling loop
            # handle ending the program
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_z:
                    bestia.dialogosemp.incrementa_idx_mess()
                if event.key == K_F4:                   
                    
                    if not bestia.dialogosemp.is_near:
                        bestia.dialogosemp.is_near=True
                        bestia.dialogosemp.sequenza_messaggi_noth()
                    else:
                        bestia.dialogosemp.is_near=False
                    if not bestia.dialogosemp.dialogo_btn:
                        bestia.dialogosemp.dialogo_btn=True
                        #bestia.set_dialogo_btn(True)
                    else:
                        bestia.dialogosemp.dialogo_btn=False
                        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                bestia.dialogosemp.dialogo_btn=True
                bestia.dialogosemp.is_near=True
                #bestia.stai_fermo_fermo=True
                bestia.fermato=True
                bestia.dialogosemp.sequenza_messaggi_noth()
                #bestia.dialogosemp.suono.play()
        bestia.dialogosemp.scrivi_frase()
        pygame.display.flip()
        mainClock.tick(40) # Feel free to experiment with any FPS setting.
              
                    
if __name__ == '__main__':
    #ciclo=MovingBeast()
    main()
"""