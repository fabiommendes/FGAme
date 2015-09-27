# -*- coding: utf8 -*-
from itertools import count


class _BodyFlagsBase:
    N = count()

    # Estado dinâmico do objeto
    active = 1 << next(N)
    is_dynamic = 1 << next(N)
    is_kinematic = 1 << next(N)
    is_static = 1 << next(N)
    is_sensor = 1 << next(N)
    is_sleeping = 1 << next(N)
    can_rotate = 1 << next(N)
    can_sleep = 1 << next(N)

    # Controle de forças
    owns_gravity = 1 << next(N)
    owns_damping = 1 << next(N)
    owns_adamping = 1 << next(N)
    owns_restitution = 1 << next(N)
    owns_friction = 1 << next(N)

    # Contatos e vínculos
    has_joints = 1 << next(N)
    has_contacts = 1 << next(N)
    has_external_force = 1 << next(N)
    has_external_accel = 1 << next(N)
    has_external_torque = 1 << next(N)
    has_external_alpha = 1 << next(N)

    # Estados temporários
    dirty_shape = 1 << next(N)
    dirty_aabb = 1 << next(N)

    # Controle do mundo
    has_visualization = 1 << next(N)
    has_simple_visualization = 1 << next(N)
    has_solid_color = 1 << next(N)
    has_line_color = 1 << next(N)

    num_bits = next(N)
    full = (1 << num_bits) - 1
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

    @classmethod
    def _make_negations(cls):
        '''Cria a negação de todas as flags'''

        cls.not_dirty_aabb = cls.full ^ cls.dirty_aabb


class BodyFlags(_BodyFlagsBase):
    f = _BodyFlagsBase

    # Negações das flags básicas ##############################################

    # Estado dinâmico do objeto
    not_active = f.full ^ f.active
    not_dynamic = f.full ^ f.is_dynamic
    not_kinematic = f.full ^ f.is_kinematic
    not_static = f.full ^ f.is_static
    not_sleep = f.full ^ f.is_sleeping
#     can_rotate = 1 << next(N)
#     can_sleep = 1 << next(N)
#
# Controle de forças
#     owns_gravity = 1 << next(N)
#     owns_damping = 1 << next(N)
#     owns_adamping = 1 << next(N)
#
# Contatos e vínculos
#     has_joints = 1 << next(N)
#     has_contacts = 1 << next(N)
#     has_external_force = 1 << next(N)
#     has_external_accel = 1 << next(N)
#     has_external_torque = 1 << next(N)
#     has_external_alpha = 1 << next(N)
#
# Estados temporários
    not_dirty_shape = f.full ^ f.dirty_shape
    not_dirty_aabb = f.full ^ f.dirty_aabb
#
# Controle do mundo
#     has_world = 1 << next(N)
#     has_visualization = 1 << next(N)

    # Flags compostas #########################################################
    dirty_any = f.dirty_aabb | f.dirty_shape
    not_dirty = f.full ^ dirty_any


del BodyFlags.f, count

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
    _BodyFlagsBase._gencode()
