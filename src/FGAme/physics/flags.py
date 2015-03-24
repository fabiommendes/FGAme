class _FlagBits:
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

# Cria as flags programaticamente
# for k, v in vars(_FlagBits).items():
#     if isinstance(v, int):
#         globals()[k.upper()] = 1 << v
#         print(k.upper(), '=', 1 << v)
# del k, v

HAS_VISUALIZATION = 65536
OWNS_GRAVITY = 1024
HAS_LINEAR = 8
HAS_INERTIA = 4
ACCEL_STATIC = 8192
HAS_BBOX = 64
OWNS_ADAMPING = 4096
HAS_WORLD = 32768
HAS_ANGULAR = 16
OWNS_DAMPING = 2048
