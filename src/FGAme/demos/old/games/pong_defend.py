from random import uniform, choice

from FGAme import *


class PongDefend(World):
    # Shapes
    screen_height = 600
    screen_width = 800
    pong_height = 150
    pong_width = 20
    ball_sides = 5
    ball_size = 30
    hit_size = 10
    inertia_multiplier = 20

    # Speeds
    ball_speed = 300
    max_ball_speed = 400
    max_speed = 500

    # Game logic
    max_hits = 12
    obstacle_N = 15
    obstacle_sides = 4
    obstacle_size = 30
    obstacle_color = (50, 50, 100)
    obstacle_dynamic = True

    # Cores
    hits_bg = Color(150, 150, 150)

    def init(self):
        self.restitution = 0.9
        self.add.margin(10, 10, -200, 10)

        # Creates pong paddle
        Y = self.pong_height
        X = self.pong_width
        W = self.screen_width
        H = self.screen_height
        self.pong = pong = self.add.poly(
            [(0, 0), (0, Y), (-X / 3, Y),
             (-X, 0.66 * Y), (-X, 0.33 * Y), (-X / 3, 0)],
            inertia='inf',
            restitution=0.5,
            damping=5.0,
        )
        self.pong_x = W - 20
        pong.move_to(pos.from_right(-20, 0))
        pong.mass *= 5
        pong.force = lambda t: -1000000 * Vec(pong.x - self.pong_x, 0)

        # Time bar
        self.timebar = self.add.aabb(shape=(20, 20), pos=(2 * W - 10, 20),
                                     color=(255, 225, 0))

        # Add objects
        self.ball = self.new_ball()
        self.obstacles = []
        for i in range(self.obstacle_N):
            new = self.new_obstacle()
            self.obstacles.append(new)

        # Define pong's amplitude
        self.max_pong_y = 2 * H - self.pong_height / 2 - 10
        self.min_pong_y = self.pong_height / 2 + 10

        # Draw gray hit points
        self.hits = 0
        self.hit_marks = []
        for i in range(self.max_hits):
            self.new_hit_mark(i, self.hits_bg)
        self.level = 0

        # Connect signals
        self.autoconnect()

    def new_ball(self):
        """
        Creates a new red ball
        """

        H, W = self.screen_height / 2, self.screen_width / 2
        ball = self.add.regular_poly(self.ball_sides, self.ball_size,
                                     color='red')
        ball.inertia *= self.inertia_multiplier
        ball.move((W, H))
        V = self.ball_speed
        speed = -V, choice([-1, 1]) * uniform(0.25 * V, 2 * V)
        ball.boost(speed)
        return ball

    def new_obstacle(self):
        """
        Creates random obstacle.
        """

        obj = self.add.regular_poly(
            self.obstacle_sides,
            self.obstacle_size,
            color=self.obstacle_color,
            pos=pos.random(20, 20, 50 + self.pong_width, 20),
            adamping=0.2,
        )
        obj.scale(uniform(0.75, 2))
        obj.rotate(uniform(0, 2 * math.pi))
        obj.inertia *= self.inertia_multiplier
        if not self.obstacle_dynamic:
            obj.make_static()
        return obj

    def new_hit_mark(self, n_hits, color='red'):
        """
        Make a new hit mark.
        """

        pos_x = 10 + (3 * n_hits + 2) * self.hit_size
        pos_y = self.screen_height - 2 * self.hit_size - 10
        hit = draw.Circle(radius=self.hit_size, pos=(pos_x, pos_y), color=color)
        self.add(hit, layer=1)
        return hit

    def frame_enter_event(self):
        """
        Executed at every frame.
        """

        if self.hits >= self.max_hits:
            self.game_over()

        # Accelerate ball
        V = self.ball.vel.norm()
        if V < self.max_ball_speed:
            V += 3
            self.ball.vel = self.ball.vel.normalize() * V

        # Limit velocity
        for obstacle in self.obstacles:
            if obstacle.speed > self.max_speed:
                obstacle.speed = self.max_speed

        # Checks if any object had escaped the game area
        if self.ball.pos.x > self.screen_width + 100:
            for _ in range(3):
                self.hit_increment()
            self.remove(self.ball)
            self.ball = self.new_ball()

        for i, obj in enumerate(self.obstacles):
            if obj.pos.x > self.screen_width + 100:
                self.hit_increment()
                self.remove(obj)
                del self.obstacles[i]
                break

        # Update the time bar and checks if level had expired.
        self.timebar.ymax = ymax = self.time * 20 - self.screen_height / 2 + 20
        if ymax > (self.screen_height / 2 - 10):
            self.next_level()

    @listen('long-press', 'up')
    def move_up(self):
        if self.pong.y < self.max_pong_y:
            self.pong.vel = (0, 600)

    @listen('long-press', 'down')
    def move_down(self):
        if self.pong.y > self.min_pong_y:
            self.pong.vel = (0, -600)

    @listen('key-down', 'left')
    def move_left(self):
        self.pong.boost((-500, 0))

    @listen('key-down', 'right')
    def move_right(self):
        self.pong.boost((300, 0))

    def hit_increment(self):
        """
        Increment hit count.
        """

        if self.hits <= self.max_hits:
            self.hit_marks.append(self.new_hit_mark(self.hits))
            self.hits += 1

    def game_over(self):
        """
        User had lost level!
        """

        raise SystemExit('game over')

    def next_level(self):
        """
        Start next level.
        """

        self.level += 1
        while len(self.hit_marks) <= self.level:
            mark = self.hit_marks.pop()
            self.remove(mark)


def game_over():
    """
    Executed when the game finishes.
    """

    from FGAme.extra.letters import add_word

    Sx, Sy = 5, 2
    world = World(background=(255, 0, 0), gravity=10)
    letters = add_word('game over', world, scale=5, pos=(180, 350))
    for l in letters:
        l.omega = uniform(-0.1, 0.1)
        l.vel += uniform(-Sx, Sx), uniform(-Sy, Sy)
        l.inertia *= 20
    world.run()


if __name__ == '__main__':
    PongDefend().run()
