'''
Implementa as interfaces da classe Body. Evita uma implementação monolítica
de uma classe enorme e favorece a reutilização e modularização do código.
'''

from FGAme.mathtools import Vec2, sqrt, null2D
from FGAme.util import popattr

INF = float('inf')



class HasAABB(object):

    '''
    Objetos que possuem uma AABB definida no atributo ``obj.aabb`` e uma
    posição definida no attributo ``obj.pos``.

    O centro da AABB não precisa coincidir com o valor de ``obj.pos``. Neste
    caso, as referências, pos_up, pos_down, pos_left e pos_right utilizam as
    coordenadas de ``obj.pos`` como referências do centro.
    '''

    __slots__ = []

    #
    # Scalar positions
    #    
    @property
    def xmin(self):
        return self.aabb.xmin

    @property
    def xmax(self):
        return self.aabb.xmax

    @property
    def ymin(self):
        return self.aabb.ymin

    @property
    def ymax(self):
        return self.aabb.ymax

    # Scalar setters
    xmin = xmin.setter(lambda obj, v: obj.move(v - obj.xmin, 0))
    xmax = xmax.setter(lambda obj, v: obj.move(v - obj.xmax, 0))
    ymin = ymin.setter(lambda obj, v: obj.move(0, v - obj.ymin))
    ymax = ymax.setter(lambda obj, v: obj.move(0, v - obj.ymax))

    #
    # Vector positions
    #
    @property
    def pos_sw(self):
        return Vec2(self.xmin, self.ymin)

    @property
    def pos_se(self):
        return Vec2(self.xmax, self.ymin)

    @property
    def pos_nw(self):
        return Vec2(self.xmin, self.ymax)

    @property
    def pos_ne(self):
        return Vec2(self.xmax, self.ymax)

    @property
    def pos_right(self):
        return Vec2(self.xmax, self.pos.y)

    @property
    def pos_left(self):
        return Vec2(self.xmin, self.pos.y)

    @property
    def pos_up(self):
        return Vec2(self.pos.x, self.ymax)

    @property
    def pos_down(self):
        return Vec2(self.pos.x, self.ymin)

    # Vector setters
    pos_sw = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_sw))
    pos_nw = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_nw))
    pos_se = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_se))
    pos_ne = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_ne))
    pos_up    = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_up))
    pos_down  = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_down))
    pos_right = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_right))
    pos_left  = pos_sw.setter(lambda obj, v: obj.move(v - obj.pos_left))
    
    #
    # Shape parameters
    #
    @property
    def bbox(self):
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def shape(self):
        return (self.xmax - self.xmin, self.ymax - self.ymin)

    @property
    def rect(self):
        x, y = self.xmin, self.ymin
        return (x, y, self.xmax - x, self.ymax - y)
    
    @property
    def width(self):
        return self.xmax - self.xmin

    @property
    def height(self):
        return self.ymax - self.ymin


