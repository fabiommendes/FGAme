# -*- coding: utf8 -*-

'''
Implementa o exemplo de "pseudo-gravidade" da documentação.
'''

from FGAme import *  # @UnusedWildImport
from FGAme.physics.forces import SpringTensorPair


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
        F = SpringTensorPair(A, B, (K, 2 * K))
        A.force, B.force = F.forces()

        E0 = F.energyT()

        @self.listen('frame-enter')
        def printP():
            print('%.e' % (F.energyT() + F.energyT() - E0))

if __name__ == '__main__':
    Gravity().run()
