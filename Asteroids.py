import arcade
import math
import random
from abc import abstractmethod
from abc import ABC

# These are Global constants to use throughout the game
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700

BULLET_RADIUS = 30
BULLET_SPEED = 10
BULLET_LIFE = 60

SHIP_TURN_AMOUNT = 3
SHIP_THRUST_AMOUNT = 0.25
SHIP_RADIUS = 30

INITIAL_ROCK_COUNT = 5

BIG_ROCK_SPIN = 1
BIG_ROCK_SPEED = 1.5
BIG_ROCK_RADIUS = 15

MEDIUM_ROCK_SPIN = -2
MEDIUM_ROCK_RADIUS = 5

SMALL_ROCK_SPIN = 5
SMALL_ROCK_RADIUS = 2


class Point:
    def __init__(self):
        self.x = 0
        self.y = 0


# Create Velocity Class for definin velocity of objects
class Velocity:
    def __init__(self):
        self.dx = 1
        self.dy = 1

    @property
    def dx(self):
        return self._dx

    @dx.setter
    def dx(self, dx):
        if dx > 50:
            self._dx = 50
        elif dx < -50:
            self._dx = -50
        else:
            self._dx = dx

    @property
    def dy(self):
        return self._dy

    @dy.setter
    def dy(self, dy):
        if dy > 50:
            self._dy = 50
        elif dy < -50:
            self._dy = -50
        else:
            self._dy = dy


# Create Parent class that is for all flying objects
class FlyingObject(ABC):
    def __init__(self):
        # Every Flying Object needs a center, velocity, radius and a boolean for if it's alive or not.
        self.center = Point()
        self.velocity = Velocity()
        self.radius = float(0.00)
        self.alive = False

    def advance(self):
        # Only advance the object if it's alive. To advance just add the velocity to the center
        if self.alive:
            self.center.x += self.velocity.dx
            self.center.y += self.velocity.dy
        # Make flying object wrap around the screen
        if self.center.x > SCREEN_WIDTH:
            self.center.x = 0
        elif self.center.x < 0:
            self.center.x = SCREEN_WIDTH

        if self.center.y > SCREEN_HEIGHT:
            self.center.y = 0
        elif self.center.y < 0:
            self.center.y = SCREEN_HEIGHT

    @abstractmethod  # Each flying object will have it's own draw function
    def draw(self):
        pass


class Ship(FlyingObject):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.center.x = SCREEN_WIDTH // 2  # start ship in center of screen
        self.center.y = SCREEN_HEIGHT // 2
        self.alive = True
        self.velocity.dx = 0
        self.velocity.dy = 0
        self.radius = SHIP_RADIUS

    def draw(self):
        if self.alive == True:
            texture = arcade.load_texture("ship.png")
            arcade.draw_texture_rectangle(
                self.center.x,
                self.center.y,
                texture.width,
                texture.height,
                texture,
                self.angle,
            )


class Laser(FlyingObject):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.length = BULLET_LIFE
        self.alive = False
        self.radius = BULLET_RADIUS

    def draw(self):
        if self.alive:
            texture = arcade.load_texture("laser.png")
            arcade.draw_texture_rectangle(
                self.center.x,
                self.center.y,
                texture.width,
                texture.height,
                texture,
                self.angle,
            )

    def fire(self, x, y, dx, dy, angle):
        self.center.x = x
        self.center.y = y
        self.angle = angle + 90
        self.velocity.dx = dx + SHIP_THRUST_AMOUNT * 40 * math.cos(
            math.radians(self.angle)
        )
        self.velocity.dy = dy + SHIP_THRUST_AMOUNT * 40 * math.sin(
            math.radians(self.angle)
        )
        self.alive = True


class Asteroid(FlyingObject, ABC):
    def __init__(self):
        super().__init__()
        self.center.x = 0
        self.center.y = random.randint(0, SCREEN_HEIGHT)

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def hit(self):
        pass


class BigAsteroid(Asteroid):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.center.x = x
        self.center.y = y
        self.velocity.dx = dx
        self.velocity.dy = dy
        self.alive = True
        self.angle = 90
        self.radius = BIG_ROCK_RADIUS

    def draw(self):
        if self.alive:
            texture = arcade.load_texture("big.png")
            arcade.draw_texture_rectangle(
                self.center.x,
                self.center.y,
                texture.width,
                texture.height,
                texture,
                self.angle,
            )

    def hit(self):
        self.alive = False

    def spin(self):
        self.angle += BIG_ROCK_SPIN


