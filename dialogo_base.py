# coding: utf-8                     
# Questa èl a classe per un dialogo base, 
#
#----------------------------------------------------------

from mappa_base import *
from miefunzioni import gui

class mio_dialogo():
	def __init__(self,rect=pygame.Rect(20,20,200,200)):
		title = gui.Label("Settaggi")
		doc = gui.Document(width=rect.width,height=rect.height)
		self.dialog=gui.Dialog(title,doc)
		self.app = gui.App()
		self.app.init(doc)
		self.app.rect= rect


def main():
	pygame.init()
	oggetto = mappa_base()
	oggetto.file_mappa="..\\tmwa\\maps\\004-2.tmx"
	world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(oggetto.file_mappa)
	oggetto.screen=oggetto.cambia_pieno_schermo('0')
	oggetto.clock = pygame.time.Clock()
	oggetto.carica_mattonelle_in_layers(world_map)
	mio_dialogo_ogg=mio_dialogo()

	while oggetto.running_loop:
		oggetto.screen.fill(0)
		oggetto.render_the_map()
		oggetto.gestione_eventi()
		for event in oggetto.coda_eventi:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					oggetto.running_loop = False
				elif event.key == pygame.K_F4:
					mio_dialogo_ogg.dialog.open()
			mio_dialogo_ogg.app.event(event)
		mio_dialogo_ogg.app.paint()
		pygame.display.flip()


if __name__ == '__main__':
	main()