class HasInertia(object):

    '''Define um objeto que possui propriedades de inércia linear (massa) e
    angular (momento de inércia).'''

    __slots__ = []

    @property
    def invmass(self):
        return self._invmass

    @property
    def invinertia(self):
        return self._invinertia

    @property
    def mass(self):
        try:
            return 1.0 / self._invmass
        except ZeroDivisionError:
            return float('inf')

    @mass.setter
    def mass(self, value):
        value = float(value)

        if value <= 0:
            raise ValueError('mass cannot be null or negative')
        elif value != INF:
            self._density = value / self.area()
            if self._invinertia:
                inertia = value * self.ROG_sqr()
                self._invinertia = 1.0 / inertia
            self._invmass = 1.0 / value
        else:
            self._invmass = 0.0
            self._invinertia = 0.0

    @property
    def inertia(self):
        try:
            return 1.0 / self._invinertia
        except ZeroDivisionError:
            return INF

    @inertia.setter
    def inertia(self, value):
        value = float(value)

        if self.can_rotate:
            if value <= 0:
                raise ValueError('inertia cannot be null or negative')
            elif value != INF:
                self._invinertia = 1.0 / value
            else:
                self._invinertia = 0.0
        else:
            self._raise_cannot_rotate_error()

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        rho = float(value)
        self._density = rho
        if self._invmass:
            self._invmass = 1.0 / (self.area() * rho)
        if self._invinertia:
            self._invinertia = 1.0 / (self.area() * rho * self.ROG_sqr())

    #
    # Propriedades Geométricas
    #
    def area(self):
        '''Área do objeto'''

        try:
            return self._baseshape.area()
        except AttributeError:
            return 0.0

    def ROG_sqr(self):
        '''Raio de giração ao quadrado.'''

        try:
            return self._baseshape.ROG_sqr()
        except AttributeError:
            return float('inf')

    def ROG(self):
        '''Raio de giração.

        Subclasses devem sobrescrever ROG_sqr, ao invés deste método.'''

        return sqrt(self.ROG_sqr())

    ###########################################################################
    #               Manipulação/consulta do estado dinâmico
    ###########################################################################
    # Simplificar e usar apenas a massa e a flag can_rotate como quesito de
    # teste.
    # FIXME: Alterar as flags nas funções make_*
    def is_dynamic(self, what=None):
        '''Retorna True se o objeto for dinâmico ou nas variáveis lineares ou
        nas angulares. Um objeto é considerado dinâmico nas variáveis lineares
        se possuir massa finita. De maneira análoga, o objeto torna-se dinâmico
        nas variáveis angulares se possuir momento de inércia finito.

        Opcionalmente pode especificar um parâmetro posicional 'linear',
        'angular', 'both' or 'any' (padrão) para determinar o tipo de consulta
        a ser realizada'''

        if what is None or what == 'any':
            return self.is_dynamic_linear() or self.is_dynamic_angular()
        elif what == 'both':
            return self.is_dynamic_linear() and self.is_dynamic_angular()
        elif what == 'linear':
            return self.is_dynamic_linear()
        elif what == 'angular':
            return self.is_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_dynamic_linear(self):
        '''Verifica se o objeto é dinâmico nas variáveis lineares'''

        return bool(self._invmass)

    def is_dynamic_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return bool(self._invinertia)

    def make_dynamic(self, what=None, restore_speed=True):
        '''Resgata a massa, inércia e velocidades anteriores de um objeto
        paralizado pelo método `obj.make_static()` ou `obj.make_kinematic()`.

        Aceita um argumento com a mesma semântica de is_dynamic()
        '''

        if what is None or what == 'both':
            self.make_dynamic_linear(restore_speed)
            self.make_dynamic_angular(restore_speed)
        elif what == 'linear':
            self.make_dynamic_linear(restore_speed)
        elif what == 'angular':
            self.make_dynamic_angular(restore_speed)
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_dynamic_linear(self, restore_speed=True):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_linear():
            self._invmass = 1.0 / (self.area() * self._density)

            # Resgata a velocidade
            if restore_speed and self._vel.is_null():
                self._vel = popattr(self, '_old_vel', null2D)

    def make_dynamic_angular(self, restore_speed=True):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_angular():
            self._inertia = 1.0 / (self._density * self.ROG_sqr())

            # Resgata a velocidade
            if restore_speed and self._omega == 0:
                self._omega = popattr(self, '_old_omega', 0.0)

    # Kinematic ###############################################################
    def is_kinematic(self, what=None):
        '''Retorna True se o objeto for cinemático ou nas variáveis lineares ou
        nas angulares. Um objeto é considerado cinemático (em uma das
        variáveis) se não for dinâmico. Se, além de cinemático, o objeto
        possuir velocidade nula, ele é considerado estático.

        Opcionalmente pode especificar um parâmetro posicional 'linear',
        'angular', 'both' (padrão) or 'any' para determinar o tipo de consulta
        a ser realizada.
        '''

        if what is None or what == 'both':
            return not (self.is_dynamic_linear() or self.is_dynamic_angular())
        elif what == 'any':
            return (
                not self.is_dynamic_linear()) or (
                not self.is_dynamic_angular())
        elif what == 'linear':
            return not self.is_dynamic_linear()
        elif what == 'angular':
            return not self.is_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_kinematic_linear(self):
        '''Verifica se o objeto é dinâmico nas variáveis lineares'''

        return not self.is_dynamic_linear()

    def is_kinematic_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return not self.is_dynamic_angular()

    def make_kinematic(self, what=None):
        '''Define a massa e/ou inércia como infinito.

        Aceita um argumento com a mesma semântica de is_kinematic()
        '''

        if what is None or what == 'both':
            self.make_kinematic_linear()
            self.make_kinematic_angular()
        elif what == 'linear':
            self.make_kinematic_linear()
        elif what == 'angular':
            self.make_kinematic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_kinematic_linear(self):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self._invmass = 0.0

    def make_kinematic_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self._invinertia = 0.0

    # Static ##################################################################
    def is_static(self, what=None):
        '''Retorna True se o objeto for estatático nas variáveis lineares e
        nas angulares. Um objeto é considerado estático (em uma das variáveis)
        se além de cinemático, a velocidade for nula.

        Opcionalmente pode especificar um parâmetro posicional 'linear',
        'angular', 'both' (padrão) or 'any' para determinar o tipo de consulta
        a ser realizada'''

        if what is None or what == 'both':
            return self.is_static_linear() and self.is_static_angular()
        elif what == 'any':
            return self.is_static_linear() or self.is_static_angular()
        elif what == 'linear':
            return self.is_static_linear()
        elif what == 'angular':
            return self.is_static_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_static_linear(self):
        '''Verifica se o objeto é dinâmico nas variáveis lineares'''

        return self.is_kinematic_linear() and self._vel == null2D

    def is_static_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return self.is_kinematic_angular() and self._omega == 0

    def make_static(self, what=None):
        '''Define a massa e/ou inércia como infinito.

        Aceita um argumento com a mesma semântica de is_static()
        '''

        if what is None or what == 'both':
            self.make_static_linear()
            self.make_static_angular()
        elif what == 'linear':
            self.make_static_linear()
        elif what == 'angular':
            self.make_static_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_static_linear(self):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self.make_kinematic_linear()
        self._old_vel = self._vel
        self._vel = null2D

    def make_static_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self.make_kinematic_angular()
        self._old_omega = self._omega
        self._omega = 0.0

    def _raise_cannot_rotate_error(self):
        raise ValueError('Cannot change angular variables with disabled '
                         '`can_rotate` flag')


class HasGlobalForces(object):

    '''
    Define um objeto que pode definir forças globais como gravidade e
    amortecimento.
    '''
    __slots__ = []

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        try:
            self._gravity = Vec2(*value)
        except TypeError:
            self._gravity = Vec2(0, -value)
        self.owns_gravity = True

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = float(value)
        self.owns_damping = True

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        self._adamping = float(value)
        self.owns_adamping = True

    @property
    def restitution(self):
        return self._restitution

    @restitution.setter
    def restitution(self, value):
        self._restitution = float(value)
        self.owns_restitution = True

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, value):
        self._friction = float(value)
        self.owns_friction = True
