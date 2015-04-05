# coding: utf-8
import os
from os.path import relpath
import pygame
from pygame.locals import *
import librerie
from gummworld2 import model,State
from librerie import pyganim,gui
from salvataggi import *

class DialogoAvvisi(gui.Dialog):
    def __init__(self,**params):
        testo=params['testo']
        self.scrivi_testo(testo)
        self.init_app()
    def scrivi_testo(self,testo):
        title = gui.Label("Avviso")
        doc = gui.Document(width=200,height=200)
        gui.Dialog.__init__(self,title,doc)
        space = title.style.font.size(" ")
        for word in testo.split(" "): 
            doc.add(gui.Label(word))
            doc.space(space)
        doc.br(space[1])
    def init_app(self):
        area=pygame.Rect(300,200,400,400)
        app = gui.App()
        self.open()
        app.init(screen=State.screen.surface,widget=self,area=area)
        app.paint()
        pygame.display.flip()
        while 1:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                break
        pygame.key.set_repeat()
        
#EofClass----------------

class Selettore(gui.Container):
    def __init__(self,**params):
        motore=params['motore']
        if motore.mag.selezionabili:
            if not True in motore.mag.selezionabili.values():
                firstkey=motore.mag.selezionabili.iterkeys().next()
                motore.mag.selezionabili[firstkey]=True
            sprite_selez=self.individua_selezionato(motore.mag.selezionabili,motore.mag.raccolti)
        else:
            return
        
        if sprite_selez==None:
            dialog = DialogoAvvisi(testo="Seleziona un'arma o uno strumento da usare! (tasto E)")
            return
        self.immagine=gui.Image(sprite_selez.image)
        self.dic_selezionabili=motore.mag.selezionabili
        self.dic_raccolti=motore.mag.raccolti
        w=40
        h=40
        posx=(800-w)/2
        posy=600-h
        self.doc = gui.Document(width=w,height=h,valign=-1,align=0)
        self.doc.add(self.immagine,align=-1)
        titlewidg = gui.Label("Sel")
        #gui.Dialog.__init__(self,titlewidg,self.doc,valign=-1,align=-1)
        self.my_dialog_init(titlewidg,self.doc)
        area=pygame.Rect(posx,posy,w,h)
        self.app = gui.App()
        
        self.open()
        self.app.init(screen=State.screen.surface,widget=self,area=area)
        self.app.paint()
        pygame.display.flip()

        self.ciclo()
    #-----------------------------
    def my_dialog_init(self,title,main,**params):
        params.setdefault('cls','selettore')
        #gui.Table.__init__(self,**params)
        #self.tr()
        #self.td(main,colspan=2,cls=self.cls+".main")
        gui.Container.__init__(self,**params)
        self.add(main,0,0)
        
    #-----------------------------
    def individua_selezionato(self,lista,dic_raccolti):
        selezionato=None
        sprite_selez=None
        for nome,condizione in lista.iteritems():
            if condizione:
                selezionato=nome
                self.selez=nome
        if selezionato is not None:
            for key,record in dic_raccolti.iteritems():
                if record[0]['nome']==selezionato:
                    sprite_selez=record[1]          
        return sprite_selez
    #------------------------------
    def cambia_selez(self,verso='next'):
        for k,condizione in self.dic_selezionabili.iteritems():
            if condizione:
                self.dic_selezionabili[k]=False
                if verso=='next':
                    scelto=self.dic_next[1][k]
                elif verso=='prev':
                    scelto=self.dic_next[0][k]
                if scelto is None:
                    scelto=self.dic_selezionabili.keys()[0]
                self.dic_selezionabili[scelto]=True
                break
        sprite_selez=self.individua_selezionato(self.dic_selezionabili,self.dic_raccolti)
        self.doc.remove(self.immagine)
        self.immagine=gui.Image(sprite_selez.image)
        self.doc.add(self.immagine,align=-1)
        self.app.paint()
        pygame.display.flip()
    #--------------------------------------------------
    def neighborhood(self,iterable):
        iterator = iter(iterable)
        prev = None
        item = iterator.next()  # throws StopIteration if empty.
        for next in iterator:
            yield (prev,item,next)
            prev = item
            item = next
        yield (prev,item,None)
    #----------------------------------
    @property
    def dic_next(self):
        mydic_next=dict()
        mydic_prev=dict()
        for lista_vicini in self.neighborhood(self.dic_selezionabili):
            previous=lista_vicini[0]
            next=lista_vicini[2]
            item=lista_vicini[1]
            mydic_prev[item]=previous
            mydic_next[item]=next
        return (mydic_prev,mydic_next)
    #----------------------------
    def ciclo(self):
        while 1:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                if event.button==4 or event.button==5:
                    self.cambia_selez()
                else:
                    break
            if event.type == KEYDOWN:
                if event.key == K_h or event.key ==K_ESCAPE:
                    break
                if event.key==K_RIGHT:
                    self.cambia_selez(verso='next')
                if event.key==K_LEFT:
                    self.cambia_selez(verso='prev')
                    
        pygame.key.set_repeat()
