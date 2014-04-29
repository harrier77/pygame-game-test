import pygame
import threading
from threading import Thread
import paths
import gummworld2
from gummworld2 import data,context

#--------------------------------------------------------
class MessageTimerClass(threading.Thread):
    def __init__(self,messaggi,ogg_genitore):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.messaggi=messaggi
        self.ogg_genitore=ogg_genitore
        self.is_open=self.ogg_genitore.open
    
    def set_open(self,var):
        self.is_open=var
    
    def run(self):
        for value in self.messaggi:
            if self.is_open:
                self.ogg_genitore.suono.play()
                self.ogg_genitore.testo=value
                self.event.wait(2)
        self.ogg_genitore.testo='...'
        self.ogg_genitore.sequenza_finita=True
        self.stop()
        #print "running"

        
    def stop(self):
        self.event.set()
        
#-----------------------------------------------------------

class Dialogosemplice():
    open=False
    testo="Hello!"
    close_clicked=False
    beeped=False
    scritto=False
    sequenza_partita=False
    sequenza_finita=True
    lista_messaggi=['...']

    def __init__(self):
        self.text_altezza=50
        self.crossrect=None
        self.screen=pygame.display.get_surface()
        self.background_txt = pygame.Surface((self.screen.get_size()[0]-1,self.text_altezza))
        self.background_txt.fill((250, 250, 250))
        self.bgrect=self.background_txt.get_rect()
        self.bgrect.top=self.screen.get_size()[1]-self.text_altezza
        self.cross=pygame.image.load('.\\immagini\\cross.gif')
        self.font=pygame.font.Font(data.filepath('font', 'Vera.ttf'), 18)
        self.crossrect=self.cross.get_rect()
        self.crossrect.x=self.bgrect.topright[0]-15
        self.crossrect.y=self.bgrect.y
        self.crossrect.width=self.crossrect.width
        self.crossrect.height=self.crossrect.height
        pygame.mixer.init()
        self.suono=pygame.mixer.Sound('immagini/message.wav')
        self.seq=MessageTimerClass(['...'],self)

    def mywrite(self):
        self.background_txt.fill((250, 250, 250))
        #font = pygame.font.Font(None, 32)
        text = self.font.render(self.testo, True, (10, 10, 10),(255,255,255))
        self.background_txt.blit(text,(10,10))
        self.background_txt.blit(self.cross,(self.crossrect.x,0))
        self.screen.blit(self.background_txt,(self.bgrect.x,self.bgrect.y))
        self.scritto=True
        
        #event=pygame.event.wait()
        #self.gestione_eventi(event)
        type_filter=pygame.MOUSEBUTTONDOWN
        for event in pygame.event.get(type_filter): # event handling loop
            self.gestione_eventi(event)
    
    #-----------------------------------------------------
    
    def scrivi_frase(self):	
        if self.open:
            #self.mybeep()
            self.mywrite()
        else:
            #self.beeped=False
            self.scritto=False
    
    #-----------------------------------------------------
    """def sequenza_messaggi(self,beast):
        if not self.sequenza_partita:
            #self.testo=beast.dic_storia['messaggio'][0]
            self.seq=MessageTimerClass(beast.dic_storia['messaggio'],self)
            self.seq.daemon=True
            self.seq.start()
            self.sequenza_partita=True
            self.sequenza_finita=False
        if self.sequenza_finita:
            self.sequenza_partita=False"""
    
     #-----------------------------------------------------
    def sequenza_messaggi_new(self):
        if not self.sequenza_partita:
            #self.testo=beast.dic_storia['messaggio'][0]
            self.seq=MessageTimerClass(self.lista_messaggi,self)
            self.seq.daemon=True
            self.seq.start()
            self.sequenza_partita=True
            self.sequenza_finita=False
        if self.sequenza_finita:
            self.sequenza_partita=False

    #---------------------------------------------------------
    def gestione_eventi(self,event):
        #event=pygame.event.peek()
        #event=pygame.event.wait()
        if event.type == pygame.QUIT:
            context.pop()
        if event.type==pygame.MOUSEBUTTONDOWN:
            pos=pygame.mouse.get_pos()
            if self.crossrect.collidepoint(pos):
                self.close_clicked=True
                self.open=False
