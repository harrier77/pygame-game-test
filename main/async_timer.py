import pygame
import time
import sys
import weakref

#-------------------------------------------------
class Pseudo_async_timer():
    scaduto=False
    id=None
    def __init__(self,pausa,func,id=None):
            self.set_future_time(pausa)
            self.pausa=pausa
            self.id=id
            self.func_da_chiamare=func
    def set_future_time(self,pausa):
            t = time.time()
            self.fut_t=t+pausa
    def check_time(self):
            tnow=time.time()
            if (tnow>self.fut_t):
                    if not self.scaduto:
                            print "scaduta pausa "+str(self.pausa)
                            self.scaduto=True
                            self.func_da_chiamare(self)
                            return True
#-------------------------------------------------


#-------------------------------------------------               
class Gruppo_timer():
    lista_timer=[]
    def add_timer(self,pausa,fun_callback,id):
            newt=Pseudo_async_timer(pausa,fun_callback,id)
            self.lista_timer.append(newt)
    def controlla_tutti_timer(self):
            for id,t in enumerate(self.lista_timer):
                    if t.check_time():
                            self.lista_timer.pop(id)
#-------------------------------------------------

#-------------------------------------------------
def fun_callback(reference):
        print "chiamata"
        print reference.id
        reference=None
        pass
#-------------------------------------------------

def main():
        pygame.init()

        print "parent"
        running_loop=True
        screen = pygame.display.set_mode((400,300))
        m=Gruppo_timer()
        m.add_timer(10,fun_callback,1)
        m.add_timer(3,fun_callback,2)
        m.add_timer(1,fun_callback,3)
        m.add_timer(4,fun_callback,4)
        while running_loop:
                screen.fill((0, 0, 0))
                coda_eventi=pygame.event.get()
                for event in coda_eventi:
                        if event.type == pygame.QUIT:
                                running_loop = False
                        elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                        running_loop = False
                                elif event.key==pygame.K_F4:
                                        print m.lista_timer

                if m.lista_timer: m.controlla_tutti_timer()
                
                pygame.display.flip()
                
if __name__ == '__main__':
        main()