#EofClass----------------    

#-------------------------------------------------------------------------------
class PguApp():
    def __init__(self,motore_genitore,inizio='menu'):
        self.scelta=0
        self.motore=motore_genitore
        #mytheme = gui.Theme(dirs="gray")
        self.app = gui.Desktop(width=800,height=600)
        self.app.connect(gui.QUIT,self.app.quit,None)
        self.tabella = gui.Table(width=200,height=300,valign=-1,y=50)
        self.tabella.style.margin_top=50
        #selezionatoimg=pygame.image.load('.\\immagini\\selezionato.png').convert_alpha()
        selezionatoimg=pygame.image.load(os.path.join('immagini','selezionato.png')).convert_alpha()
        self.selezionatoimg=pygame.transform.scale(selezionatoimg,(28,28))
        #print self.tabella.style.margin_top
        if inizio=="inventario":
            self.inventario()
        elif inizio=="animali":
            self.inventario_animali()
        elif inizio=="mappa":
            self.mini_mappa()
        elif inizio=='salvataggi':
            self.menu_salvataggi()
        else:
            self.menu()
        
        self.app.init(self.tabella)
        self.mioloop=True
        clock = pygame.time.Clock()
        while self.mioloop:
                mousemotions = pygame.event.get(MOUSEMOTION)
                if mousemotions: #checks if the list is nonempty
                        mousemotion = mousemotions[-1]
                coda_eventi=pygame.event.get()
                for event in coda_eventi:
                        if event.type == pygame.QUIT:
                            self.quit()
                        elif event.type == pygame.USEREVENT:
                            continue
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button==4:
                                print 'prossimo'
                            if event.button==5:
                                print "precedente"
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_e:
                                self.quit()
                            if event.key == pygame.K_ESCAPE:
                                self.quit()
                                    
                        self.app.event(event)
                        self.app.paint()
                        pygame.display.flip()
                        

        pygame.key.set_repeat()
    #-------------------------------------------------------------------------------   
    def menu(self):
        self.tabella.tr()
        inventario=gui.Button(value='Inventario')
        inventario.connect(gui.CLICK,self.inventario)
        self.tabella.td(inventario)
        
        self.tabella.tr()
        inv_animali=gui.Button(value='Animali al seguito')
        inv_animali.connect(gui.CLICK,self.inventario_animali)
        self.tabella.td(inv_animali)

        self.tabella.tr()
        tornabtn=gui.Button(value='Torna al gioco')
        tornabtn.connect(gui.CLICK,self.quit)
        self.tabella.td(tornabtn)
        nrighe=self.tabella.getRows()
        self.tabella.style.height=nrighe*50
        
    def carica_salvato(self,filename):
        self.salvato=Salvataggio()
        self.salvato.ricarica_manuale(target_file=filename)
        self.mappa_da_ricaricare=dict()
        self.mappa_da_ricaricare=self.salvato.root
        self.scelta=2
        if self.motore.is_motore_runnig:
            dirmappa=self.mappa_da_ricaricare['quale_mappa']
            self.motore.init_partita_salvata(dir_mappa=dirmappa,miodebug=False,objsalvataggio=self.salvato)
        self.quit()
        
        
    def menu_riprendi(self):
        self.tabella.clear()
        self.tabella.tr()
        etichettacomandi=gui.Label("Partite salvate:",color=(255,0,0,1))
        self.tabella.td(etichettacomandi,colspan=2)
        miopath=os.path.join('saved','')
        lista_file=os.listdir(miopath)
        for filename in lista_file:
             self.tabella.tr()
             etif=gui.Link(filename)
             etif.connect(gui.CLICK,self.carica_salvato,filename)
             self.tabella.td(etif)
        nrighe=self.tabella.getRows()
        self.tabella.style.height=nrighe*50
    
    def new_game(self):
        self.scelta=1
        if self.motore.is_motore_runnig:
            dirmappa=self.motore.dirmappa
            self.motore.init_nuova_partita(dir_mappa=dirmappa,miodebug=False)
        self.quit()
        
    def menu_salvataggi(self):
        self.tabella.clear()
        self.tabella.tr()
        nuova=gui.Button(value='Nuova gioco')
        #nuova.connect(gui.CLICK,self.quit)
        nuova.connect(gui.CLICK,self.new_game)
        self.tabella.td(nuova,colspan=3)
        
        self.tabella.tr()
        riprendi=gui.Button(value='Carica gioco salvato')
        riprendi.connect(gui.CLICK,self.menu_riprendi)
        self.tabella.td(riprendi,colspan=3)
        
        self.tabella.tr()
        tornabtn=gui.Button(value='Torna al gioco')
        tornabtn.connect(gui.CLICK,self.quit)
        self.tabella.td(tornabtn,colspan=3)
        
        self.tabella.tr()
        etichettacomandi=gui.Label("Comandi da tastiera",color=(255,0,0,1))
        #etichettacomandi.style.font.size=" "
        self.tabella.td(etichettacomandi,colspan=2)

        self.tabella.tr()
        etichetta=gui.Label("Selettore armi:",align=0)
        self.tabella.td(etichetta)
        etichetta1=gui.Label("h + rotellina")
        self.tabella.td(etichetta1)

        
        self.tabella.tr()
        etichetta=gui.Label("Inventario oggetti:")
        self.tabella.td(etichetta)
        etichetta1=gui.Label("t")
        self.tabella.td(etichetta1)
        
        self.tabella.tr()
        etichetta=gui.Label("Animali catturati:")
        self.tabella.td(etichetta)
        etichetta1=gui.Label("e")
        self.tabella.td(etichetta1)
        
        self.tabella.tr()
        etichetta=gui.Label("Visualizza mappa:")
        self.tabella.td(etichetta)
        etichetta1=gui.Label("m")
        self.tabella.td(etichetta1)
        
        self.tabella.tr()
        etichetta=gui.Label("Questo menu':")
        self.tabella.td(etichetta)
        etichetta1=gui.Label("F1")
        self.tabella.td(etichetta1)
        
        nrighe=self.tabella.getRows()
        self.tabella.style.height=nrighe*50
        
        
        
    #-------------------------------------------------------------------------------
    def scarica(self,id_cosa_raccolta,i,tab_riga,eti,immagine,idx_img,sel):
        if id_cosa_raccolta in self.motore.lista_beast:
            self.motore.lista_beast[id_cosa_raccolta].segui=False
            print self.motore.lista_beast[id_cosa_raccolta].properties
            try:
                del self.motore.mag.seguito[i]
                self.motore.lista_beast[id_cosa_raccolta].properties['sottotipo']='catturabile'
            except:
                #print "i="+str(i),self.motore.mag.seguito
                exit()
        else:
            obj=pygame.sprite.Sprite()
            obj.image=immagine.value #is a surface, 32x32
            obj.rect=obj.image.get_rect()
            obj.rect.x=self.motore.avatar.rect.x+16
            obj.rect.y=self.motore.avatar.rect.y+16
            obj.img_idx=idx_img
            self.motore.raccolto_spathash.add(obj)
            r=self.motore.avatar.rect.x/32
            c=self.motore.avatar.rect.y/32
            obj.name=(r,c)
            #print type(idx_img)
            self.motore.matr_layer_raccolto[r][c]=idx_img
            #for i in self.motore.tiled_map.mio_resource.indexed_tiles:
                #print i
            #print self.motore.tiled_map.mio_resource.indexed_tiles[582]
            nomestrumento=self.motore.mag.raccolti[i][0]['nome']
            self.motore.mag.raccolti.pop(i)
            self.motore.mag.selezionabili.pop(nomestrumento)
        self.tabella.remove(tab_riga)
        self.tabella.remove(eti)
        self.tabella.remove(immagine)
        self.tabella.remove(sel)
    #-------------------------------------------------------------------------------
    def loop_inventario(self,lista_oggetti):
        sel_val=''
        for s in self.motore.mag.selezionabili:
            if self.motore.mag.selezionabili[s] ==True:sel_val=s
        
        self.g = gui.Group(name='armi',value=sel_val)
        #unchainimg=pygame.image.load('.\\immagini\\unchain.png').convert_alpha()
        unchainimg=pygame.image.load(os.path.join('immagini','unchain.png')).convert_alpha()
        unchainimg=pygame.transform.scale(unchainimg,(20,20))
        iconunchain=gui.Image(unchainimg)
        for i,cosa in lista_oggetti.iteritems():
                eti=gui.Label(cosa[0]['nome'])
                immagine=gui.Image(cosa[1].image)
                #immagine=pygame.sprite.Sprite()
                self.tabella.tr()
                self.tabella.td(eti)
                self.tabella.td(immagine)
                L=gui.Button(iconunchain)
                dic=cosa[0]
                if 'numero' in dic:idx_img=dic['numero'] 
                else:idx_img=0 
                sel=gui.Radio(self.g,value=dic['nome'])
                L.connect(gui.CLICK,self.scarica,dic['nome'],i,L,eti,immagine,idx_img,sel)
                self.tabella.td(L)
                self.tabella.td(sel)
        nrighe=self.tabella.getRows()
        self.tabella.style.height=nrighe*10
    #-------------------------------------------------------------------------------       
    def inventario(self):
        self.tabella.clear()
        self.tabella.tr()
        if len(self.motore.mag.raccolti)==0:
            etichetta=gui.Label("Avvicinati a qualcosa per raccoglierlo")
        else:
            etichetta=gui.Label("Inventario oggetti raccolti:")
        
        self.tabella.td(etichetta,colspan=2)
        self.loop_inventario(self.motore.mag.raccolti)
    #------------------------------------------------------------------------------- 
    def inventario_animali(self):
        self.tabella.clear()
        self.tabella.tr()
        etichetta=gui.Label("Animali al seguito:")
        self.tabella.td(etichetta,colspan=2)
        self.loop_inventario(self.motore.mag.seguito)
    #-------------------------------------------------------------------------------
    def mini_mappa(self):
        self.tabella.clear()
        self.tabella.style.margin_top=90
        #mappa=pygame.image.load('.\\immagini\\minimappa.jpg').convert()
        mappa=pygame.image.load(os.path.join('immagini','minimappa.jpg')).convert()
        mappa=pygame.transform.scale(mappa,(550,494))
        immagine=gui.Image(mappa)
        self.tabella.tr()
        self.tabella.td(immagine)
        
    #-------------------------------------------------------------------------------
    def quit(self):
        if hasattr(self,'g'):
            for s in self.motore.mag.selezionabili:
                self.motore.mag.selezionabili[s]=False
            if self.g.value in self.motore.mag.selezionabili:
                self.motore.mag.selezionabili[self.g.value]=True
        self.mioloop=False
