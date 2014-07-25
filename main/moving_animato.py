# coding: utf-8
from moving_beast import calcola_passi,MovingBeast,Dialogosemplice,StateToEvent
import datetime
from random import randint
import pygame
from pygame.locals import *
from gummworld2 import geometry,model,data
import copy

#from miovardump import miovar_dump
    
    
#---------------------------------------
#Animazione di unità che non parla e non affronta il personaggio avatar
#limitandosi a camminare avanti e indietro secondo il percorso della proprietà points
#della retta con una pausa indicata in durata_pausa
#Se c'è l'animazione, se colpito cade e muore restando sul terreno.
#----------------------------------------         
class AnimatoSemplice(MovingBeast):
    def __init__(self,animato):
        MovingBeast.__init__(self,animato,parlante=False)
        self.dialogosemp=type('obj', (object,), {'dialogo_show' : False}) # qui la proprietà dialogo_show viene settata a False
        #self.linearossa=pygame.image.load('immagini/linearossa.png').convert()
        
        self.salute=3
        self.sotto_tiro=False
    #----------------------------------------
    @property
    def draw_fotogramma(self):
        self.disegna_linea_salute()
        return True
    #----------------------------------------

    @property
    def corpo_a_corpo(self):
        hits= pygame.sprite.spritecollide(self.motore.avatar.sprite,self.motore.beast_sprite_group, False)
        if hits:
            ogg_colpito=self.motore.lista_beast[hits[0].id]
            print ogg_colpito.id
            return True
        else:
            return False
    #----------------------------------------
    def evento_colpito(self):
        if 'arco' in self.motore.mag.selezionabili:
            if self.motore.mag.selezionabili['arco']==True:
                if not self.corpo_a_corpo:
                    self.fallo_morire()
        if 'spada' in self.motore.mag.selezionabili:
            if self.motore.mag.selezionabili['spada']==True:
                self.fallo_morire()
    #-------------------------------------------------------------------------
    def fallo_morire(self):
        if hasattr(self, 'miocingdying'):
            self.sotto_tiro=True
            self.motore.suono_colpito.play()
            if self.salute>0:
                    self.salute=self.salute-1
                    if self.salute<1:
                        self.miocingdying.moveConductor.mio_set_loop()
                        self.miocing=self.miocingdying
                        self.staifermo=True
                        self.morto=True
        else:
            self.motore.suono_noncolpito.play()
    #-------------------------------------------------------------------------
    def disegna_linea_salute(self):
        if hasattr(self, 'miocingdying'):
            if self.salute>0 and self.sotto_tiro:
                basicfont = pygame.font.SysFont(None, 16)
                text = basicfont.render(str(self.salute), True, (0, 255, 0))
                lung=self.salute*20
                cx,cy=self.motore.State.camera.rect.topleft
                self.motore.State.screen.blit(text,(self.rect.x-cx,self.rect.y-cy-10))
                pygame.draw.line(self.motore.State.screen.surface,(0,255,0),(self.rect.x-cx,self.rect.y-cy),(self.rect.x-cx+lung,self.rect.y-cy))
    #----------------------------------------
    def muovi_animato(self):
        if self.auto: ##verifica se deve procedere a calcolare una nuova sequenza di passi
            if self.contatore_destinazioni>len(self.lista_destinazioni)-1: 
                    self.contatore_destinazioni=0 #resetta il contatore della lista delle destinazioni automatiche
                    self.segmento=0
            if (self.x,self.y)==self.lista_destinazioni[self.contatore_destinazioni]:
                    #print "destinazione uguale a partenza"
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
        elif self.is_persona_collide and not self.morto:
            self.scegli_fotogramma_animazione(self.miocing,self.direzione)
        else:
            if not self.morto:
                if (self.direzione=='right') or (self.direzione=='SE') or (self.direzione=='NE'): 
                    self.fotogramma=self.miocing.animObjs['right_stand'].ritorna_fotogramma()
                elif (self.direzione=='left') or (self.direzione=='SW') or (self.direzione=='NW'): 
                    self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()
            else: self.scegli_fotogramma_animazione(self.miocing,self.direzione)
            
        if (self.lanciato==False) and (self.is_walking==False) and (self.staifermo==False):
                self.mio_timer_pausa() #lancia il timer che conta i secondi della pausa passati come parametro a MovingBeast()
                fotog_sprite=self.sprite_fotogrammanew
        if self.miotimer: #controlla ad ogni ciclo se è attivo un timer e se la pausa di quel timer è scaduta
            self.miotimer.check_time()
     
        return self.fotogramma
