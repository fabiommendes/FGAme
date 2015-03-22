#-*- coding: utf8 -*-

import six
from FGAme.mathutils import Vector

#==============================================================================
# Funções úteis
#==============================================================================
NOT_IMPLEMENTED = NotImplementedError('must be implemented at child classes')
INF = float('inf')
ORIGIN = Vector(0, 0)


def do_nothing(*args, **kwds):
    pass


def raises_method(ex=NOT_IMPLEMENTED):
    def method(self, *args, **kwds):
        raise ex
    return method

#==============================================================================
# Flags de propriedades físicas
#==============================================================================


class PhysBits:
    has_inertia = 2
    has_linear = 3
    has_angular = 4
    has_bbox = 6

    owns_gravity = 10
    owns_damping = 11
    owns_adamping = 12
    accel_static = 13

    has_world = 15
    has_visualization = 16

PHYS_HAS_MASS = 1 << 1
PHYS_HAS_INERTIA = 1 << 2
PHYS_HAS_SPEED = 1 << 3
PHYS_HAS_ASPEED = 1 << 4
PHYS_HAS_ROTATION = 1 << 5
PHYS_HAS_BBOX = 1 << 6
PHYS_OWNS_GRAVITY = 1 << 10
PHYS_OWNS_DAMPING = 1 << 11
PHYS_OWNS_ADAMPING = 1 << 12
PHYS_ACCEL_STATIC = 1 << 13
PHYS_HAS_WORLD = 1 << 15
PHYS_HAS_VISUALIZATION = 1 << 16

# Flags primárias -- metacódigo
# attrs = [(n, k) for (k, n) in PhysBits.__dict__.items()
#              if isinstance(n, int)]
# for n, k in sorted(attrs):
#     print('PHYS_%s = 1 << %i' % (k.upper(), n))

#==============================================================================
# Classes Base --- todos objetos físicos derivam delas
#==============================================================================


class PhysElementMeta(type):

    '''Metaclasse para todas as classes que representam objetos físicos'''

    BLACKLIST = ['_is_mixin_', '__module__', '__doc__', '__module__',
                 '__dict__', '__weakref__', '__slots__', '__subclasshook__']

    def __new__(cls, name, bases, ns):
        # Insere uma cláusula de __slots__ vazia
        ns.setdefault('__slots__', [])

        # Verifica se existem classes mix-in entre as bases
        true_bases = tuple(B for B in bases
                           if not getattr(B, '_is_mixin_', False))
        if len(bases) != len(true_bases):
            for i, B in enumerate(bases):
                if not getattr(B, '_is_mixin_', False):
                    continue

                # Encontra quais variáveis/métodos foram definidos nas classes
                # mixin
                allvars = {attr: getattr(B, attr) for attr in dir(B)}
                for var in cls.BLACKLIST:
                    if var in allvars:
                        del allvars[var]
                for attr, value in list(allvars.items()):
                    if hasattr(object, attr):
                        if getattr(object, attr) is value:
                            del allvars[attr]

                # Insere as variáveis que não foram definidas em ns nem em
                # nenhuma base anterior
                prev_bases = bases[:i]
                for attr in list(allvars.keys()):
                    if attr in ns:
                        del allvars[attr]
                        continue

                    for B in prev_bases:
                        if hasattr(B, attr):
                            del allvars[attr]
                            break

                ns.update(allvars)

                # Atualiza a lista de __slots__ utilizando o atributo _slots_
                # do mixin e toda hierarquia inferior
                for tt in B.mro():
                    slots = getattr(tt, '_slots_', [])
                    ns['__slots__'].extend(slots)

        # Atualiza a lista de propriedades e retira slots repetidos
        _properties_ = set(ns.get('_properties_', []))
        for base in bases:
            _properties_.update(getattr(base, '_properties_', []))
        ns['_properties_'] = _properties_
        ns['__slots__'] = list(set(ns['__slots__']))
        new = type.__new__(cls, name, true_bases, ns)

        # Atualiza as docstrings vazias utilizando as docstrings da primeira
        # base válida
        mro = new.mro()[1:-1]
        for name, method in ns.items():
            if not callable(method):
                continue

            doc = getattr(method, '__doc__', '<no docstring>')
            if not doc:
                for base in mro:
                    try:
                        other = getattr(base, name)
                    except AttributeError:
                        continue
                    if other.__doc__:
                        method.__doc__ = other.__doc__
                    break

        return new


