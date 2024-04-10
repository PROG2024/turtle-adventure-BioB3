"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
from PIL import Image, ImageTk
import random, os, math
import tkinter as tk


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color
        self.__speed: int

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    @property
    def speed(self) -> int:
        """
        Get the speed of enemy
        """
        return self.__speed

    @speed.setter
    def speed(self, speed) -> None:
        """
        Set the speed of enemy
        """
        self.__speed = speed

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__x_state = self.state_move_right
        self.__y_state = self.state_move_down

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0,
                                       fill=self.color)
        self.speed = random.randint(1,5)

    def update(self) -> None:
        self.__x_state()
        self.__y_state()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x-self.size/2,
                           self.y-self.size/2,
                           self.x+self.size/2,
                           self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def state_move_right(self):
        self.x += self.speed
        if self.check_x_border():
            self.speed *= random.choice([1,1.1])
            self.__x_state = self.state_move_left

    def state_move_left(self):
        self.x -= self.speed
        if self.check_x_border():
            self.speed *= random.choice([1,1.1])
            self.__x_state = self.state_move_right

    def state_move_down(self):
        self.y += self.speed
        if self.check_y_border():
            self.speed *= random.choice([1,1.1])
            self.__y_state = self.state_move_up

    def state_move_up(self):
        self.y -= self.speed
        if self.check_y_border():
            self.speed *= random.choice([1,1.1])
            self.__y_state = self.state_move_down

    def check_x_border(self):
        if self.x < 0 or self.x > self.canvas.winfo_width():
            return True
        return False

    def check_y_border(self):
        if self.y < 0 or self.y > self.canvas.winfo_height():
            return True
        return False

class RandomWalkEnemy(Enemy):
    """
    Enemy that set random waypoint and move to it
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__destination = self.gen_dest()

    def gen_dest(self) -> None:
        """
        Generate a random destination
        """
        return (random.randint(0,self.canvas.winfo_width()),
                random.randint(0,self.canvas.winfo_height()))

    def update_x(self):
        if self.__destination[0] > self.x:
            self.x += min(self.speed, self.__destination[0] - self.x)
        else:
            self.x -= min(self.speed, self.x - self.__destination[0])

    def update_y(self):
        if self.__destination[1] > self.y:
            self.y += min(self.speed, self.__destination[1] - self.y)
        else:
            self.y -= min(self.speed, self.y - self.__destination[1])
    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0,
                                       fill=self.color)
        self.speed = random.randint(1,5)
        self.x = random.randint(0, self.canvas.winfo_width())
        self.y = random.randint(0, self.canvas.winfo_height())

    def update(self) -> None:
        if self.__destination[0] == self.x and self.__destination[1] == self.y:
            self.__destination = self.gen_dest()
        self.update_x()
        self.update_y()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x-self.size/2,
                           self.y-self.size/2,
                           self.x+self.size/2,
                           self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

class ChasingEnemy(Enemy):
    """
    Enemy that chase the player by setting the player's location as the waypoint
    """
    def __init__(self, 
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__player_loc = self.gen_player_loc()

    def gen_player_loc(self):
        """
        Get the player's location
        """
        return (self.game.player.x, self.game.player.y)

    def update_x(self):
        if self.__player_loc[0] > self.x:
            self.x += min(self.speed, self.__player_loc[0] - self.x)
        else:
            self.x -= min(self.speed, self.x - self.__player_loc[0])

    def update_y(self):
        if self.__player_loc[1] > self.y:
            self.y += min(self.speed, self.__player_loc[1] - self.y)
        else:
            self.y -= min(self.speed, self.y - self.__player_loc[1])

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0,
                                                 fill=self.color)
        self.speed = 2
        self.x = random.randint(self.canvas.winfo_width()/2, self.canvas.winfo_width())
        self.y = random.randint(0, self.canvas.winfo_height())

    def update(self) -> None:
        self.__player_loc = self.gen_player_loc()
        self.update_x()
        self.update_y()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x-self.size/2,
                           self.y-self.size/2,
                           self.x+self.size/2,
                           self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

class FencingEnemy(Enemy):
    """
    Enemy that guards the home by rotating around it
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__state = self.move_right_state

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0,
                                               fill=self.color)
        self.speed = random.randint(1,3)
        self.x = self.game.home.x + random.randint(18,22)
        self.y = self.game.home.y + random.randint(18,22)

    def move_right_state(self):
        if self.x < self.game.home.x + 20:
            self.x += self.speed
        else:
            self.__state = self.move_up_state

    def move_left_state(self):
        if self.x > self.game.home.x - 20:
            self.x -= self.speed
        else:
            self.__state = self.move_down_state

    def move_up_state(self):
        if self.y > self.game.home.y - 20:
            self.y -= self.speed
        else:
            self.__state = self.move_left_state

    def move_down_state(self):
        if self.y < self.game.home.y + 20:
            self.y += self.speed
        else:
            self.__state = self.move_right_state

    def update(self) -> None:
        self.__state()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x-self.size/2,
                           self.y-self.size/2,
                           self.x+self.size/2,
                           self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

