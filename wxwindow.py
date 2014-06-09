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

        favicon = wx.Icon('pirate1.ico', wx.BITMAP_TYPE_ICO, 16, 16)
        wx.Frame.SetIcon(self, favicon)
        
        
        #self.testo.SetLabel(label='')
        #self.testo.SetLabel(label='Qui vengono mostrate le informazioni sul gioco...')
        
        self.basicText = wx.TextCtrl(pnl, -1, "", size=(175, -1),pos=(40,1))
        self.testo_immesso=self.basicText.GetValue()
        self.basicText.SetInsertionPoint(0)
        # A button
        self.button =wx.Button(pnl, label="View Object",pos=(220,1))
        self.Bind(wx.EVT_BUTTON, self.OnBottone,self.button)
        
        self.basicTextAgg = wx.TextCtrl(pnl, -1, "", size=(175, -1),pos=(380,1))
        self.testo_immesso_agg=self.basicTextAgg.GetValue()
        self.basicTextAgg.SetInsertionPoint(0)
        self.buttonAgg =wx.Button(pnl, label="Change Object",pos=(560,1))
        self.Bind(wx.EVT_BUTTON, self.OnBottoneAgg,self.buttonAgg)
        
        
        self.testo = wx.StaticText(parent=pnl, pos=(40, 30),style=wx.BORDER_SIMPLE,size=(700,20))
        self.testo.SetBackgroundColour('white')
        self.testo1 = wx.TextCtrl(parent=pnl, value="Qui vengono mostrate le informazioni sul gioco...", pos=(40, 60), size=(700,500),style=wx.TE_MULTILINE|wx.TE_LINEWRAP)
        
        """vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.basicText, 1, wx.EXPAND)
        vbox.Add(self.button, 1, wx.EXPAND)
        vbox.Add(self.testo, 1, wx.EXPAND)
        vbox.Add(self.testo1, 1, wx.EXPAND)"""
        #pnl.SetSizer(vbox)
        #vbox.Fit(self)
        
        
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
        self.Show(True)
        self.OnOpen(None)
    
    def OnOpen(self,e):
        print "open"
        pygame.init()
        self.External_Executable = Thread ()
        self.External_Executable.daemon=True
        self.External_Executable.start()
        self.External_Executable.oggetto.wx=self
        self.oggetto_da_vedere=self.External_Executable.oggetto

        
    def OnStop(self,e):
        pygame.quit()
        self.External_Executable.oggetto.pop()
        
    def OnHide(self,e):
        self.Show(False)
        
    
    def OnShow(self,e):
        self.Raise() 
        pass
    
    def OnBottone(self,e):
        self.testo_immesso=self.basicText.GetValue()
        print self.testo_immesso
        if len(self.testo_immesso)>0:
            self.oggetto_da_vedere=eval("self.External_Executable.oggetto"+"."+self.testo_immesso)
        else:
            self.oggetto_da_vedere=self.External_Executable.oggetto 
        
        self.OnText(e)
        
    def OnBottoneAgg(self,e):
        testo_immesso=self.basicTextAgg.GetValue()
        print testo_immesso
        if len(testo_immesso)>0:
            #self.External_Executable.oggetto.lista_beast['interlocutore'].attendi_evento=False
            exec("self.External_Executable.oggetto."+self.basicText.GetValue()+"="+testo_immesso)
        self.OnText(e)
        
        
    
    def OnText(self,e):
        
        oldtext= self.testo1.GetValue()
        text=self.External_Executable.oggetto.mappa_dirfile
        #self.testo.SetLabel(label=oldtext+"\n"+"Mappa in esecuzione:"+text)
        self.testo1.SetValue(oldtext+"\n"+"Mappa in esecuzione:"+text)
        beasts=self.External_Executable.oggetto.lista_beast
        foo = WritableObject()                   # a writable object
        original = sys.stdout
        sys.stdout = foo                         # redirection
        miovar_dump(self.oggetto_da_vedere)
        oldtext= self.testo1.GetValue()
        #self.testo.SetLabel(label=oldtext+"\n"+' '.join(foo.content))
        #self.testo1.SetValue(oldtext+"\n"+' '.join(foo.content))
        self.testo1.SetValue(' '.join(foo.content))
        self.testo.SetLabel(label=str(self.oggetto_da_vedere))
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
        #print evt.GetKeyCode()
        if evt.GetKeyCode()==345:
            self.OnClose(evt)
        if evt.GetKeyCode()==349:
            self.testo.SetLabel(label=str(self.oggetto_da_vedere))
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