import pprint
import inspect
from inspect import *
import sys


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))

def mio_print(ogg):
        global i
        i=i+1
        sys.stdout.write("   ")
        sys.stdout.write(str(i)+": ")                     
        print ""+str(ogg[0])+": "
        sys.stdout.write("    ")
        if str(type(ogg[1]))=="<type 'instance'>":
            print type(ogg[1])
        else:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(ogg[1])
            sys.stdout.write("    (")
            miotipo=str(type(ogg[1]))+" "
            sys.stdout.write(miotipo.split("\'")[1] +")")
        
        print "   - - - - - - - - - - - - -"

def miovar_dump(oggetto,miotip=0):
        print "- - - - - - - - - - - - -"       
        pprint.pprint(oggetto)
        print "- - - - - - - - - - - - -"
        sys.stdout.write("Object type:")
        print type(oggetto)
        testo=inspect.getmembers(oggetto)
        print "  - - - - - - - - - - "
        print "  Members of object:"
        print "  - - - - - - - - - - "
        global i
        i=0
        for ogg in testo:
                
                if (miotip==2): 
                        if (ogg[0]=="__dict__"):
                                pp = pprint.PrettyPrinter(indent=4)
                                pp.pprint (ogg[1])
                else:
                        if ogg[0]=="__dict__":
                                print "   (__dict__: omitted)"
                                print "   - - - - - - - - - - - - -"
                        else: 
                                
                                if miotip==1:
                                        if str(type(ogg[1]))=="<type 'instancemethod'>":
                                                mio_print(ogg)
                                else:
                                        mio_print(ogg)

