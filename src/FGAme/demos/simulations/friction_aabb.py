from FGAme import World, AABB, pos

world = World(friction=0.1, restitution=0, gravity=500)
world.add_bounds(width=10)
world.add(
    AABB(
        pos=pos.middle - (300, +150),
        vel=(220, 70), 
        shape=(50, 50), 
        color='random',
    )
)

world.run()
