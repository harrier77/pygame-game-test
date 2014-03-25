import os, sys, inspect
import paths
cmd_folder = os.path.realpath(".//gumworld2/")
if cmd_folder not in sys.path:
     sys.path.insert(0, cmd_folder)

