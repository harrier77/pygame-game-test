#!/usr/bin/python -OO

import miopaths
import gummworld2
import __builtin__
__builtin__.miavar=True
__builtin__.miodebug=False
from main import myengine


import pygame
import os

pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()                      #initialize pygame

pygame.mixer.music.load(os.path.join('suoni', 'open.ogg'))#load music

#music is already the name of the music object
#pygame.mixer.music.play(loops=0, start=0.0): return None
pygame.mixer.music.play(-1) # play endless

#import cProfile

myengine.newmain(debug=False)

#cProfile.run('myengine.miomain(debug=False)','rstats')