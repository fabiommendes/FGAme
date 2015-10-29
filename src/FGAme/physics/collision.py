# -*- coding: utf8 -*-
from math import sqrt
from FGAme.mathtools import Vec2, asvector


#
# Pontos de Contato/Manifolds
#
class ContactPoint(Vec2):

    '''Representa um ponto de contato com um certo nível de penetração'''

    __slots__ = ['depth']

    def __init__(self, x, y, depth):
        super(Vec2, self).__init__(x, y)
        self.depth = depth


class BaseContactManifold(object):

    '''Classe mãe para ContactManifold restitution SimpleContactManifold'''

    def __iter__(self):
        return iter(self.points)


class ContactManifold(BaseContactManifold):

    '''Representa uma lista de pontos de contato associados a uma única
    normal.'''

    __slots__ = ['normal', 'points']

    def __init__(self, normal, points):
        self.normal = normal.normalized()
        self.points = list(points)


class SimpleContactManifold(BaseContactManifold):

    '''Representa um contato simples com apenas um ponto'''

    __slots__ = ['normal', 'point']

    def __init__(self, normal, point):
        self.normal = normal
        self.point = point

    @property
    def points(self):
        return [self.point]

    def __iter__(self):
        yield self.point


#
# Contatos abstratos
#
class Pair(object):

    '''Representa alguma ligação, conexão ou agrupamento de dois objetos'''

    __slots__ = ('A', 'B')

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def swap(self):
        '''Troca os dois objetos do par *INPLACE*'''

        self.B, self.A = self.A, self.B

    def swapped(self):
        '''Retorna um par com os elementos trocados'''

        new = self.copy()
        new.swap()
        return new

    def other(self, obj):
        '''Se for chamada com o objeto A, retorna o objeto B e vice-versa'''

        if obj is self.A:
            return self.B
        elif obj is self.B:
            return self.A
        else:
            raise ValueError('object does not participate in the connection')

    def isvalid(self):
        '''Retorna True caso o contato ainda seja válido ou False caso já tenha
        sido desfeito.'''

        raise NotImplementedError

    def update(self):
        '''Recalcula todas as propriedades que modem ser modificadas de um
        frame para o outro'''

        raise NotImplementedError

    #
    # Propriedades físicas
    #
    def center_of_mass(self):
        A, B = self
        return (A. mass * A.pos + B.mass * B.pos) / (A.mass + B.mass)

    def energyK(self):
        return self.A.energyK() + self.B.energyK()

    def momentumP(self):
        return self.A.momentumP() + self.B.momentumP()

    def momentumL(self):
        pos = (0, 0)
        return self.A.momentumL(pos) + self.B.momentumL(pos)

    #
    # Magic methods
    #
    def __eq__(self, other):
        return self is other

    def __getitem__(self, i):
        if i == 0:
            return self.A
        elif i == 1:
            return self.B
        else:
            raise IndexError(i)

    def __hash__(self):
        return id(self)

    def __iter__(self):
        yield self.A
        yield self.B

    def __contains__(self, element):
        return element is self.A or element is self.B


class BroadContact(Pair):

    '''Representa um contato na Broad phase'''

    def get_collision(self):
        '''Retorna o objecto de collisão associado ao contato. Caso não haja
        colisão, retorna None'''

        raise NotImplementedError


class CBBContact(BroadContact):

    '''Representa um par de objetos com caixas de contorno circulares que
    se sobrepõem'''

    pass


class AABBContact(BroadContact):

    '''Representa um par de objetos com caixas de contorno alinhadas ao eixo
    que se sobrepõem'''

    pass


###############################################################################
#                         Classe Colisão
# ----------------------------------------------------------------------------
#
# Representa uma colisão entre dois objetos.  Resolve a colisão sob demanda.
#
###############################################################################