@six.add_metaclass(PhysElementMeta)
class PhysElement(object):

    '''Classe mãe para os objetos que possuem física definida.

    Não possui propriedades, mas apenas define flags e (possivelmente) um
    dicionário extra de parâmetros. Por razões de performance e eficiência na
    alocação de memória, todas as sub-classes devem definir seus __slots__.

    É possível armazenar variáveis adicionais no dicionário privado do objeto
    utilizando o atributo _dict_. Para isso, a classe deve definir um conjunto
    de strings de atributos opcionais na variável _properties_. A
    metaclasse se encarrega de simular o comportamento de __slots__ no
    sentido que as sub-classes não precisam definir as _optinal_vars_ da
    classe mãe.

    Todas as variáveis dentro deste objeto possuem valores padrão de None.

    É possível criar parâmetros localmente utilizando o método
    'set_property()'. Estas propriedades são acessadas como atributos e podem
    ser listadas pelo método get_properties()

    Example
    -------

    Esta classe define apenas funcionalidades básicas, como acesso às flags de
    física e propriedades.

    Acesso a flags

    >>> elem = PhysElement()
    >>> elem.flag_has_mass
    False
    >>> elem.flag_has_mass = True
    >>> elem.flag_has_mass
    True

    Acesso a propriedades

    >>> elem.set_property('foo', 'bar')
    >>> elem.foo
    'bar'


    '''

    __slots__ = ['_phys_flags', '_dict_']
    _properties_ = set()

    def __init__(self, flags=0, dict_=None):
        self._phys_flags = flags
        self._dict_ = dict_

    def __getattr__(self, attr):
        # Captura slots não inicializados
        if hasattr(type(self), attr):
            raise AttributeError(attr)

        D = self._dict_
        if D is not None:
            try:
                return self._dict_[attr]
            except KeyError:
                pass

        if attr in self._properties_:
            return None
        else:
            raise AttributeError(attr)

# Mantêm a simetria com __getattr__, mas possivelmente incorre numa perda de
# performance. Do jeito que está, as propriedades são definidas como somente
# para leitura. É necessário definir propridedades explicitamente na classe
# para obter acesso de escrita.
#
# É fácil fazer alguma mágica na metaclasse para definir acesso rw, caso
# pareça interessante.
#
#     def __setattr__(self, attr, value):
#         try:
#             descriptor = self.__class__.__dict__[attr]
#         except KeyError:
#             if (attr in self._properties_ or
#                     (self._dict_ is not None and attr in self._dict_)):
#                 self._dict_[attr] = value
#         else:
#             descriptor.__set__(self, value)

    @property
    def _dict(self):
        if self._dict_ is None:
            self._dict_ = {}
        return self._dict_

    def set_property(self, name, value):
        '''Define uma propriedade do objeto'''

        if name.startswith('_'):
            raise ValueError('cannot change private properties'
                             ' (names starting with _)')

        self._dict[name] = value

    def get_property(self, name):
        '''Retorna uma propriedade do objeto'''

        if name.startswith('_'):
            raise ValueError('cannot access private properties'
                             ' (names starting with _)')

        try:
            return self._dict_[name]
        except (KeyError, TypeError):
            if name in self._properties_:
                return None
            else:
                raise ValueError('property')

    def get_properties(self):
        '''Retorna um dicionário com todas as propriedades definidas para o
        objeto em questão'''

        items = (self._dict_ or {}).items()
        return {k: v for (k, v) in items if not k.startswith('_')}

    def _getp(self, name, default):
        '''Versão mais rápida e privada de get_property(). Pode acessar
        qualquer propriedade adicional'''

        try:
            return self._dict_.get(name, default)
        except (TypeError, KeyError):
            return default

    def _setp(self, name, value):
        '''Versão mais rápida e privada de set_property(). Pode acessar
        qualquer propriedade adicional'''

        try:
            self._dict_[name] = value
        except TypeError:

            self._dict_ = {name: value}

    def _delp(self, name):
        '''Apaga uma propriedade do dicionário'''

        del self._dict_[name]
        if not self._dict_:
            self._dict_ = None

    def _clearp(self, *names):
        '''Limpa propriedades do dicionário, caso estejam definidas'''

        D = self._dict_
        if D is not None:
            for name in names:
                if name in D:
                    del D[name]

        if not D:
            self._dict_ = None

    #==========================================================================
    # Valores padrão
    #==========================================================================
    mass = float('inf')
    inertia = float('inf')
    pos = Vector(0, 0)
    vel = Vector(0, 0)
    theta = 0.0
    omega = 0.0

    area = 0
    ROG_sqr = 0
    ROG = 0

    #==========================================================================
    # Métodos com implementações inócuas
    #==========================================================================
    move = do_nothing()
    boost = do_nothing()
    rotate = do_nothing()
    aboost = do_nothing()

    #==========================================================================
    # Controle de flags
    #==========================================================================
