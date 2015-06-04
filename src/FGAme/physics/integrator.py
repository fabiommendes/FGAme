from collections import UserList


class Integrator(UserList):

    '''Classe se comporta como uma lista de objetos cuja dinâmica é resolvida
    separadamente do loop principal da FGAme.

    Objetos podem ser adicionados a um grupo do tipo Integrator caso o
    algoritmo de Euler semi-implícito utilizado pela FGAme não possua a
    acurácia necessária para resolução de forças (ex.: sistemas
    autogravitantes)
    '''

    def __init__(self):
        self._data = []

    def add(self, obj):
        '''Adiciona um objeto à lista de objetos'''

        self.append(obj)

    @property
    def data(self):
        return self._data

    def update(self, dt):
        '''Atualiza as posições e velocidades'''


class GravityIntegrator(Integrator):

    def __init__(self):
        super(GravityIntegrator, self).__init__()
        #...

    def update_accelerations(self):
        '''Retorna a lista de acelerações para cada objeto'''

        #...

    def update(self, dt):
        '''Utiliza o método de Velocity Verlet para atualizar as posições e
        velocidades'''

        #...
