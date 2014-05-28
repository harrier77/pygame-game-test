#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
ZetCode wxPython tutorial

This example shows a simple menu.

author: Jan Bodnar
website: www.zetcode.com
last modified: September 2011
'''

import wx
import os
import miopaths
import subprocess
import threading
import miopaths
import gummworld2
import __builtin__
__builtin__.miavar=True
__builtin__.miodebug=False
import pygame
from main import myengine


class Thread (threading.Thread):
    def __init__(self):
        debug=False
        threading.Thread.__init__(self)
        self.oggetto=myengine.App_gum(resolution=(800,600),miodebug=debug)
        icon=pygame.image.load(".\immagini\\icona2.gif")
        pygame.display.set_icon(icon)
    def run (self):
        gummworld2.run(self.oggetto)


class Example(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs) 
            
        self.InitUI()
        
    def InitUI(self):    

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem1 = fileMenu.Append(wx.ID_OPEN, 'Open', 'Open application')
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        fitem2 = fileMenu.Append(3, 'Testo', 'QTesto')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_MENU, self.OnOpen, fitem1)
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.Bind(wx.EVT_MENU, self.OnText, fitem2)
        
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        
        self.version = wx.StaticText(parent=pnl, pos=(50, 50),style=wx.BORDER_SIMPLE,size=(400,400))
        self.version.SetLabel(label='')
        self.version.SetLabel(label='Qui vengono mostrate le informazioni sul gioco...')
        # A button
        self.button =wx.Button(pnl, label="Lancia gioco",pos=(20,20))
        self.Bind(wx.EVT_BUTTON, self.OnOpen,self.button)
        self.button1 =wx.Button(pnl, label="Stop",pos=(200,20))
        self.Bind(wx.EVT_BUTTON, self.OnStop,self.button1)
        
        #vbox.Add(self.version, flag=wx.ALL, border=5)
        #pnl.SetSizer(vbox)

        self.SetSize((500, 500))
        self.SetTitle('Lanciatore')
        #self.Centre()
        self.SetPosition((850,80))
        self.Show(True)
    
    def OnOpen(self,e):
        print "open"
        pygame.init()
        self.External_Executable = Thread ()
        self.External_Executable.daemon=True
        self.External_Executable.start()
        self.External_Executable.oggetto.wx=self
    
    def OnStop(self,e):
        pygame.quit()
        self.External_Executable.oggetto.pop()
    
    def OnText(self,e):
        print "Text"
        text=self.External_Executable.oggetto.mappa_dirfile
        self.version.SetLabel(label=text)
    
    def OnQuit(self, e):
        self.Close()

def main():
    
    ex = wx.App()
    Example(None)
    ex.MainLoop()    


if __name__ == '__main__':
    main()