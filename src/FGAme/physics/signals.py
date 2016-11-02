from FGAme.signals import global_signal


pre_collision_signal = global_signal(
    'pre-collision', ['simulation'], ['col'],
    help_text='Triggered when a collision between two objects occurs. This'
              'signal is resolved before collision.'
)
post_collision_signal = global_signal(
    'post-collision', ['simulation'], ['col'],
    help_text='Like pre-collision, but it is triggered just *after* collision '
              'is resolved.'
)
object_added_signal = global_signal(
    'object-added', ['simulation', 'object'], [],
    help_text='Triggered when an object is added to the simulation.'
)
object_removed_signal = global_signal(
    'object-removed', ['simulation', 'object'], [],
    help_text='Triggered when an object is removed from simulation.'
)
gravity_changed_signal = global_signal(
    'gravity-changed', ['simulation'], ['old', 'new'],
    help_text='Triggered when the simulation gravity changes.'
)
damping_changed_signal = global_signal(
    'damping-changed', ['simulation'], ['old', 'new'],
    help_text='Triggered when the global damping changes.'
)
adamping_changed_signal = global_signal(
    'adamping-changed', ['simulation'], ['old', 'new'],
    help_text='Triggered when the global angular damping changes.'
)
friction_changed_signal = global_signal(
    'friction-changed', ['simulation'], ['old', 'new'],
    help_text='Triggered when friction coefficient changes.'
)
restitution_changed_signal = global_signal(
    'restitution-changed', ['simulation'], ['old', 'new'],
    help_text='Triggered when restitution coefficient changes.'
)
out_of_bounds_signal = global_signal(
    'out-of-bounds', ['simulation', 'object'], [],
    help_text='Triggered when an object leaves the simulation bounds.'
)
max_speed_signal = global_signal(
    'max-speed', ['simulation', 'object'], [],
    help_text='Trigerred when an object reaches the maximum simulation speed.'
)
sleep_signal = global_signal(
    'sleep', ['simulation', 'object'],
    help_text='Triggered when object starts sleeping.'
)
wake_up_signal = global_signal(
    'wake-up', ['simulation', 'object'],
    help_text='Triggered when object leaves sleeping state.'
)
import pgzero