class Collision(Pair):

    '''Representa a colisão entre dois objetos.

    Subclasses de Collision devem implementar o método .resolve() que resolve
    a colisão entre os dois objetos.

    Example
    -------

    Considere a colisão unidimensional entre dois círculos

    >>> from FGAme.physics import Circle, flags
    >>> A = Circle(1, pos=(0, 1), mass=1, vel=(1, 0))
    >>> B = Circle(1, pos=(2, 1), mass=1)

    A colisão unidimensional de dois objetos de mesma massa simplesmente troca
    as velocidades. Antes disso, no entanto, é necessário passar os parâmetros
    de colisão para que se possa calcular os resultados.

    >>> col = Collision(A, B,
    ...                 pos=(1, 1),    # ponto de colisão
    ...                 normal=(1, 0)) # normal da colisão

    Podemos investigar as propriedades físicas da colisão restitution verificar
    que as leis de conservação são preservadas

    >>> col.energyK(); col.momentumP(); col.momentumL()
    0.5
    Vec(1, 0)
    -1.0

    Podemos resolver a colisão utilizando ou o método step() ou o resolve(). O
    segundo é chamado apenas uma vez restitution já aciona os sinais de
    colisão. O método step() é utilizado em resoluções iterativas com vários
    objetos colidindo simultaneamente.

    >>> col.resolve()

    Agora investigamos os valores finais restitution vemos que as leis de
    conservação foram satisfeitas.

    >>> col.energyK(); col.momentumP(); col.momentumL()
    0.5
    Vec(1, 0)
    -1.0

    Investigando as propriedades, verificamos que de fato a velocidade dos dois
    objetos foi invertida

    >>> A.vel; B.vel
    Vec(0, 0)
    Vec(1, 0)


    Suponha agora que a colisão não se deu no ponto selecionado anteriormente.

    >>> A.vel, B.vel = (1, 0), (0, 0)
    >>> col = Collision(A, B,
    ...                 pos=(0, 0),    # ponto de colisão
    ...                 normal=(1, 0)) # normal da colisão

    Esta posição induz a uma velocidade de rotação e transferência de energia
    de movimento linear para angular.

    >>> col.resolve()
    >>> A.linearK() + B.linearK(), A.angularK() + B.angularK(), col.energyK()
    (0.2777777777777778, 0.2222222222222222, 0.5)

    As leis de conservação continuam sendo satisfeitas
    >>> col.energyK(); col.momentumP(); col.momentumL()
    0.5
    Vec(1, 0)
    -1.0
    '''

    def __init__(self, A, B, normal=None, pos=None, delta=0.0):
        super(Collision, self).__init__(A, B)
        self.normal = normal = asvector(normal)
        self.pos = pos = asvector(pos)
        self.delta = delta = float(delta)
        self.active = True

        # Obtêm parâmetros da colisão
        self.restitution = sqrt(A.restitution * B.restitution)
        self.friction = sqrt(A.friction * B.friction)

    def resolve(self):
        '''Resolve as velocidades dos elementos que participam da colisão'''
        
        if self.friction:
            self.__resolve_with_friction()
        else:
            self.__resolve_simple()
    
    def __resolve_simple(self):
        '''Resolve colisões simples sem atrito'''
        
        A, B = self
        normal = self.normal
        pos = self.pos
        vrel = B.vpoint(pos) - A.vpoint(pos)
        vrel_normal = vrel.dot(normal)

        if vrel_normal < 0:
            # Posições e velocidades relativas
            rA = self.pos - A.pos
            rB = self.pos - B.pos
    
            # Massa efetiva
            invmass = A.invmass + B.invmass
            invmass += A.invinertia * (rA.cross(normal) ** 2)
            invmass += B.invinertia * (rB.cross(normal) ** 2)
            effmass = 1.0 / invmass
    
            # Impulso normal
            Jn = effmass * (1 + self.restitution) * vrel_normal
            Jvec = Jn * normal
            
            # Aplica impulso total
            A.apply_impulse(Jvec, pos=pos)
            B.apply_impulse(-Jvec, pos=pos)

    def __resolve_with_friction(self):
        '''Resolve colisões simples com atrito'''

        A, B = self
        normal = self.normal
        pos = self.pos
        vrel = B.vpoint(pos) - A.vpoint(pos)
        vrel_normal = vrel.dot(normal)
        friction = self.friction  
        restitution = self.restitution
        
        if vrel_normal < 0:
            # Escolhe o vetor tangente
            tangent = normal.perp()
            vrel_tangent = vrel.dot(tangent)
            if vrel_tangent < 0:
                vrel_tangent *= -1
                tangent *= -1
            
            # Parâmetros úteis
            rA = pos - A.pos
            rB = pos - B.pos
            rA_n, rA_t = rA.dot(normal), rA.dot(tangent)
            rB_n, rB_t = rB.dot(normal), rB.dot(tangent)

            # Massas efetivas inversas 
            invmassN = (A.invmass + A.invinertia * rA.cross(normal)**2 +  
                        B.invmass + B.invinertia * rB.cross(normal)**2)
            invmassT = (A.invmass + A.invinertia * rA.cross(tangent)**2 +  
                        B.invmass + B.invinertia * rB.cross(tangent)**2)
            invmassD = A.invinertia * rA_n * rA_t + B.invinertia * rB_n * rB_t  

            # Precisamos encontrar o valor do vetor J = Jn * n + Jt * t, onde
            # as componentes Jn e Jt são desconhecidas.
            # 
            # Existem alguns guias para realizar esta tarefa. O primeiro é a 
            # relação entre as velocidades relativas normais antes e depois
            # da colisão. Isto é dado pela expressão do coeficiente de 
            # restituição e resulta em
            #
            #     Jn / Mn - Jt / Md = (1 + e) * urel_n 
            #
            # Posteriormente, queremos aplicar a lei de Coulomb para o atrito,
            # que estabelece que a força de atrito máxima carrega a seguinte
            # relação com a normal 
            #
            #     |Ft| = mu * |Fn|,
            #
            # o que se traduz imediatamente em uma expressão para os impulsos:
            #
            #     |Jt| = mu * |Jn|,
            #
            # Sabemos que Jt > 0, pois o vetor de velocidade relativa está 
            # alinhado ao tangente. A força de atrito produz um impulso na
            # direção de t para o corpo A e na direção oposta para B. Já Jn < 0,
            # pois o impulso que o corpo A recebe deve ser necessariamente na
            # direção oposta à normal. A relação anterior fica portanto
            #
            #     Jt = -mu * Jn.
            #
            # Onde esperamos obter apenas o valor máximo do impulso devido ao 
            # atrito. Como então saber se o atrito satura ou se o valor máximo
            # deve ser utilizado? Usamos o critério de que o sinal da velocidade
            # relativa tangencial de saída deve permanecer positivo: ou seja,
            # o atrito é capaz de interromper o deslocamento tangencial, mas 
            # não de invertê-lo. 
            #
            # Assim, usa-se o critério:
            #
            #     vrel_tangent' >= 0,
            #
            # onde,
            #
            #     vrel_tangent' = vrel_tangent - Jn / Md + Jt / Mt
            #
            # Caso o critério acima seja violado, igualamos a velocidade 
            # tangencial a zero e usamos esta condição como condição suplementar
            # à da definição do coeficiente de restituição.
            #

            # Primeiramente assumimos o caso não saturado.
            Jn = (1 + restitution) * vrel_normal / (invmassN - friction * invmassD)
            Jt = -friction * Jn
            vrel_tangent_out = vrel_tangent + invmassD * Jn - invmassT * Jt
            
            # Verifica o sinal da velocidade de saída. Se for negativo, 
            # assume que o atrito saturou e que devemos usar o critério
            # de que a velocidade tangencial de saída deve ser nula.
            if vrel_tangent_out < 0:
                denom = invmassT * invmassN - invmassD**2  # <= 0
                Jn = ((1 + restitution) * vrel_normal * invmassT + 
                      invmassD * vrel_tangent) / denom
                Jt = ((1 + restitution) * vrel_normal * invmassD + 
                      invmassN * vrel_tangent) / denom

                # Roubo?
                if Jt < 0:
                    Jtmax = vrel_tangent / (invmassD / friction + invmassT)
                    Jn = (1 + restitution) * vrel_normal / invmassN
                    Jt = min(-friction * Jn, Jtmax)
        
            # Aplica impulso total
            Jvec = Jn * normal + Jt * tangent
            A.apply_impulse(Jvec, pos=pos)
            B.apply_impulse(-Jvec, pos=pos)


    def cancel(self):
        '''Cancela a colisão'''
        
        self.active = False

    def pre_collision(self):
        '''Dispara sinais antes de resolver a colisão''' 
    
        A, B = self
        A.trigger_pre_collision(self)
        B.trigger_pre_collision(self)
        #if self.active:
        #    if A.invmass:
        #        A.collisions.append(self)
        #    if B.invmass:
        #        B.collisions.append(self)
    
    def post_collision(self):
        '''Dispara sinais após resolver a colisão'''
        
        A, B = self
        A.trigger_post_collision(self)
        B.trigger_post_collision(self)
        #if A.invmass:
        #    A.collisions.remove(self)
        #if B.invmass:
        #    B.collisions.remove(self)

    def is_simple(self):
        '''Retorna True se o contato for o único contato de ambos os objetos
        envolvidos'''

        return (len(self.A._contacts) <= 1) and (len(self.B._contacts) <= 1)

    def remove_overlap(self, beta=1.0):
        '''Remove a superposição entre os objetos movendo cada objeto por uma
        fração inversamente proporcional às respectivas massas'''

        normal = self.normal
        A, B = self
        a = A._invmass
        b = B._invmass
        beta /= a + b
        A.move((-beta * a) * normal)
        B.move((beta * b) * normal)

    def baumgarte(self, beta, mindelta=0.3):
        '''Realiza o ajuste de baumgarte para remover gradualmente a 
        superposição entre dois objetos.'''
        
        delta = self.delta
        if delta > mindelta:
            A, B = self
            delta = 0.5 * delta
            Z = A.invmass + B.invmass
            delta_a = delta * A.invmass / Z
            delta_b = delta * B.invmass / Z
            if delta_a:
                A.move(-delta_a * self.normal)
            if delta_b:
                B.move(delta_b * self.normal)


class ContactOrdered(Collision):

    '''Um objeto de contato em que o primeiro objeto é sempre mais pesado que
    o segundo'''

    def __init__(self, A, B, world=None, pos=None, normal=None, **kwds):
        if A._invmass > B._invmass:
            B, A = A, B
        super(ContactOrdered, self).__init__(A, B, world, pos, normal, **kwds)


class Island(object):

    def __init__(self, collisions):
        self.collisions = collisions
        
    


if __name__ == '__main__':
    import doctest
    doctest.testmod()