#---------------------------------------------------
#fine della Classe

#-------------------------------------------------------
#Animazione di unità che cammina per i fatti suoi
#ma se colpita col lasso cambia tipo e segue il catturatore
#-------------------------------------------------------                 
class AnimatoCambiaTipo(AnimatoSemplice):
    #----------------------------------------------------
    def __init__(self,animato):
        self.oldanimato=animato
        AnimatoSemplice.__init__(self,animato)
    #---------------------------------------------------
    def evento_colpito(self):
        if 'lasso' in self.motore.mag.selezionabili:
            if self.motore.mag.selezionabili['lasso']:
                self.cambialo()
    #----------------------------------------------------
    def cambialo(self):
        #print "cambialo"
        self.motore.avatar_group.objects.remove(self)
        self.motore.beast_sprite_group.remove(self.sprite_fotogrammanew)
        newbeast=AnimatoMandria(self.oldanimato,motore=self.motore)
        newbeast.x=self.x
        newbeast.y=self.y
        newbeast.segui=True
        self.motore.mag.suono.play()
        newbeast.motore=self.motore
        newbeast.aggiorna_pos_da_seguire()
        self.motore.lista_beast[self.id]=newbeast
        self.motore.avatar_group.add(newbeast)
        dict_prop={'nome':self.id}
        self.motore.mag.seguito.append((dict_prop,self.sprite_fotogrammanew))
#------------------------------------------------------------
#fine della Classe

#---------------------------------------
#Animazione di unità che affronta il personaggio avatar
#iniziando a parlare, viene attivata da un evento AttivaAnimato sulla mappa
#----------------------------------------              
class AnimatoParlanteAvvicina(MovingBeast):
    #----------------------------------------
    def __init__(self,animato):
        MovingBeast.__init__(self,animato,parlante=False)
        self.dialogosemp=Dialogosemplice(self)
        self.in_uscita=False
        self.cliccato=False
    #----------------------------------------
    @property
    def draw_fotogramma(self):
        if self.attendi_evento or self.finito_evento:
            return False
        else:
            return True
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        hits=self.motore.avatar.rect.colliderect(self.talk_box)  
        if self.dialogosemp.dialogo_show:
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
                #self.dialogosemp.dialogo_btn=False
                self.dialogosemp.dialogo_show=False
                self.dialogosemp.open=False
                self.dialogosemp.idx_mess=0
                self.fermato=False
    #-------------------------------------------------------------------------
    def aggiorna_pos_da_seguire(self):
        pos_partenza=self.lista_destinazioni[0]
        pos_arrivo_x=self.motore.avatar.hitbox.bottomleft[0]
        pos_arrivo_y=self.motore.avatar.hitbox.bottomleft[1]
        self.lista_destinazioni=[pos_partenza,(pos_arrivo_x,pos_arrivo_y)]
    #----------------------------------------
    def muovi_animato(self):
        self.aggiorna_pos_da_seguire()
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
            #print self.lista_destinazioni[self.contatore_destinazioni]
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


