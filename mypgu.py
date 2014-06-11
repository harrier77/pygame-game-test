import miopaths
import gummworld2
import __builtin__
__builtin__.miavar=True
__builtin__.miodebug=False
from main import myengine
import pygame
from pygame.locals import *
import miovar_dump
from miovar_dump import miovar_dump
import sys; sys.path.insert(0, "D:\\the_assassins_land_of_fire\\new-trunk\\librerie")
import gui
import os

class Quit(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Esci/Fine'
        gui.Button.__init__(self,**params)
        self.miomenu=params['miomenu']
        self.connect(gui.CLICK,self.quit)
    def quit(self):
        print 'quit'
        self.miomenu.mioloop=False

class Lancia(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Vai/Riprendi'
        gui.Button.__init__(self,**params)
        self.pgu=params['pgu']
        self.genitore=params['genitore']
        self.connect(gui.CLICK,self.go,params)
        self.inizializzato=False
    def go(self,parametri):
        if not self.inizializzato:
            oggetto=myengine.miomain(debug=False)
            self.inizializzato=True
            self.genitore.app_gioco=oggetto
        else:
            self.genitore.app_gioco.mio_riprendi()
        self.pgu.repaint()

class MioMenu():
    def __init__(self):
        x,y = 20,80
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
        
        app = gui.Desktop(width=800,height=600)
        app.connect(gui.QUIT,app.quit,None)
        tabella = gui.Table(width=600,height=400)
        
        tabella.tr()
        b=Lancia(pgu=app,genitore=self)
        tabella.td(b)
       
        tabella.tr()
        settaggi=gui.Button(value='Settaggi')
        tabella.td(settaggi)
        
        tabella.tr()
        punteggio=gui.Button(value='Punteggio')
        tabella.td(punteggio)
        
        tabella.tr()
        inventario=gui.Button(value='Inventario')
        tabella.td(inventario)
        
        tabella.tr()
        e = Quit(miomenu=self)
        tabella.td(e)

        app.init(tabella)
        self.mioloop=True
        clock = pygame.time.Clock()
        while self.mioloop:
                mousemotions = pygame.event.get(MOUSEMOTION)
                if mousemotions: #checks if the list is nonempty
                        mousemotion = mousemotions[-1]
                coda_eventi=pygame.event.get()
                for event in coda_eventi:
                        if event.type == pygame.QUIT:
                                self.mioloop = False
                        elif event.type == pygame.USEREVENT:
                                continue
                        elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                        self.mioloop = False
                        app.event(event)
                        app.loop()
                        clock.tick(60)

o=MioMenu()