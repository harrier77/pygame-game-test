# coding: utf-8                     
import sys
import os
import pygame
from librerie import pyganim
#inizio classe
class Beast():
        
        def __init__(self,dir_name="boar"):
                try:
                        os.stat('animazioni')
                except:
                        print 'cambio dir a ..\\'
                        os.chdir('..\\') 
                anim_file_name=dir_name
                variable_path_name=dir_name+"/"+anim_file_name
                self.front_standing = pygame.image.load('animazioni/animation/'+variable_path_name+'_front_walk.001.gif')
                self.back_standing = pygame.image.load('animazioni/animation/'+variable_path_name+'_back_walk.001.gif')
                self.left_standing = pygame.image.load('animazioni/animation/'+variable_path_name+'_left_walk.001.gif')
                self.right_standing = pygame.transform.flip(self.left_standing, True, False)
                self.playerWidth, self.playerHeight = self.front_standing.get_size()
                self.rect=self.front_standing.get_rect()
                
                # creating the PygAnimation objects for walking/running in all directions
                animTypes = 'left_walk back_walk front_walk NW SW'.split()
                #animTypes = 'back_walk front_walk left_walk'.split()
                self.animObjs = {}
                for animType in animTypes:
                    imagesAndDurations = [('animazioni/animation/'+variable_path_name+'_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
                    self.animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)
                my_aniType=['left_stand']
                for animType in my_aniType:
                    imagesAndDurations1 = [('animazioni/animation/'+variable_path_name+'_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
                    self.animObjs[animType] = pyganim.PygAnimation(imagesAndDurations1)
                
                #create the right-facing sprites by copying and flipping the left-facing sprites
                self.animObjs['right_walk'] = self.animObjs['left_walk'].getCopy()
                self.animObjs['right_walk'].flip(True, False)
                self.animObjs['right_walk'].makeTransformsPermanent()
                
                self.animObjs['SE'] = self.animObjs['SW'].getCopy()
                self.animObjs['SE'].flip(True, False)
                self.animObjs['SE'].makeTransformsPermanent()
                
                self.animObjs['NE'] = self.animObjs['NW'].getCopy()
                self.animObjs['NE'].flip(True, False)
                self.animObjs['NE'].makeTransformsPermanent()
                
                self.animObjs['right_stand'] = self.animObjs['left_stand'].getCopy()
                self.animObjs['right_stand'].flip(True, False)
                self.animObjs['right_stand'].makeTransformsPermanent()
           
                self.moveConductor = pyganim.PygConductor(self.animObjs)



#fine classe -------------------------------------