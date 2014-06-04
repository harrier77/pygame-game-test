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
from miovar_dump import *



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
        fitem2 = fileMenu.Append(3, 'Membri oggetto', 'QTesto')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_MENU, self.OnOpen, fitem1)
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.Bind(wx.EVT_MENU, self.OnText, fitem2)
        
        pnl = wx.Panel(self)
        pnl.SetBackgroundColour((0, 0, 0))
        vbox = wx.BoxSizer(wx.VERTICAL)
        favicon = wx.Icon('pirate.ico', wx.BITMAP_TYPE_ICO, 16, 16)
        wx.Frame.SetIcon(self, favicon)
        
        #self.testo = wx.StaticText(parent=pnl, pos=(50, 50),style=wx.BORDER_SIMPLE,size=(700,500))
        #self.testo.SetBackgroundColour('white')
        #self.testo.SetLabel(label='')
        #self.testo.SetLabel(label='Qui vengono mostrate le informazioni sul gioco...')
        self.testo1 = wx.TextCtrl(parent=pnl, value="Qui vengono mostrate le informazioni sul gioco...", pos=(40, 40), size=(700,500),style=wx.TE_MULTILINE|wx.TE_LINEWRAP)

        # A button
        #self.button =wx.Button(pnl, label="Lancia gioco",pos=(20,20))
        #self.Bind(wx.EVT_BUTTON, self.OnOpen,self.button)
        #self.button1 =wx.Button(pnl, label="Stop",pos=(200,20))
        #self.Bind(wx.EVT_BUTTON, self.OnStop,self.button1)
        #self.button1 =wx.Button(pnl, label="Nascondi",pos=(400,20))
        #self.Bind(wx.EVT_BUTTON, self.OnHide,self.button1)
        
        #vbox.Add(self.version, flag=wx.ALL, border=5)
        #pnl.SetSizer(vbox)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKey)
        self.SetSize((805, 622))
        self.SetTitle('Pannello comandi')
        #self.Centre()
        self.SetPosition((18,60))
        #self.Show(True)
        self.OnOpen()
    
    def OnOpen(self):
        print "open"
        
        pygame.init()
        self.External_Executable = Thread ()
        self.External_Executable.daemon=True
        self.External_Executable.start()
        self.External_Executable.oggetto.wx=self
    
    def OnStop(self,e):
        pygame.quit()
        self.External_Executable.oggetto.pop()
        
    def OnHide(self,e):
        self.Show(False)
        
    
    def OnShow(self,e):
        self.Raise() 
        pass
    
    def OnText(self,e):
        oldtext= self.testo1.GetValue()
        text=self.External_Executable.oggetto.mappa_dirfile
        #self.testo.SetLabel(label=oldtext+"\n"+"Mappa in esecuzione:"+text)
        self.testo1.SetValue(oldtext+"\n"+"Mappa in esecuzione:"+text)
        beasts=self.External_Executable.oggetto.lista_beast
        foo = WritableObject()                   # a writable object
        original = sys.stdout
        sys.stdout = foo                         # redirection
        miovar_dump(self.External_Executable.oggetto)
        for k,beast in beasts.iteritems():
            print beast
        oldtext= self.testo1.GetValue()
        #self.testo.SetLabel(label=oldtext+"\n"+' '.join(foo.content))
        self.testo1.SetValue(oldtext+"\n"+' '.join(foo.content))
        sys.stdout=original
    def OnQuit(self, e):
        #self.OnHide(e)
        #self.Close()
        print "quit"
    
    def OnClose(self, e):
        """dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()"""
        self.OnHide(e)
    
    def onKey(self, evt):
        print evt.GetKeyCode()
        if evt.GetKeyCode()==345:
            self.OnClose(evt)
        if evt.GetKeyCode() == wx.WXK_DOWN:
            print "Down key pressed"
        else:
            evt.Skip()
        

def main():
    
    ex = wx.App()
    Example(None)
    ex.MainLoop()    


if __name__ == '__main__':
    main()