class MedAsteroid(Asteroid):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.center.x = x
        self.center.y = y
        self.velocity.dx = dx
        self.velocity.dy = dy
        self.alive = True
        self.angle = 90
        self.radius = MEDIUM_ROCK_RADIUS

    def draw(self):
        if self.alive:
            texture = arcade.load_texture("medium.png")
            arcade.draw_texture_rectangle(
                self.center.x,
                self.center.y,
                texture.width,
                texture.height,
                texture,
                self.angle,
            )

    def hit(self):
        self.alive = False

    def spin(self):
        self.angle += MEDIUM_ROCK_SPIN


class SmallAsteroid(Asteroid):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.center.x = x
        self.center.y = y
        self.velocity.dx = dx
        self.velocity.dy = dy
        self.alive = True
        self.angle = 90
        self.radius = SMALL_ROCK_RADIUS

    def draw(self):
        if self.alive:
            texture = arcade.load_texture("small.png")
            arcade.draw_texture_rectangle(
                self.center.x,
                self.center.y,
                texture.width,
                texture.height,
                texture,
                self.angle,
            )

    def hit(self):
        self.alive = False

    def spin(self):
        self.angle += SMALL_ROCK_SPIN


class Game(arcade.Window):
    """
    This class handles all the game callbacks and interaction
    This class will then call the appropriate functions of
    each of the above classes.
    You are welcome to modify anything in this class.
    """

    def __init__(self, width, height):
        """
        Sets up the initial conditions of the game
        :param width: Screen width
        :param height: Screen height
        """
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.SMOKY_BLACK)

        self.held_keys = set()

        # TODO: declare anything here you need the game class to track

        self.ship = Ship()
        self.lasers = []
        self.asteroids = []
        for i in list(range(1, 6)):
            angle = 360 * random.randint(0, 360)
            asteroid = BigAsteroid(
                random.randint(0, 1) * SCREEN_WIDTH,
                random.randint(0, SCREEN_HEIGHT),
                BIG_ROCK_SPEED * math.sin(angle),
                BIG_ROCK_SPEED * math.cos(angle),
            )
            self.asteroids.append(asteroid)

    def on_draw(self):
        """
        Called automatically by the arcade framework.
        Handles the responsibility of drawing all elements.
        """

        # clear the screen to begin drawing
        arcade.start_render()

        # TODO: draw each object
        self.ship.draw()

        for laser in self.lasers:
            laser.draw()

        for asteroid in self.asteroids:
            asteroid.draw()

    def update(self, delta_time):
        """
        Update each object in the game.
        :param delta_time: tells us how much time has actually elapsed
        """
        self.check_collisions()

        self.check_keys()

        # TODO: Tell everything to advance or move forward one step in time
        self.ship.advance()
        for laser in self.lasers:
            laser.advance()
            laser.length -= 1
            if laser.length < 1:
                laser.alive = False

        for asteroid in self.asteroids:
            asteroid.advance()
            asteroid.spin()

        # TODO: Check for collisions

    def check_keys(self):
        """
        This function checks for keys that are being held down.
        You will need to put your own method calls in here.
        """
        if arcade.key.LEFT in self.held_keys:
            self.ship.angle += SHIP_TURN_AMOUNT

        if arcade.key.RIGHT in self.held_keys:
            self.ship.angle -= SHIP_TURN_AMOUNT

        if arcade.key.UP in self.held_keys:
            self.ship.velocity.dx += SHIP_THRUST_AMOUNT * math.cos(
                math.radians(self.ship.angle + 90)
            )
            self.ship.velocity.dy += SHIP_THRUST_AMOUNT * math.sin(
                math.radians(self.ship.angle + 90)
            )

        if arcade.key.DOWN in self.held_keys:
            self.ship.velocity.dx -= SHIP_THRUST_AMOUNT * math.cos(
                math.radians(self.ship.angle + 90)
            )
            self.ship.velocity.dy -= SHIP_THRUST_AMOUNT * math.sin(
                math.radians(self.ship.angle + 90)
            )

        # Machine gun mode...
        if arcade.key.F in self.held_keys:
            laser = Laser()
            laser.fire(
                self.ship.center.x,
                self.ship.center.y,
                self.ship.velocity.dx,
                self.ship.velocity.dy,
                self.ship.angle,
            )
            self.lasers.append(laser)
            self.ship.velocity.dx -= (
                SHIP_THRUST_AMOUNT * 3 * math.cos(math.radians(self.ship.angle + 90))
            )
            self.ship.velocity.dy -= (
                SHIP_THRUST_AMOUNT * 3 * math.sin(math.radians(self.ship.angle + 90))
            )

    def on_key_press(self, key: int, modifiers: int):
        """
        Puts the current key in the set of keys that are being held.
        You will need to add things here to handle firing the bullet.
        """
        if self.ship.alive:
            self.held_keys.add(key)

            if key == arcade.key.SPACE:
                # TODO: Fire the bullet here!
                laser = Laser()
                laser.fire(
                    self.ship.center.x,
                    self.ship.center.y,
                    self.ship.velocity.dx,
                    self.ship.velocity.dy,
                    self.ship.angle,
                )
                self.lasers.append(laser)
                self.ship.velocity.dx -= (
                    SHIP_THRUST_AMOUNT
                    * 2
                    * math.cos(math.radians(self.ship.angle + 90))
                )
                self.ship.velocity.dy -= (
                    SHIP_THRUST_AMOUNT
                    * 2
                    * math.sin(math.radians(self.ship.angle + 90))
                )

            if key == arcade.key.G:
                # TODO: Fire the bullet here!
                for i in [
                    -25,
                    0,
                    25,
                ]:
                    laser = Laser()
                    laser.fire(
                        self.ship.center.x,
                        self.ship.center.y,
                        self.ship.velocity.dx,
                        self.ship.velocity.dy,
                        self.ship.angle + i,
                    )
                    self.lasers.append(laser)

                self.ship.velocity.dx -= (
                    SHIP_THRUST_AMOUNT
                    * 10
                    * math.cos(math.radians(self.ship.angle + 90))
                )
                self.ship.velocity.dy -= (
                    SHIP_THRUST_AMOUNT
                    * 10
                    * math.sin(math.radians(self.ship.angle + 90))
                )

        if key == arcade.key.R:
            self.ship = Ship()
            self.lasers = []
            self.asteroids = []
            for i in list(range(1, 6)):
                angle = 360 * random.randint(0, 360)
                asteroid = BigAsteroid(
                    random.randint(0, 1) * SCREEN_WIDTH,
                    random.randint(0, SCREEN_HEIGHT),
                    BIG_ROCK_SPEED * math.sin(angle),
                    BIG_ROCK_SPEED * math.cos(angle),
                )
                self.asteroids.append(asteroid)

    def on_key_release(self, key: int, modifiers: int):
        """
        Removes the current key from the set of held keys.
        """
        if key in self.held_keys:
            self.held_keys.remove(key)

    def check_collisions(self):
        for laser in self.lasers:
            for asteroid in self.asteroids:
                # Make sure they are both alive before checking for a collision
                if laser.alive and asteroid.alive:
                    too_close = laser.radius + asteroid.radius

                    if (
                        abs(laser.center.x - asteroid.center.x) < too_close
                        and abs(laser.center.y - asteroid.center.y) < too_close
                    ):
                        # its a hit!
                        laser.alive = False
                        asteroid.hit()
                        new_x = asteroid.center.x
                        new_y = asteroid.center.y
                        new_dx = asteroid.velocity.dx
                        new_dy = asteroid.velocity.dy

                        if asteroid.radius == BIG_ROCK_RADIUS:
                            asteroid = MedAsteroid(new_x, new_y, new_dx, new_dy + 2)
                            self.asteroids.append(asteroid)
                            asteroid = MedAsteroid(new_x, new_y, new_dx, new_dy - 2)
                            self.asteroids.append(asteroid)
                            asteroid = SmallAsteroid(new_x, new_y, new_dx + 5, new_dy)
                            self.asteroids.append(asteroid)
                        elif asteroid.radius == MEDIUM_ROCK_RADIUS:
                            asteroid = SmallAsteroid(
                                new_x, new_y, new_dx + 1.5, new_dy + 1.5
                            )
                            self.asteroids.append(asteroid)
                            asteroid = SmallAsteroid(
                                new_x, new_y, new_dx - 1.5, new_dy - 1.5
                            )
                            self.asteroids.append(asteroid)

                        # We will wait to remove the dead objects until after we
                        # finish going through the list

        for asteroid in self.asteroids:
            if asteroid.alive == True:
                too_close = self.ship.radius + asteroid.radius

                if (
                    abs(self.ship.center.x - asteroid.center.x) < too_close
                    and abs(self.ship.center.y - asteroid.center.y) < too_close
                ):
                    self.ship.alive = False

        # Now, check for anything that is dead, and remove it
        self.cleanup_zombies()

    def cleanup_zombies(self):
        """
        Removes any dead bullets or targets from the list.
        :return:
        """
        for laser in self.lasers:
            if not laser.alive:
                self.lasers.remove(laser)

        for asteroid in self.asteroids:
            if not asteroid.alive:
                self.asteroids.remove(asteroid)


# Creates the game and starts it going
window = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.run()
