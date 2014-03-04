# coding: utf-8                     
# Questa è la classe mappa base basata su schermo base, 
# viene caricata la mappe e gestiti gli eventi di movimento
# e le funzioni che gestiscono il lancio di proiettili da un punto.
# Per usare i proiettili nella mappa serve usare uno sprite
#----------------------------------------------------------

from schermo_base import *

import winsound
from miefunzioni import pyganim
from pygame.locals import*
from pygame.time import Clock
import tiledtmxloader
import pprint

file_mappa="D:\\games\\tmwa\\maps\\001-2.tmx"
world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(file_mappa)



i=0
for mio in world_map.layers:
	print mio.name
	if mio.name=="Collision":
		print dir(world_map.layers[i])
		world_map.layers.pop(i)
	i=i+1

for mio in world_map.layers:
	print mio.name



#print dir(world_map)
#print world_map.layers

#for mio in world_map.tile_sets:
#	print mio.name

resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()

resources.load(world_map)
#print dir(resources)
#print resources 
#sprite_layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)