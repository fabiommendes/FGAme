#-*- coding: utf8 -*-
'''
Implementa o exemplo de "pseudo-gravidade" da documentação.
'''

from FGAme import *
from FGAme.force import SpringF, GravityF, SpringSF, GravitySF

#get_mainloop(fps=240)

class Gravity(World):
    def __init__(self):
        # Chamamos o __init__ da classe pai
        super(Gravity, self).__init__()

        # Criamos dois objetos
        A = Circle(20, pos=(500, 300), vel=(100, 300), color='red')
        B = Circle(20, pos=(400, 300), vel=(-100, -300))
        self.A, self.B = A, B
        self.add([A, B])

        # Definimos a força de interação entre ambos
        K = self.K = A.mass
        F = SpringF(A, B, (K, 2 * K))
        F = GravityF(A, B, 3e4)
        Fa = SpringSF(A, 2 * K, r0=(0, 0))
        Fb = GravitySF(B, 0.9e4, epsilon=10)
        A.external_force, B.external_force = F.forces()
        #A.external_force = Fa
        #B.external_force = Fb

        E0 = F.totalE()
        #E0 = Fa.totalE() + Fb.totalE()
        @self.listen('frame-enter')
        def printP():
            print('%.e' % (Fa.totalE() + Fb.totalE() - E0))
            #print(F.totalE() / E0)

if __name__ == '__main__':
    Gravity().run()