# Propriedades de controle de flags -- metacódigo
#
# Descomente e rode este código caso queira recalcular as propriedades
# associadas à cada flag de física.
#
#     template = '''
#     @property
#     def flag_flagname(self):
#         return bool(self._phys_flags & PHYS_FLAGNAME)
#
#     @flag_flagname.setter
#     def flag_flagname(self, value):
#         if value:
#             self._phys_flags |= PHYS_FLAGNAME
#         else:
#             self._phys_flags &= ~PHYS_FLAGNAME'''
#
#     attrs = [(n, k) for (k, n) in PhysBits.__dict__.items()
#                  if isinstance(n, int)]
#     for n, k in sorted(attrs):
#         func_def = template.replace('flagname', k)
#         func_def = func_def.replace('FLAGNAME', k.upper())
#         print(func_def)

    # Definições geradas pelo código acima
    @property
    def flag_has_mass(self):
        return bool(self._phys_flags & PHYS_HAS_MASS)

    @flag_has_mass.setter
    def flag_has_mass(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_MASS
        else:
            self._phys_flags &= ~PHYS_HAS_MASS

    @property
    def flag_has_inertia(self):
        return bool(self._phys_flags & PHYS_HAS_INERTIA)

    @flag_has_inertia.setter
    def flag_has_inertia(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_INERTIA
        else:
            self._phys_flags &= ~PHYS_HAS_INERTIA

    @property
    def flag_has_speed(self):
        return bool(self._phys_flags & PHYS_HAS_SPEED)

    @flag_has_speed.setter
    def flag_has_speed(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_SPEED
        else:
            self._phys_flags &= ~PHYS_HAS_SPEED

    @property
    def flag_has_aspeed(self):
        return bool(self._phys_flags & PHYS_HAS_ASPEED)

    @flag_has_aspeed.setter
    def flag_has_aspeed(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_ASPEED
        else:
            self._phys_flags &= ~PHYS_HAS_ASPEED

    @property
    def flag_has_rotation(self):
        return bool(self._phys_flags & PHYS_HAS_ROTATION)

    @flag_has_rotation.setter
    def flag_has_rotation(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_ROTATION
        else:
            self._phys_flags &= ~PHYS_HAS_ROTATION

    @property
    def flag_has_bbox(self):
        return bool(self._phys_flags & PHYS_HAS_BBOX)

    @flag_has_bbox.setter
    def flag_has_bbox(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_BBOX
        else:
            self._phys_flags &= ~PHYS_HAS_BBOX

    @property
    def flag_owns_gravity(self):
        return bool(self._phys_flags & PHYS_OWNS_GRAVITY)

    @flag_owns_gravity.setter
    def flag_owns_gravity(self, value):
        if value:
            self._phys_flags |= PHYS_OWNS_GRAVITY
        else:
            self._phys_flags &= ~PHYS_OWNS_GRAVITY

    @property
    def flag_owns_damping(self):
        return bool(self._phys_flags & PHYS_OWNS_DAMPING)

    @flag_owns_damping.setter
    def flag_owns_damping(self, value):
        if value:
            self._phys_flags |= PHYS_OWNS_DAMPING
        else:
            self._phys_flags &= ~PHYS_OWNS_DAMPING

    @property
    def flag_owns_adamping(self):
        return bool(self._phys_flags & PHYS_OWNS_ADAMPING)

    @flag_owns_adamping.setter
    def flag_owns_adamping(self, value):
        if value:
            self._phys_flags |= PHYS_OWNS_ADAMPING
        else:
            self._phys_flags &= ~PHYS_OWNS_ADAMPING

    @property
    def flag_accel_static(self):
        return bool(self._phys_flags & PHYS_ACCEL_STATIC)

    @flag_accel_static.setter
    def flag_accel_static(self, value):
        if value:
            self._phys_flags |= PHYS_ACCEL_STATIC
        else:
            self._phys_flags &= ~PHYS_ACCEL_STATIC

    @property
    def flag_has_world(self):
        return bool(self._phys_flags & PHYS_HAS_WORLD)

    @flag_has_world.setter
    def flag_has_world(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_WORLD
        else:
            self._phys_flags &= ~PHYS_HAS_WORLD

    @property
    def flag_has_visualization(self):
        return bool(self._phys_flags & PHYS_HAS_VISUALIZATION)

    @flag_has_visualization.setter
    def flag_has_visualization(self, value):
        if value:
            self._phys_flags |= PHYS_HAS_VISUALIZATION
        else:
            self._phys_flags &= ~PHYS_HAS_VISUALIZATION

    #==========================================================================
    # is_dynamic*() queries
    #==========================================================================

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

        return self.mass == INF

    def is_dynamic_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return self.inertia == INF

    def make_dynamic(self, what=None):
        '''Resgata a massa, inércia e velocidades anteriores de um objeto
        paralizado pelo método `obj.make_static()` ou `obj.make_kinematic()`.

        Aceita um argumento com a mesma semântica de is_dynamic()
        '''

        if what is None or what == 'both':
            self.make_dynamic_linear()
            self.make_dynamic_angular()
        elif what == 'linear':
            self.make_dynamic_linear()
        elif what == 'angular':
            self.make_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_dynamic_linear(self):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_linear():
            # Regata a massa
            mass = self._getp('old_mass', None)
            if mass is None:
                raise RuntimeError('old mass is not available for recovery')
            else:
                self.mass = mass

            # Resgata a velocidade
            if self.vel == ORIGIN:
                self.vel = self._getp('old_vel', ORIGIN)

        self._clearp('old_mass', 'old_vel')

    def make_dynamic_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_angular():
            # Regata a massa
            inertia = self._getp('old_inertia', None)
            if inertia is None:
                raise RuntimeError('old inertia is not available for recovery')
            else:
                self.inertia = inertia

            # Resgata a velocidade
            if self.omega == 0:
                self.omega = self._getp('old_omega', 0)

        self._clearp('old_inertia', 'old_omega')

    #==========================================================================
    # Kinematic
    #==========================================================================

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

        if not self.is_kinematic_linear():
            self._setp('old_mass', self.mass)
            self.mass = 'inf'

    def make_kinematic_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_kinematic_angular():
            self._setp('old_inertia', self.inertia)
            self.inertia = 'inf'

    #==========================================================================
    # Static
    #==========================================================================

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

        return self.is_kinematic_linear() and self.vel == ORIGIN

    def is_static_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return self.is_kinematic_angular() and self.omega == 0

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
        if self.vel != ORIGIN:
            self._setp('old_vel', self.vel)
            self.vel = (0, 0)

    def make_static_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self.make_kinematic_angular()
        if self.omega != 0:
            self._setp('old_omega', self.omega)
            self.omega = 0.0


if __name__ == '__main__':
    import doctest
    doctest.testmod()
