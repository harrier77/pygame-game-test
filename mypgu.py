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
from miovar_dump import *

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

class Settaggi(gui.Button):
    def __init__(self,genitore):
        gui.Button.__init__(self,value='Settaggi')
        self.genitore=genitore
        self.connect(gui.CLICK,self.go)
    def go(self):
        foo = WritableObject()   # a writable object
        original = sys.stdout
        sys.stdout = foo           # redirection
        #miovar_dump(self.genitore.app_gioco)
        sys.stdout=original
        tabella = gui.Table(width=600,height=400)
        tabella.tr()
        b=gui.Button(value='Prova')
        tabella.td(b)
        tabella.tr()
        miodoc=gui.Document()
        #miodoc.add(' '.join(foo.content))
        #miodoc.block(align=0)
        title = gui.Label("About Cuzco's Paint")
        space = title.style.font.size(" ")
        #for word in (' '.join(foo.content).split(" ")):
        for word in ("Pippo Topolino Pluto Pippo \n Topolino Pluto Pippo Topolino Pluto Pippo Topolino Pluto Pippo Topolino Pluto Pippo Topolino Pluto Pippo Topolino Pluto".split(" ")):
            if word=='\n':
                miodoc.br(space[1])
            else:
                miodoc.add(gui.Label(word))
                miodoc.space(space)
        
        
        tabella.td(miodoc)
        #print foo.content
        self.genitore.app.init(tabella)
        

class MioMenu():
    def __init__(self):
        x,y = 20,80
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

        self.app = gui.Desktop(width=800,height=600)
        self.app.connect(gui.QUIT,self.app.quit,None)
        tabella = gui.Table(width=600,height=400)
        
        tabella.tr()
        b=Lancia(pgu=self.app,genitore=self)
        tabella.td(b)
       
        tabella.tr()
        #settaggi=gui.Button(value='Settaggi')
        settaggi=Settaggi(self)
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

        self.app.init(tabella)
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
                        self.app.event(event)
                        self.app.loop()
                        clock.tick(60)

o=MioMenu()