class CrossEnemy(Enemy):
    """
    Enemy that travel in a cross shape from corner to corner
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__state = self.move_down_state
        self.x = 0
        self.y = 0
        self.__x_speed = 0
        self.__y_speed = 0

    def create(self) -> None:
        self.__imgtk = ImageTk.PhotoImage(Image.open(
            os.path.join(os.getcwd(), 'images','gauss-in-action-glyph.png')))
        self.__id = self.canvas.create_image(self.x,self.y, image=self.__imgtk, anchor=tk.CENTER)
        self.speed = random.randint(10,15)

    def move_down_state(self):
        if self.canvas.winfo_height()-self.y >= 10:
            delta_x = self.canvas.winfo_width() - self.x
            delta_y = self.canvas.winfo_height() - self.y
            hypotenuse = (delta_x**2 + delta_y**2)**0.5
            self.__x_speed = self.speed * (delta_x/hypotenuse)
            self.__y_speed = self.speed * (delta_y/hypotenuse)
            self.x += self.__x_speed
            self.y += self.__y_speed
        else:
            self.x = 0
            self.y = self.canvas.winfo_height()
            self.__state = self.move_up_state

    def move_up_state(self):
        if self.y >= 10:
            delta_x = self.canvas.winfo_width() - self.x
            delta_y = self.y
            hypotenuse = (delta_x**2 + delta_y**2)**0.5
            self.__x_speed = self.speed * (delta_x/hypotenuse)
            self.__y_speed = self.speed * (delta_y/hypotenuse)
            self.x += self.__x_speed
            self.y -= self.__y_speed
        else:
            self.x = 0
            self.y = 0
            self.__state = self.move_down_state

    def update(self) -> None:
        self.__state()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,self.x,self.y)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level
        self.__game.after(100, self.create_enemy)
        for _ in range(3):
            self.__game.after(10000, self.create_chasing, level/4)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create new enemies, possibly based on the game level
        """
        self.create_random()
        self.create_chasing()
        self.create_fencing()
        self.create_cross()

    def create_random(self) -> None:
        """
        Create RandomWalkEnemy based on the game level
        """
        for _ in range(2*self.game.level-1):
            new_enemy = RandomWalkEnemy(self.__game, 15, 'blue')
            self.game.add_element(new_enemy)

    def create_chasing(self, num=None) -> None:
        """
        Create ChasingEnemy based on the game level
        """
        if not num:
            num = self.__level
        for _ in range(math.ceil(num/3)):
            new_enemy = ChasingEnemy(self.__game, 20, 'red')
            self.game.add_element(new_enemy)

    def create_fencing(self) -> None:
        """
        Create FencingEnemy based on the game level
        """
        for _ in range(math.ceil(self.game.level/2)):
            new_enemy = FencingEnemy(self.__game, 10, 'green')
            self.game.add_element(new_enemy)

    def create_cross(self) -> None:
        """
        Create CrossEnemy based on the game level
        """
        for _ in range(3*self.game.level-2):
            new_enemy = CrossEnemy(self.__game, 25, 'black')
            self.game.add_element(new_enemy)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
