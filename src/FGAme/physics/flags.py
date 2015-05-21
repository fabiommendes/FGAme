# -*- coding: utf8 -*-
from itertools import count


class BodyFlags:
    N = count()

    # Estado dinâmico do objeto
    is_dynamic = 1 << next(N)
    is_kinematic = 1 << next(N)
    is_static = 1 << next(N)
    is_sleep = 1 << next(N)
    can_rotate = 1 << next(N)
    can_sleep = 1 << next(N)

    # Controle de forças
    owns_gravity = 1 << next(N)
    owns_damping = 1 << next(N)
    owns_adamping = 1 << next(N)

    # Contatos e vínculos
    has_joints = 1 << next(N)
    has_contacts = 1 << next(N)
    has_external_force = 1 << next(N)
    has_external_accel = 1 << next(N)
    has_external_torque = 1 << next(N)
    has_external_alpha = 1 << next(N)

    # Estados temporários
    is_dirty = 1 << next(N)

    # Controle do mundo
    has_world = 1 << next(N)
    has_visualization = 1 << next(N)

    num_bits = next(N)
    del N

    @classmethod
    def _gencode(cls):
        '''Imprime código com a definição de cada flag. Poderia fazer
        dinamicamente, mas o Eclipse não entende e aponta erros que não
        existem.
        '''

        flags = {k: v for (k, v) in vars(cls).items() if not k.startswith('_')}
        del flags['num_bits']
        flags = ['%s = %s' % (k.upper(), v) for (k, v) in flags.items()]
        print('\n'.join(sorted(flags)))

del count

###############################################################################
# Código copy & paste para do BodyFlags._gencode()
###############################################################################
CAN_ROTATE = 16
CAN_SLEEP = 32
HAS_CONTACTS = 1024
HAS_JOINTS = 512
HAS_VISUALIZATION = 8192
HAS_WORLD = 4096
IS_DIRTY = 2048
IS_DYNAMIC = 1
IS_KINEMATIC = 2
IS_SLEEP = 8
IS_STATIC = 4
OWNS_ADAMPING = 256
OWNS_DAMPING = 128
OWNS_GRAVITY = 64

###############################################################################
# Imprime o código quando chamado do __main__
###############################################################################
if __name__ == '__main__':
    BodyFlags._gencode()
