import pygame



from pygame.locals import*
from sys import exit

from miefunzioni import html
from miefunzioni import gui
import os
from giocatore_animato import *
import scroll
position = 1, 1
os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])



class miopgumenu():
        def cliccato(self,param):
                if param=="esci":
                        self.mioloop=False
                elif param=="apri":
                        self.open_file_browser(None)
                elif param=="uno":
                        self.scrivi_html("episod1.html")
		elif param=="due":
                        self.scrivi_html("episod2.html")
		elif param=="anteprima":
			scroll.main()
        
        def open_file_browser(self,arg):
                self.schermata=self.screen.copy()
                self.d.open()

        def handle_file_browser_closed(self,dlg):
                if dlg.value: 
                        self.screen.blit(self.schermata, (0,0))
                        miog=giocatore_animato()


                        miog.vedi_collisioni=False
                        miog.file_mappa=dlg.value
                        miog.main()
                        
        def scrivi_html(self,file):
                font = pygame.font.SysFont("Verdana", 28)
                with open ("storia/"+file, "r") as myfile:
                    data_html=myfile.read().replace('\n', '')
                self.doc = html.HTML(data=data_html,width=500,font=font,globals={'menuchiamante':self})
                self.contenitore.remove(self.voci_menu_contenitore)
                self.contenitore.add(self.doc,120,150)
                self.app.paint()


        def ripristina_menu(self):
                self.contenitore.remove(self.doc)
                self.contenitore.add(self.voci_menu_contenitore,0,0)
                self.mostra_menu=True
                self.screen.blit(self.schermata_vuota, (0,0))
        
        def mio_close(self):
                print "chiuso"
                self.ripristina_menu()

                
        def mio_open_mappa(self,filemappa='001-1.tmx',playerpos=(10,10)):
                self.ripristina_menu()
                miog=giocatore_animato()
                miog.file_mappa="..\\tmwa\\maps\\"+filemappa
		miog.playerpos=playerpos
                miog.cam_world_pos_x=playerpos[0]
                miog.cam_world_pos_y=playerpos[1]
		
                miog.main()

        def aggiungi_voci_menu(self):
                self.voci_menu_contenitore = gui.Container(align=-1,valign=-1)
                
                link2 = gui.Link("Episodio I: una visita")
                link2.connect(gui.CLICK,self.cliccato,'uno')
                self.voci_menu_contenitore.add(link2,120,150)
                
                link3 = gui.Link("Episodio II: la foresta")
                link3.connect(gui.CLICK,self.cliccato,'due')
                self.voci_menu_contenitore.add(link3,120,200)
                
                link4 = gui.Link("Episodio III: l'ignoto")
                link4.connect(gui.CLICK,self.cliccato,None)
                self.voci_menu_contenitore.add(link4,120,250)
                
                link5 = gui.Link("Episodio IV: ...")
                link5.connect(gui.CLICK,self.cliccato,None)
                self.voci_menu_contenitore.add(link5,120,300)
                
                
                link1 = gui.Link("Apri file")
                link1.connect(gui.CLICK,self.cliccato,"apri")
                self.voci_menu_contenitore.add(link1,120,350)
		
		link7 = gui.Link("Anteprima mappe")
                link7.connect(gui.CLICK,self.cliccato,"anteprima")
                self.voci_menu_contenitore.add(link7,120,400)
                
                link6 = gui.Link("Esci")
                link6.connect(gui.CLICK,self.cliccato,"esci")
                self.voci_menu_contenitore.add(link6,120,450)
                
                self.contenitore.add(self.voci_menu_contenitore,0,0)
        

        def main(self):
                imm_sfondo = "immagini/pergamena.jpg"
                imm_sfondo2 = "immagini/pergamena3.jpg"
                pygame.init()
                giallo=255,255,128
                video=pygame.display.Info()
                screen_width= video.current_w-2
                screen_height= video.current_h-2
                self.screen = pygame.display.set_mode((screen_width,screen_height))
                background = pygame.Surface(self.screen.get_size())
                background = background.convert()
                background.fill((giallo))
                
                sfondo1 = pygame.image.load(imm_sfondo).convert()
                sfondo1_ridotto =pygame.transform.scale(sfondo1,(650,768)) 
                sfondo2 = pygame.image.load(imm_sfondo2).convert()
                sfondo2_ridotto=pygame.transform.scale(sfondo2,(650,768))
                size = width, height = 500,300
                self.screen.blit(background, (0,0))
                self.screen.blit(sfondo1_ridotto,(0,0))
                self.screen.blit(sfondo2_ridotto,(650,0))
                pygame.display.flip()
                self.schermata_vuota=self.screen.copy()

                app = gui.App()
                self.app=app

                self.contenitore = gui.Container(align=-1,valign=-1)
                self.aggiungi_voci_menu()

                app.init(self.contenitore)
                
                self.d = gui.FileDialog(path="D:\\games\\tmwa\\maps")
                self.d.connect(gui.CHANGE, self.handle_file_browser_closed, self.d)
                self.d.mioclosed=False

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
                                self.screen.blit(self.schermata_vuota, (0,0))
                                app.paint()
                                
                                pygame.display.flip()
                                clock.tick(60)


if __name__ == '__main__':
        oggetto=miopgumenu()
        
        oggetto.main()
        