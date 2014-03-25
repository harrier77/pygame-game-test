import cProfile, pstats

import pygame
from pygame.sprite import Sprite
from pygame.locals import *
import sys
sys.path.append("./miogummworld") 
import paths
import gummworld2
from gummworld2 import context, data, model, geometry, toolkit
from gummworld2 import Engine, State, TiledMap, Vec2d
from miefunzioni import pyganim
from miefunzioni import miodebug
import tiledtmxloader


class Avatar(model.Object):
    
        def __init__(self, map_pos, screen_pos):
                model.Object.__init__(self)		
                self.animated_object=self.crea_giocatore_animato()
                self.giocatore_animato=self.animated_object['front_walk']
                self.image= self.giocatore_animato.ritorna_fotogramma()
                self.rect = self.image.get_rect()
                self.position = map_pos
                self.screen_position = screen_pos
                
        def crea_giocatore_animato(self):
                # load the "standing" sprites (these are single images, not animations)
                front_standing = pygame.image.load('gameimages/crono_front.gif')
                back_standing = pygame.image.load('gameimages/crono_back.gif')
                left_standing = pygame.image.load('gameimages/crono_left.gif')
                right_standing = pygame.transform.flip(left_standing, True, False)

                playerWidth, playerHeight = front_standing.get_size()
                # creating the PygAnimation objects for walking/running in all directions
                animTypes = 'back_run back_walk front_run front_walk left_run left_walk'.split()
                animObjs = {}
                for animType in animTypes:
                    imagesAndDurations = [('gameimages/crono_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
                    animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)
                # create the right-facing sprites by copying and flipping the left-facing sprites
                animObjs['right_walk'] = animObjs['left_walk'].getCopy()
                animObjs['right_walk'].flip(True, False)
                animObjs['right_walk'].makeTransformsPermanent()
                animObjs['right_run'] = animObjs['left_run'].getCopy()
                animObjs['right_run'].flip(True, False)
                animObjs['right_run'].makeTransformsPermanent()
                moveConductor = pyganim.PygConductor(animObjs)
                moveConductor.play()
                return animObjs
#-------------------------------------------------------------------------------



class App(Engine):
    
    def __init__(self, resolution=(1200,600)):
        resolution = Vec2d(resolution)
        
        ## Load Tiled TMX map, then update the world's dimensions.
        #tiled_map = TiledMap(data.filepath('map', 'Gumm no swamps.tmx'))
        tiled_map = TiledMap('mappe/001-1.tmx')

        Engine.__init__(self,
            caption='Tiled Map',
            resolution=resolution,
            camera_target=Avatar((325,420), resolution//2),
            map=tiled_map,
            frame_speed=0)
       
        self.visible_objects = []
        # I like huds.
        toolkit.make_hud()

        State.speed = 3.33
        self.movex = 0
        self.movey = 0
        self.cammina=False
        #miodebug.meth_dump(State.map.layers[0])
        self.visible_objects = toolkit.get_object_array()

        
    
    def update(self, dt):
        """overrides Engine.update"""
        if self.movex or self.movey:
            State.camera.position += self.movex,self.movey
        State.camera.update()
        self.visible_objects = toolkit.get_object_array()
        State.hud.update(dt)
 
    
    def draw(self, interp):
        """overrides Engine.draw"""
        # Draw stuff.
        State.screen.clear()
        toolkit.draw_object_array(self.visible_objects)
        State.hud.draw()
        self.draw_avatar()
        State.screen.flip()
    
    def draw_avatar(self):
        camera = State.camera
        self.avatar = camera.target
        if self.cammina:self.avatar.image= self.avatar.giocatore_animato.ritorna_fotogramma()
        camera.surface.blit(self.avatar.image, self.avatar.screen_position)

     

        

    def on_key_down(self, unicode, key, mod):
        self.cammina=True
        if key == K_DOWN: 
                self.movey += State.speed
                self.avatar.giocatore_animato=self.avatar.animated_object['front_walk']
        elif key == K_UP: 
                self.movey += -State.speed
                self.avatar.giocatore_animato=self.avatar.animated_object['back_walk']
        elif key == K_RIGHT: 
                self.movex += State.speed
                self.avatar.giocatore_animato=self.avatar.animated_object['right_walk']
        elif key == K_LEFT: 
                self.movex += -State.speed
                self.avatar.giocatore_animato=self.avatar.animated_object['left_walk']
        elif key == K_ESCAPE: context.pop()
        
        

    def on_key_up(self, key, mod):
            self.cammina=False
            if key == K_DOWN: self.movey -= State.speed
            elif key == K_UP: self.movey -= -State.speed
            elif key == K_RIGHT: self.movex -= State.speed
            elif key == K_LEFT: self.movex -= -State.speed
    
    def on_quit(self):
        context.pop()


def main():
    app = App()
    #miodebug.var_dump(app)
    gummworld2.run(app)


"""
if __name__ == '__main__':
    if False:
        cProfile.run('main()', 'prof.dat')
        p = pstats.Stats('prof.dat')
        p.sort_stats('time').print_stats()
    else:
        main()
"""
if __name__ == '__main__':main()