#EofCLass-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class AutoDict(dict):
    def __init__(self):
        dict.__init__(self)
        self.id=0
        self.ultimo=0  
    def append(self,item):
        self.id=self.id+1
        self[self.id]=item
        self.ultimo=max(self.keys())
    
    @property
    def lista_nomi_seguito(self):
        mialista=[]
        for i,riga in self.iteritems():
            mialista.append(riga[0]['nome'])
        return mialista
        

    #EofClass

#-------------------------------------------------------------------------------
class Magazzino(model.Object):
    def __init__(self,motore):
        self.motore=motore
        self.raccolti=AutoDict()
        self.seguito=AutoDict()
        self.selezionabili=dict()
        self.suono=pygame.mixer.Sound('suoni/message.wav')
    

    #-------------------------------------------------------
    def remove_single_tile(self,obj):
        self.motore.raccolto_spathash.remove(obj)
        self.motore.matr_layer_raccolto[obj.name[0]][obj.name[1]]=0 #azzera anche il corrispondente contenuto della matrice

    #-------------------------------------------------------        
    def is_raccolto_collide(self):
        newsprite=self.motore.avatar.sprite
        hits=pygame.sprite.spritecollide(newsprite, self.motore.raccolto_spathash.objects,False)
        if hits:
            for obj in hits:
                prop_ogg= self.motore.dict_gid_to_properties[obj.img_idx]
                prop_ogg['mappa']=self.motore.mappa_dirfile
                self.raccolti.append((prop_ogg,obj))
                nomestrumento=prop_ogg['nome']
                self.selezionabili[nomestrumento]=False
                self.remove_single_tile(obj)
                self.motore.raccolto_spathash.remove(obj)
                self.motore.matr_layer_raccolto[obj.name[0]][obj.name[1]]=0 #azzera anche il corrispondente contenuto della matrice
                #print obj.name[0],obj.name[1]
                self.suono.play()
    #-------------------------------------------------------        
    def delete_selezionabile(self,key):
        self.selezionabili.pop(key)
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class Miohero(model.Object):
    #------------------------------------
    def __init__(self,map_pos,screen_pos,parentob,dormi=True):
        model.Object.__init__(self)
        # load the "standing" sprites (these are single images, not animations)
        self.sit_standing=pygame.image.load('animazioni/gameimages/crono_sleep.000.gif')
        self.front_standing = pygame.image.load('animazioni/gameimages/crono_front.gif')
        self.back_standing = pygame.image.load('animazioni/gameimages/crono_back.gif')
        self.left_standing = pygame.image.load('animazioni/gameimages/crono_left.gif')
        self.right_standing = pygame.transform.flip(self.left_standing, True, False)

        self.standing_scelta=self.sit_standing
        self.div_scala=1.8
        self.miosprite=pygame.sprite.Sprite()
        self.parent=parentob
        self.dormi=dormi
        self.animated_object=self.crea_giocatore_animato()
        self.giocatore_animato=self.animated_object['front_walk']
        #self.image= self.giocatore_animato.ritorna_fotogramma()
        self.rect=self.image.get_rect()
        #self.hitbox = self.rect
        self.herosprite=pygame.sprite.Sprite()
        self.herosprite.image=self.image
        self.herosprite.rect=self.rect
        self.position = map_pos
        self.screen_position = screen_pos
        
            
    #------------------------------------       
    def crea_giocatore_animato(self):
        #playerWidth, playerHeight = self.front_standing.get_size()
        # creating the PygAnimation objects for walking/running in all directions
        animTypes = 'back_run back_walk front_run front_walk left_run left_walk'.split()
        animObjs = {}
        for animType in animTypes:
            imagesAndDurations = [('animazioni/gameimages/crono_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 0.1) for num in range(6)]
            animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)
        
        imagesAndDurations = [('animazioni/gameimages/crono_sleep.000.gif',1),('animazioni/gameimages/crono_sleep.001.gif',1)]
        animObjs['sleep']=pyganim.PygAnimation(imagesAndDurations)
        
        for id in animObjs:
                dim_meta=(int(animObjs[id].getRect().width/self.div_scala),int(animObjs[id].getRect().height/self.div_scala))
                animObjs[id].scale(dim_meta)
                
        # create the right-facing sprites by copying and flipping the left-facing sprites
        animObjs['right_walk'] = animObjs['left_walk'].getCopy()
        animObjs['right_walk'].flip(True, False)
        animObjs['right_walk'].makeTransformsPermanent()
        animObjs['right_run'] = animObjs['left_run'].getCopy()
        animObjs['right_run'].flip(True, False)
        animObjs['right_run'].makeTransformsPermanent()

        self.moveConductor = pyganim.PygConductor(animObjs)
        self.moveConductor.play()
        return animObjs
    #------------------------------------
    @property
    def image(self):
        if self.parent.cammina:
            image= self.giocatore_animato.ritorna_fotogramma()
            self.dormi=False
        elif self.dormi:
            self.giocatore_animato=self.animated_object['sleep']
            image=self.giocatore_animato.ritorna_fotogramma()
        else:
            image=self.standing_scelta
            dim_meta= (int(image.get_size()[0]/self.div_scala),int(image.get_size()[1]/self.div_scala))
            image=pygame.transform.scale(image,dim_meta)
        if hasattr(self.parent,'arma') and not self.parent.cammina:
            self.parent.arma.draw_arma()
        return image
    #------------------------------------ 
    @property
    def hitbox(self):
        hitbox=self.rect.copy()
        hitbox.height=12
        hitbox.width=10
        #y = self.rect.y+(hitbox.height/2)
        y = self.rect.y+hitbox.height/2
        x= self.rect.x-(hitbox.width/2)
        
        hitbox.y=y
        hitbox.x=x
        #print hitbox.midbottom
        return hitbox
    
    @property
    def sprite(self):
        miosprite=self.miosprite
        miosprite.image=self.image
        miosprite.rect=self.hitbox
        return miosprite

#-------------------------------------------------------------------------------   
class Arma(object):
    def __init__(self,parent,nomeutensile='spada'):
        self.parent=parent
        #self.load(nomeutensile)

    #def load(self,nomeutensile):
    #    arma=pygame.image.load('immagini/'+nomeutensile+'.png').convert()
    #    self.arma=pygame.transform.scale(arma,(16,16))
        
    @property
    def arma_img(self):
        colorkey = self.arma.get_at((0,0))
        self.arma.set_colorkey(colorkey, RLEACCEL)
        return self.arma
    
    def draw(self):
        cx,cy=self.parent.State.camera.rect.topleft
        img=self.arma_img
        avatar=self.parent.avatar
        direzione=self.parent.direzione_avatar
        if not avatar.dormi:
            x=avatar.rect.x-cx
            y=avatar.rect.y-cy
            if direzione=='right':
                x=avatar.rect.x-cx-3
                y=avatar.rect.y-cy-9
            elif direzione=='left':
                img=pygame.transform.flip(self.arma_img,True,False)
                y=avatar.rect.y-cy-9
                x=avatar.rect.x-cx-25
            elif direzione=='front':
                y=avatar.rect.y-cy-4
                x=avatar.rect.x-cx-12
            elif direzione=='back':
                img=pygame.transform.rotate(self.arma_img,200)
                img=pygame.transform.scale(img,(10,10))
                y=avatar.rect.y-cy+5
                x=avatar.rect.x-cx
            #print direzione+str(x)+ str(y)
            self.parent.screen.blit(img,(x,y))
    
    def draw_arma(self):
        if 'spada' in self.parent.mag.selezionabili:
            if self.parent.mag.selezionabili['spada']:
                arma=pygame.image.load('immagini/spada.png').convert()
                self.arma=pygame.transform.scale(arma,(16,16))
                self.draw()
        if 'piccone' in self.parent.mag.selezionabili:
            if self.parent.mag.selezionabili['piccone']:
                arma=pygame.image.load('immagini/piccone.png').convert()
                self.arma=pygame.transform.scale(arma,(24,24))
                self.draw()
            
#--EofClass---------------------------------------------------------                

#function
def filter_dic_for_json(dic):
    for key,val in dic.iteritems():
        print key,val
        print type(val)
            
    return dic
#eofunction
#function
def lista_matrice_gids(matrice):
    #le mattonelle del livello sono contenute in cell_ids che però non si può salvare perché contiene surfaces
    #cell_ids=self.tiled_map.layers[5].objects.cell_ids
    #come cancellare una singola cella sul livello 0; inutile perché non ha alcun effetto sulla lista degli sprite
    #self.tiled_map.raw_map.layers[0].content2D[0][1]=0
    #print self.tiled_map.raw_map.layers[5].content2D[7][7] #così si estrae il gid della mattonella alla posizione 7,7
    #print self.tiled_map.mio_resource.indexed_tiles[580][2] #così si può ottenere l'immagine della mattonella con gid 580
    r=0
    c=0
    for riga in matrice:
        for cella in riga:
            if cella:
                sys.stdout.write(" ")
                sys.stdout.write("("+str(r)+",")
                sys.stdout.write(str(c)+")->")
                sys.stdout.write(str(cella)+"\n ")
            c=c+1
        c=0
        r=r+1
    #exit()
#eofunction