#---------------------------------------
#Animazione di unità che segue il personaggio avatar
# se si avvicina per prenderla o se la cattura con il lasso
#----------------------------------------              
class AnimatoSegue(MovingBeast):
    #----------------------------------------
    def __init__(self,animato,motore=None,segui=False):
        MovingBeast.__init__(self,animato,parlante=False)
        self.ultimo=motore.mag.seguito.ultimo
        self.dialogosemp=Dialogosemplice(self)
        self.in_uscita=False
        self.cliccato=False
        self.draw_fotogramma=True
        self.direzione="right"
        self.segui=segui
    
    #----------------------------------------
    @property
    def suonato(self):
        if self.segui:
            return True
        else:
            return False
    #----------------------------------------
    def aggiorna_pos_da_seguire(self):
        #self.posarrivo_rect=self.motore.avatar.hitbox
        pos_partenza=self.x,self.y
        incx=incy=0
        if self.motore.direzione_avatar=='front':
            incx=incy=-20
        elif self.motore.direzione_avatar=='back':
            incx=+16
            incy=+42
        elif self.motore.direzione_avatar=='left':
            incx=+16
            incy=+42
        elif self.motore.direzione_avatar=='right':
            incx=-32
            incy=+42
        pos_arrivo_x=self.posarrivo_rect.bottomleft[0]+incx
        pos_arrivo_y=self.posarrivo_rect.bottomleft[1]+incy
        pos_da_raggiungere=pos_arrivo_x,pos_arrivo_y
        self.lista_destinazioni=[pos_partenza,pos_da_raggiungere]
        self.listap=self.passi(pos_partenza,pos_da_raggiungere)  #qui viene compilata la lista dei passi da seguire per camminare nel percorso
        self.direzione=self.calcola_direzione(pos_partenza,pos_da_raggiungere) #calcola la direzione della destinazione da raggiungere

    #----------------------------------------
    def controlla_se_preso(self):
        if not self.suonato:
            hits=self.rect.colliderect(self.motore.avatar.hitbox)
            if hits:
                self.motore.mag.suono.play()
                self.segui=True
                dict_prop={'nome':self.id}
                self.motore.mag.seguito.append((dict_prop,self.sprite_fotogrammanew))

    #----------------------------------------
    @property
    def posarrivo_rect(self):
        p=self.motore.mag.seguito.get(self.ultimo)
        if p is not None:
            id_p=p[0]['nome']
            if p[0]['nome']!=self.id:
                return self.motore.lista_beast[id_p].rect
        return self.motore.avatar.hitbox
        
        
     #--------------------------------------------------------------------------------
    def scegli_fotogramma_animazione(self,miocing,direzione):
        self.direzione=direzione
        if self.listap:  ##inizia la camminata
            if not self.staifermo:
                #qui vengono impostati x e y del fotogramma da proiettare prendendoli dalla lista della camminata self.listap
                if self.listap:
                    pos= self.listap.pop(0)
                    self.x,self.y=pos #qui vengono impostati x e y del fotogramma da proiettare sullo schermo prendendoli dalla lista della camminata self.listap
                    #fine impostazione ---------------------------------------------------------------------------------------------------
                    """if self.vai_incontro:
                        if self.motore:
                                self.lista_destinazioni=[self.lista_destinazioni[0],(self.motore.avatar.hitbox.bottomleft[0],self.motore.avatar.hitbox.bottomleft[1])]"""
                        #endifclause
                    #endifclause
            #end_if_clause
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
            
    #----------------------------------------
    def muovi_animato(self):
        self.controlla_se_preso()
        if self.segui : self.aggiorna_pos_da_seguire()
        #sezione che effettivamente muove l'animazione, ma solo se la lista delle posizioni da seguire non è vuota
        #print self.collisione_con_altri
        #print self.motore.beast_sprite_group
        if self.is_p_in_listap: 
            self.scegli_fotogramma_animazione(self.miocing,self.direzione)
        else:
            if (self.direzione=='right') or (self.direzione=='SE') or (self.direzione=='NE'): 
                self.fotogramma=self.miocing.animObjs['right_stand'].ritorna_fotogramma()
            elif (self.direzione=='left') or (self.direzione=='SW') or (self.direzione=='NW'): 
                self.fotogramma=self.miocing.animObjs['left_stand'].ritorna_fotogramma()
        
        return self.fotogramma
    #----------------------------------------
