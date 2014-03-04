
"""
This is the pygame minimal example.
Modificato per usare pyganim
"""

import sys
import os
import math
import pygame
from pygame.locals import*
from miefunzioni import *
import pprint
from inspect import getmembers


try:
    import _path
except:
    pass

import tiledtmxloader



#  -----------------------------------------------------------------------------

def main():
        """
        Main method.
        """
        """args = sys.argv[1:]
        if len(args) < 1:
        path_to_map = os.path.join(os.pardir, "001-1.tmx")
        print(("usage: python %s your_map.tmx\n\nUsing default map '%s'\n" % \
            (os.path.basename(__file__), path_to_map)))
        else:
        path_to_map = args[0]
        """
        #carica_mappa('..\mappa_luca\mappa luca.tmx')
        carica_mappa("mappe/mappa_luca_x25.tmx")
        
#  -----------------------------------------------------------------------------



        
#  -----------------------------------------------------------------------------

def carica_mappa(file_name,layer_collisioni=2,fullscr='0'):
    x_strega=300
    
    # parser the map (it is done here to initialize the
    # window the same size as the map if it is small enough)
    world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(file_name)

    # init pygame and set up a screen
    pygame.init()
    #pygame.display.set_caption("tiledtmxloader - " + file_name + " - keys: arrows, 0-9")
    
    screen_width = min(900, world_map.pixel_width)
    screen_height = min(600, world_map.pixel_height)
    if fullscr=='0':
        screen = pygame.display.set_mode((screen_width, screen_height))
    elif fullscr=='fullscr':
        screen_width=1366
        screen_height=768
        screen = pygame.display.set_mode((screen_width, screen_height),FULLSCREEN)    

    # load the images using pygame
    resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()
    resources.load(world_map)

    # prepare map rendering
    assert world_map.orientation == "orthogonal"

    # renderer
    renderer = tiledtmxloader.helperspygame.RendererPygame()

    # create hero sprite
    # use floats for hero position
    hero_pos_x = screen_width/3
    hero_pos_y = screen_height/3
    #hero_pos_x=1439
    hero_pos_y=366
    

    animated_object=crea_giocatore()
    giocatore_animato=animated_object['front_walk']
    animated_image= giocatore_animato.ritorna_fotogramma()
    rect = animated_image.get_rect()
    rect.midbottom = (hero_pos_x, hero_pos_y)
    hero=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_image, rect)
      
    strega=crea_strega()
    animated_strega=strega.ritorna_fotogramma()
    animated_strega.get_rect().midbottom=(hero_pos_x, hero_pos_y)
    stregasprite=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_strega,animated_strega.get_rect())
    #print getmembers(stregasprite)
    
    
    # cam_offset is for scrolling
    cam_world_pos_x = hero.rect.centerx
    cam_world_pos_y = hero.rect.centery

    # set initial cam position and size
    renderer.set_camera_position_and_size(cam_world_pos_x, cam_world_pos_y, \
                                        screen_width, screen_height)
    
    corsa=False
    # retrieve the layers
 
    sprite_layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)

    # filter layers
    sprite_layers = [layer for layer in sprite_layers if not layer.is_object_group]

    # add the hero the the right layer, it can be changed using 0-9 keys
    sprite_layers[1].add_sprite(hero)

    # layer add/remove hero keys
    num_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, \
                    pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

    # variables for the main loop
    clock = pygame.time.Clock()
    running_loop = True

    # set up timer for fps printing
    pygame.time.set_timer(pygame.USEREVENT, 1000)

    # mainloop
    cammina=False
    i=2
    speed=2
    font = pygame.font.Font(None, 26)
    direction_x=0
    direction_y=0
    while running_loop:
        dt = clock.tick(200)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_loop = False
            elif event.type == pygame.USEREVENT:
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running_loop = False
                elif event.type == pygame.KEYDOWN:
                        cammina=True
                        if event.key == pygame.K_LEFT:
                                giocatore_animato=animated_object['left_walk']
                                direction_x =-1
                        elif event.key == pygame.K_RIGHT:
                                giocatore_animato=animated_object['right_walk']
                                direction_x =1
                        elif event.key == pygame.K_UP:
                                giocatore_animato=animated_object['back_walk']
                                direction_y =-1
                        elif event.key == pygame.K_DOWN:
                                giocatore_animato=animated_object['front_walk']
                                direction_y =1
                        if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                                corsa=True
                                
            elif event.type == pygame.KEYUP:
                cammina=False
                corsa=False                
                direction_x=0
                direction_y=0
            #end for event handling       

               

        # find directions (metodo originale, sostituito intercettando l'evento event invece di key.get_pressed
        """direction_x = pygame.key.get_pressed()[pygame.K_RIGHT] - pygame.key.get_pressed()[pygame.K_LEFT]
           direction_y = pygame.key.get_pressed()[pygame.K_DOWN] - pygame.key.get_pressed()[pygame.K_UP]"""
        
        
        
        # make sure the hero moves with same speed in all directions (diagonal!)
        dir_len = math.hypot(direction_x, direction_y)
        dir_len = dir_len if dir_len else 1.0
     
        
        if corsa:
                speed=8
        else:
                speed=2
        
        step_x = speed*direction_x / dir_len
        step_y = speed*direction_y / dir_len
        
        hero_width = hero.rect.width
        #attenzione questa non e' la vera altezza ma?
        hero_height = 5   
        
        #controlla se collisione:
        step_x, step_y = check_collision(hero_pos_x, hero_pos_y, step_x, step_y, hero_width, hero_height, sprite_layers[layer_collisioni])
        
        hero_pos_x += step_x
        hero_pos_y += step_y       
        hero.rect.midbottom = (hero_pos_x, hero_pos_y)

        # adjust camera according to the hero's position, follow him
        renderer.set_camera_position(hero.rect.centerx, hero.rect.centery)

        # clear screen, might be left out if every pixel is redrawn anyway
        screen.fill((0, 0, 0))
        
        #------------------------------------------------------
        #gioc_animato=animated_object['right_walk']
        if cammina:
                animated_image= giocatore_animato.ritorna_fotogramma()
                rect = animated_image.get_rect()
                rect.midbottom = (hero_pos_x, hero_pos_y)
                
                sprite_layers[1].remove_sprite(hero)
                hero=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_image, rect)
                sprite_layers[1].add_sprite(hero)
                testog = font.render("Giocatore cammina", 1, (255, 255, 255))
                if corsa:
                        testog = font.render("Giocatore corre", 1, (255, 255, 255))
        else:
                testog = font.render("Giocatore fermo", 1, (255, 255, 255))
        #---------------------------------------------------------
        
        #---------------------------------------------------------
        
        animated_strega=strega.ritorna_fotogramma()
        strega_rect=animated_strega.get_rect()
        x_strega=x_strega+1
        if x_strega>1000:
                x_strega=0
        strega_rect.midbottom=coord_strega(x_strega)
        
        sprite_layers[2].remove_sprite(stregasprite)
        stregasprite=tiledtmxloader.helperspygame.SpriteLayer.Sprite(animated_strega,strega_rect)
        sprite_layers[2].add_sprite(stregasprite)
        
        
        #---------------------------------------------------------
        
        # render the map
        for sprite_layer in sprite_layers:
            if sprite_layer.is_object_group:
                # we dont draw the object group layers
                # you should filter them out if not needed
                continue
            else:
                renderer.render_layer(screen, sprite_layer)
        
        # Display some text
        textx = font.render("Movimento x:"+str(step_x), 1, (255, 255, 255))
        texty = font.render("Movimento y:"+str(step_y), 1, (255, 255, 255))
        screen.blit(textx, (10,10))
        screen.blit(texty, (10,30))
        screen.blit(testog, (10,60))
        
        
        
        pygame.display.flip()
        #end while loop
    

if __name__ == '__main__':

    main()


