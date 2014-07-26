import pickle
from miovardump import miovar_dump
from moving_beast import MovingBeast

class Salvataggio():
    def __init__(self):
        self.matr_layer_raccolto=[]
        self.avatar_pos=(100,100)
    #-----------------------------
    def salva(self,motore=None):
        dati=dict()
        dati['matr_layer_raccolto']=motore.matr_layer_raccolto
        dati['avatar_pos']=motore.avatar.position
        dati['animati']=list()
        for id,beast in motore.lista_beast.iteritems():
            dati['animati'].append({'id':id,'classe':beast.classe,'is_segui':beast.segui,'posizione':(int(beast.x),int(beast.y))})
        filename="saved\\salvataggio.txt"
        pickle.dump(dati, open(filename,"wb" ) )


    #-----------------------------
    def ricarica(self,motore=None):
        filename="saved\\salvataggio.txt"
        dati=pickle.load(open( filename, "rb" ))
        nuovamatrice=dati['matr_layer_raccolto']
        motore.mag.ricostruisci_layer_raccolto(nuovamatrice)
        motore.avatar.position=dati['avatar_pos']
        motore.avatar.rect.x=dati['avatar_pos'][0]
        motore.avatar.rect.y=dati['avatar_pos'][1]
        motore.avatar_group.add(motore.avatar)
        del motore.lista_beast
        motore.lista_beast=dict()
        for layer in motore.overlays:
            sprites = layer.objects.intersect_objects(motore.State.camera.rect)
            for s in sprites:
                if isinstance(s,MovingBeast):
                    motore.avatar_group.objects.remove(s)

#Eofclass#-------------------------------------------------