#EofClass---------------------------------------------------


#---------------------------------------
# Animazione di unità che segue il personaggio avatar
# ma solo se presa al lasso non se si avvicina, (in modo da poterla sganciare facilmente)
#----------------------------------------              
class AnimatoMandria(AnimatoSegue):
    #----------------------------------------
    def __init__(self,animato,motore=None,segui=False):
        AnimatoSegue.__init__(self,animato,motore=motore)
        self.motore=motore
        self.motore.beast_sprite_group.add(self.sprite_fotogrammanew) #si deve riaggniungere il nuovo sprite

    #----------------------------------------
    def evento_colpito(self):
        print self.motore.mag.seguito.ultimo
        if not self.segui:
            if 'lasso' in self.motore.mag.selezionabili:
                if self.motore.mag.selezionabili['lasso']:
                    self.motore.mag.suono.play()
                    self.segui=True
                    dict_prop={'nome':self.id}
                    self.motore.mag.seguito.append((dict_prop,self.sprite_fotogrammanew))
    #----------------------------------------
    #----------------------------------------
    def controlla_se_preso(self):
        pass
    
    
#EofClass---------------------------------------------------


#---------------------------------------
#Animazione di unità che attacca il personaggio se attaccata
#----------------------------------------              
class AnimatoAttacca(AnimatoSemplice):
    #----------------------------------------
    def __init__(self,animato):
        #MovingBeast.__init__(self,animato,parlante=False)
        AnimatoSemplice.__init__(self,animato)
        self.dialogosemp=Dialogosemplice(self)
        #self.draw_fotogramma=True
        self.vaiattacca=False
        self.miocingcammina=copy.copy(self.miocing)
        self.direzione='left'
        #self.miocing=self.miocingfermo
    #----------------------------------------
    @property
    def is_collide_avatar(self):
        hits=self.rect.colliderect(self.motore.avatar.hitbox)
        if hits:
            return True
        else:
            return False
    #--------------------------------------------------------------------------------
    def scegli_fotogramma_con_fermo_animato(self,miocing,direzione):
        self.direzione=direzione
        self.miocing=self.miocingfermo
        if self.vaiattacca and self.salute>0:
            self.miocing=self.miocingattacca

        if len(self.listap)>0:  ##inizia la camminata
            if not self.staifermo:
                #qui vengono impostati x e y del fotogramma da proiettare prendendoli dalla lista della camminata self.listap
                pos= self.listap.pop(0)
                self.x,self.y=pos #qui vengono impostati x e y del fotogramma da proiettare sullo schermo prendendoli dalla lista della camminata self.listap
            #di seguito viene selezionata l'iimmagine a seconda della direzione della camminata; x e y sono già stati impostati
            
            if self.salute<1:
                self.miocingdying.moveConductor.mio_set_loop()
                self.miocing=self.miocingdying
            else:
                self.miocing=self.miocingcammina

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
    
    #-------------------------------------------------------------------------
    def riduci_lista(self,lista):
        newlista=lista[1::2] 
        return newlista
    #-------------------------------------------------------------------------
    def passi(self,or_pos=(300,200),target_pos=(200,200)):
        distanza=int(geometry.distance(or_pos,target_pos))
        lista_posizioni=[]
        for progress_distance in range(1,distanza,1):  
                p= geometry.step_toward_point(or_pos, target_pos, progress_distance)
                lista_posizioni.append(p)
        return self.riduci_lista(lista_posizioni)
    
    #-------------------------------------------------------------------------
    def aggiorna_pos_da_seguire(self):
        pos_partenza=self.x,self.y
        incx=28
        incy=20
        segnox=segnoy=1
        if self.motore.direzione_avatar=='front':
            segnox=0
            segnoy=1
        elif self.motore.direzione_avatar=='back':
            segnox=0
            segnoy=2
        elif self.motore.direzione_avatar=='left':
            segnox=1
            segnoy=1
        elif self.motore.direzione_avatar=='right':
            segnox=-1
            segnoy=1  
        pos_arrivo_x=self.motore.avatar.hitbox.bottomleft[0]+incx*segnox
        pos_arrivo_y=self.motore.avatar.hitbox.bottomleft[1]+incy*segnoy
        pos_da_raggiungere=pos_arrivo_x,pos_arrivo_y
        self.lista_destinazioni=[pos_partenza,pos_da_raggiungere]
        self.listap=self.passi(pos_partenza,pos_da_raggiungere)  #qui viene compilata la lista dei passi da seguire per camminare nel percorso
        if not self.is_collide_avatar and not self.morto:
            self.direzione=self.calcola_direzione(pos_partenza,pos_da_raggiungere) #calcola la direzione della destinazione da raggiungere
    #----------------------------------------
    def muovi_animato(self):
        if self.vaiattacca:
            self.aggiorna_pos_da_seguire()
        #self.miocing.moveConductor.play()
        if self.morto:
            self.miocing=self.miocingdying
        self.scegli_fotogramma_con_fermo_animato(self.miocing,self.direzione)
        return self.fotogramma
