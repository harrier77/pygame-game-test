import sys
sys.path.insert(0, '..')


import pygame
from pygame.locals import *
from miefunzioni import gui
from class_menu import *


class mio_file_dialog(mio_menu):
	def __init__(self):
		mio_menu.__init__(self)
		print "Inzializzazione oggetto file_dialog..."
		pygame.init()
		self.screen=self.cambia_pieno_schermo('0')
		pygame.mouse.set_cursor(*pygame.cursors.tri_left)
		font = pygame.font.SysFont("Comic Sans MS", 18)
		self.metti_sfondi()	



def open_file_browser(arg):
    d = gui.FileDialog()
    d.connect(gui.CHANGE, handle_file_browser_closed, d)
    d.open()
    

def handle_file_browser_closed(dlg):
    if dlg.value: input_file.value = dlg.value


#oggetto=mio_file_dialog()

#gui.theme.load('../data/themes/default')
app = gui.App()

app.connect(gui.QUIT,app.quit,None)

main = gui.Container(width=500, height=400) #, background=(220, 220, 220) )


main.add(gui.Label("File Dialog Example", cls="h1"), 20, 20)


td_style = {'padding_right': 10}
t = gui.Table()
t.tr()
t.td( gui.Label('File Name:') , style=td_style )
input_file = gui.Input()
t.td( input_file, style=td_style )
b = gui.Button("Browse...")
t.td( b, style=td_style )
b.connect(gui.CLICK, open_file_browser, None)


main.add(t, 20, 100)


"""
app.init(main)
while not app._quit:
	app.loop()
"""

app.init(main)
while not app._quit:
    app.loop()
    for e in pygame.event.get():
	#if e.type is QUIT: 
	#    app._quit = True
	if e.type is KEYDOWN and e.key == K_ESCAPE: 
	    done = True
	else:
	    app.event(e)
	app.screen.fill((0,0,0))    
	app.paint()
	pygame.time.wait(100)



