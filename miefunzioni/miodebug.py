import pprint
import inspect

def var_dump(oggetto):
        #print oggetto.__dict__
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(oggetto.__dict__)
        #pp.pprint(dir(oggetto))

def meth_dump(oggetto):
        for name, data in inspect.getmembers(oggetto):
            if name == '__builtins__':
                continue
            print '%s :' % name, repr(data)
                