#EofClass---------------------------------------------------

#Inizio Classe               
class AnimatoParlanteFermo(MovingBeast):
    #----------------------------------------
    def __init__(self,animato):
        MovingBeast.__init__(self,animato,parlante=False)
        self.dialogosemp=Dialogosemplice(self)
        self.dialogosemp.idx_mess=-1
        self.dialogosemp.conta_click=-1
        self.direzione='SW'
        self.collisione=False
    #----------------------------------------
    @property
    def draw_fotogramma(self):
        return True
    #-------------------------------------------------------------------------
    @property
    def is_persona_collide(self):
        #self.dialogosemp.dialogo_show=True
        if self.collisione:
            #print self.dialogosemp.idx_mess
            e=self.motore.State.mioevento
            if e:
                if e.type==pygame.MOUSEBUTTONDOWN and e.button == 3:
                    self.dialogosemp.dialogo_show=True
        #self.dialogosemp.finito_dialogo=False
        newsprite=self.motore.avatar.sprite
        hits=self.beast_hit_box.colliderect(newsprite.rect)
        if hits:
            return True
        else:
            return False
    #-------------------------------------------------------------------------
    def fallo_parlare(self):
        hits=self.motore.avatar.rect.colliderect(self.talk_box)
        if hits:
            self.collisione=True
            #max_idx=len(self.dialogosemp.lista_messaggi)
            #if self.dialogosemp.conta_click>=max_idx:
                #self.dialogosemp.finito_dialogo=True
        if self.dialogosemp.dialogo_show:
            if hits:
                self.dialogosemp.is_near=True
                self.fermato=True
                if hasattr(self.dialogosemp,'sequenza_messaggi_noth'):
                    self.dialogosemp.sequenza_messaggi_noth()
            else:
                self.dialogosemp.is_near=False
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
#EofClass---------------------------------------------------

#---------------------------------------------------
#Inizio Classe            come AnimatoParlanteFermo solo che non parla
class AnimatoFermo(AnimatoParlanteFermo):
    #----------------------------------------
    def __init__(self,animato):
        AnimatoParlanteFermo.__init__(self,animato)
        self.miocing=self.miocingfermo

    #-------------------------------------------------------------------------
    def muovi_animato(self):
        #sezione che effettivamente muove l'animazione, ma solo se non èin pausa o non è fermata
        self.scegli_fotogramma_animazione(self.miocing,self.direzione)
        return True
#EofClass---------------------------------------------------


    
    