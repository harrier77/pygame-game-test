# coding: utf-8                     
# Questa èl a classe per un dialogo base, 
#
#----------------------------------------------------------
import pygame
from miefunzioni import gui
from miefunzioni import miovar_dump


class vuota():
        def esci(self):
                exit()


class Mio_dialogo():
        def __init__(self,rect=pygame.Rect(20,20,600,30),oggetto_chiamante=vuota(),screen=None):
                self.screen=screen
                self.oggetto_chiamante=oggetto_chiamante
                title = gui.Label(" ")
                c=gui.Table(width=rect.width,height=rect.height)
                tabella = gui.Table(width=rect.width,height=rect.height)
                self.dialog=gui.Dialog(title,tabella)
                
                tabella.tr()
                b1=gui.Button("Menu")
                b1.connect(gui.CLICK,self.esci,None)
                tabella.td(b1)
                
                b2=gui.Button("Cruscotto")
                b2.connect(gui.CLICK,self.toggle_cruscotto)
                tabella.td(b2)
                
                b3=gui.Button("Nascondi collisioni si/no")
                b3.connect(gui.CLICK,self.nascondi_collisioni)
                tabella.td(b3)
                
                b4=gui.Button("Collisioni si/no")
                b4.connect(gui.CLICK,self.ignora_collisioni)
                tabella.td(b4)
                
                b5=gui.Button("Aiuto")
                tabella.td(b5)
                
                b5=gui.Button("Esci")
                b5.connect(gui.CLICK,self.esci,None)
                tabella.td(b5)
                self.app = gui.App()
                self.app.init(c)
                self.app.rect= rect
                #self.running_loop=True
                
        def my_close(self):
                self.aperto=False
                self.dialog.close()
                
        def esci(self,param):
                if hasattr(self.oggetto_chiamante,"esci"):
                        self.oggetto_chiamante.esci()
                if hasattr(self.oggetto_chiamante,"running_loop"):
                        self.oggetto_chiamante.running_loop=False

        def toggle_cruscotto(self):
                print "cruscotto"
                if hasattr(self.oggetto_chiamante,"is_cruscotto"):
                        if not self.oggetto_chiamante.is_cruscotto:
                                self.oggetto_chiamante.is_cruscotto=True
                        else:
                                self.oggetto_chiamante.is_cruscotto=False
                self.my_close()

        def nascondi_collisioni(self):
                if (self.oggetto_chiamante.map.get_layer_by_name('Collision').visible==True):
                        #self.oggetto_chiamante.sprite_layers[self.oggetto_chiamante.idx_coll_layer].visible=False
                        print self.oggetto_chiamante.idx_collisioni
                        self.oggetto_chiamante.map.layers[self.oggetto_chiamante.idx_collisioni].visible=False
                else:
                        self.oggetto_chiamante.map.get_layer_by_name('Collision').visible==True
                self.my_close()
                        
        def ignora_collisioni(self):
                if self.oggetto_chiamante.ignora_collisioni:
                        self.oggetto_chiamante.ignora_collisioni=False
                else:
                        self.oggetto_chiamante.ignora_collisioni=True
                self.my_close()
        
        def main(self,open=False):
                self.aperto=open
                running_loop=True
                while running_loop:
                        self.screen.fill(0)
                        #dialogo_o.gestione_eventi()
                        self.coda_eventi=pygame.event.get()
                        
                        for event in self.coda_eventi:
                                
                                if event.type == pygame.QUIT:
                                        running_loop = False
                                elif event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_ESCAPE:
                                                running_loop = False
                                        elif (event.key == pygame.K_F4):
                                                self.dialog.open()
                                #print event
                                if self.aperto:
                                        self.dialog.open()
                                        self.aperto=False
                                self.app.event(event)
                        self.app.paint()
                        pygame.display.flip()
       

#---------------------------------------

if __name__ == '__main__':
        #main()
        pygame.init()
        newscreen = pygame.display.set_mode((800, 600))
        miodialogo=Mio_dialogo(screen=newscreen)
        miodialogo.main(open=True)