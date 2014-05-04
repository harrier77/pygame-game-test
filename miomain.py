import miopaths
import gummworld2
import __builtin__
__builtin__.miavar=True
__builtin__.miodebug=False
from main import myengine
#import cProfile
myengine.miomain(debug=False)
#cProfile.run('myengine.miomain(debug=False)','rstats')